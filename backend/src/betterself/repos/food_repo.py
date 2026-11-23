import uuid
from datetime import datetime

from sqlalchemy import Select, and_, case, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from betterself.core.exceptions import RecordNotFound
from betterself.core.text_search import folded_column
from betterself.models.consumption_models import FoodConsumption
from betterself.models.food_models import Food, FoodSource
from betterself.repos.off_catalog_repo import CatalogProduct
from betterself.schemas.food_schemas import FoodCreate, FoodUpdate
from betterself.models.user_models import User

"""
Gère le catalogue d'aliments et de produits alimentaires.

Les aliments peuvent être créés manuellement par un utilisateur ou
importés depuis une source externe. Les valeurs nutritionnelles sont
toujours exprimées pour la quantité de référence de l'aliment.
"""
class FoodRepository:
    def __init__(self, db: Session):
        self.db = db


    """
    Recherche des aliments selon un terme libre, une catégorie, ou les
    deux. La recherche porte sur le nom, la marque et la référence externe.
    """
    def search_foods(
        self,
        *,
        query: str | None = None,
        category: str | None = None,
        limit: int = 20,
        offset: int = 0, # Offset pour la pagination des résultats.
    ) -> list[Food]:
        statement = select(Food).order_by(Food.name.asc())

        # Si un terme de recherche est spécifié, on filtre les aliments par ce terme.
        if query:
            search_term = f"%{query.strip().lower()}%"

            statement = statement.where(
                or_(
                    Food.name.ilike(search_term),
                    Food.brand.ilike(search_term),
                    Food.external_reference_id.ilike(search_term),
                )
            )

        # Si une catégorie est spécifiée, on filtre les aliments par cette catégorie.
        if category:
            statement = statement.where(
                Food.category == category,
            )

        statement = statement.limit(limit).offset(offset)
        return list(self.db.scalars(statement))


    """
    Sélectionne les aliments avec la date de leur dernière utilisation par l'utilisateur.
    Un aliment qu'il a créé, mais pas encore consigné, compte à partir de sa création.
    La date est nulle si l'aliment ne fait pas partie de son historique.
    """
    def _select_with_last_use(self, user: User) -> Select[tuple[Food, datetime | None]]:
        consumptions = (
            select(
                FoodConsumption.food_id,
                func.max(FoodConsumption.consumed_at).label("consumed_at"),
            )
            .where(FoodConsumption.user_id == user.id)
            .group_by(FoodConsumption.food_id)
            .subquery()
        )
        last_use = func.coalesce(
            consumptions.c.consumed_at,
            case((Food.created_by_user_id == user.id, Food.created_at)),
        ).label("last_use")

        return select(Food, last_use).outerjoin(
            consumptions, consumptions.c.food_id == Food.id
        )


    # Retourne l'historique de l'utilisateur, du plus récent au plus ancien.
    def list_history(self, user: User, limit: int = 20) -> list[Food]:
        statement = self._select_with_last_use(user)
        last_use = statement.selected_columns.last_use
        statement = statement.where(last_use.is_not(None)).order_by(last_use.desc(), Food.name)
        return list(self.db.scalars(statement.limit(limit)))


    """
    Recherche des aliments dont le nom ou la marque contient tous les mots (déjà
    normalisés), ou qui portent l'un des codes fournis. Chaque aliment est accompagné
    de la date de sa dernière utilisation.
    """
    def search_with_history(
        self,
        user: User,
        *,
        words: list[str],
        barcodes: list[str],
        catalog_codes: list[str],
        limit: int = 200,
    ) -> list[tuple[Food, datetime | None]]:
        statement = self._select_with_last_use(user)
        last_use = statement.selected_columns.last_use
        text = folded_column(Food.name) + " " + folded_column(Food.brand)

        statement = statement.where(
            or_(
                # Les mots ne contiennent que des lettres et des chiffres : aucun
                # caractère spécial de LIKE à échapper.
                and_(*(text.like(f"%{word}%") for word in words)),
                Food.external_reference_id.in_(barcodes),
                and_(
                    Food.source == FoodSource.OPEN_FOOD_FACTS,
                    Food.external_reference_id.in_(catalog_codes),
                ),
            )
        ).order_by(last_use.desc().nulls_last(), func.length(Food.name))

        return [(food, used) for food, used in self.db.execute(statement.limit(limit))]


    """
    Crée un aliment manuel associé à l'utilisateur connecté.
    La validation de cohérence entre calories et macronutriments est effectuée par le schéma Pydantic `FoodCreate`.
    """
    def create_food(
        self,
        user: User,
        data: FoodCreate,
    ) -> Food:
        food = Food(
            name=data.name.strip(),
            brand=data.brand.strip() if data.brand else None,
            description=data.description,
            category=data.category,
            reference_weight_g=data.reference_weight_g,
            calories_kcal=data.calories_kcal,
            protein_g=data.protein_g,
            carbohydrates_g=data.carbohydrates_g,
            fat_g=data.fat_g,
            source=FoodSource.MANUAL,
            external_reference_id=data.external_reference_id,
            created_by_user_id=user.id,
        )
        self.db.add(food)
        self.db.flush()
        return food
    

    # Retourne l'aliment importé d'Open Food Facts portant ce code-barres.
    def get_by_external_reference(self, code: str) -> Food | None:
        return self.db.scalar(
            select(Food).where(
                Food.source == FoodSource.OPEN_FOOD_FACTS,
                Food.external_reference_id == code,
            )
        )


    """
    Copie un produit du catalogue Open Food Facts dans les aliments, s'il n'y est pas déjà.
    Retourne l'aliment et indique s'il vient d'être créé.
    """
    def get_or_import_product(self, product: CatalogProduct) -> tuple[Food, bool]:
        existing = self.get_by_external_reference(product.code)
        if existing is not None:
            return existing, False

        food = Food(
            name=product.name,
            brand=product.brand,
            reference_weight_g=product.reference_weight_g,
            serving_g=product.serving_g,
            calories_kcal=product.calories_kcal,
            protein_g=product.protein_g,
            carbohydrates_g=product.carbohydrates_g,
            fat_g=product.fat_g,
            source=FoodSource.OPEN_FOOD_FACTS,
            external_reference_id=product.code,
        )

        try:
            # Le SAVEPOINT limite l'annulation à cette insertion.
            with self.db.begin_nested():
                self.db.add(food)
        except IntegrityError:
            # Une autre requête vient peut-être d'importer le même produit.
            existing = self.get_by_external_reference(product.code)
            if existing is None:
                raise
            return existing, False

        return food, True


    """
    Met à jour un aliment manuel créé par l'utilisateur connecté.
    Un aliment provenant d'une source externe ne devrait pas être modifié directement par un utilisateur.
    """
    def update_food(
        self,
        user: User,
        food_id: uuid.UUID,
        data: FoodUpdate,
    ) -> Food:
        ALLOWED_UPDATE_FIELDS = {"name", "brand", "description"}

        food = self.get_food_or_404(
            food_id=food_id,
        )

        if food.source is not FoodSource.MANUAL:
            raise PermissionError(
                "Seuls les aliments créés manuellement peuvent être modifiés."
            )

        if food.created_by_user_id != user.id:
            raise PermissionError(
                "Vous n'êtes pas autorisé à modifier cet aliment."
            )
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
                if field in ALLOWED_UPDATE_FIELDS:
                    setattr(food, field, value)

        self.db.flush()
        return food

    """
    Supprime un aliment manuel créé par l'utilisateur connecté.
    Une suppression logique pourra être préférable plus tard si des entrées de journal alimentaire référencent déjà cet aliment.
    """
    def delete_food(
        self,
        user: User,
        food_id: uuid.UUID,
    ) -> None:
        food = self.get_food_or_404(
            food_id=food_id,
        )

        if food.source is not FoodSource.MANUAL:
            raise PermissionError(
                "Seuls les aliments créés manuellement peuvent être supprimés."
            )

        if food.created_by_user_id != user.id:
            raise PermissionError(
                "Vous n'êtes pas autorisé à supprimer cet aliment."
            )
        self.db.delete(food)
        self.db.flush()


    """
    Retourne un aliment à partir de son identifiant ou lève une
    exception s'il n'existe pas.
    """
    def get_food_or_404(self, food_id: uuid.UUID) -> Food:
        food = self.db.get(Food, food_id)

        if food is None:
            raise RecordNotFound("Aucun aliment n'a été trouvé.")

        return food