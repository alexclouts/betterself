import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from betterself.core.exceptions import RecordNotFound
from betterself.foods.models import Food, FoodSource
from betterself.foods.schemas import FoodCreate, FoodUpdate
from betterself.users.models import User


class FoodService:
    """
    Gère le catalogue d'aliments et de produits alimentaires.

    Les aliments peuvent être créés manuellement par un utilisateur ou
    importés depuis une source externe. Les valeurs nutritionnelles sont
    toujours exprimées pour la quantité de référence de l'aliment.
    """

    def __init__(self, db: Session):
        self.db = db


    # Fonction pour récupérer un aliment par son identifiant
    def get_food_or_404(self, food_id: uuid.UUID) -> Food:
        """
        Retourne un aliment à partir de son identifiant ou lève une
        exception s'il n'existe pas.
        """
        food = self.db.get(Food, food_id)

        if food is None:
            raise RecordNotFound("Aucun aliment n'a été trouvé.")

        return food


    # Fonction pour rechercher des aliments par nom, marque ou référence externe
    def search_foods(
        self,
        *,
        query: str | None = None,
        category: str | None = None,
        limit: int = 20,
        offset: int = 0, # Offset pour la pagination des résultats.
    ) -> list[Food]:
        """
        Recherche des aliments selon un terme libre, une catégorie, ou les
        deux. La recherche porte sur le nom, la marque et la référence
        externe.
        """
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


    # Fonction pour créer un aliment manuellement
    def create_food(
        self,
        user: User,
        data: FoodCreate,
    ) -> Food:
        """
        Crée un aliment manuel associé à l'utilisateur connecté.

        La validation de cohérence entre calories et macronutriments est
        effectuée par le schéma Pydantic `FoodCreate`.
        """
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
        self.db.commit()
        self.db.refresh(food)

        return food


    # Fonction pour mettre à jour un aliment créé par l'utilisateur
    def update_food(
        self,
        user: User,
        food_id: uuid.UUID,
        data: FoodUpdate,
    ) -> Food:
        """
        Met à jour un aliment manuel créé par l'utilisateur connecté.

        Un aliment provenant d'une source externe ne devrait pas être
        modifié directement par un utilisateur.
        """
        ALLOWED_UPDATE_FIELDS = {"name", "brand", "description"}

        food = self.get_food_or_404(food_id)

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

        self.db.commit()
        self.db.refresh(food)

        return food

    # Fonction pour supprimer un aliment créé par l'utilisateur
    def delete_food(
        self,
        user: User,
        food_id: uuid.UUID,
    ) -> None:
        """
        Supprime un aliment manuel créé par l'utilisateur connecté.

        Une suppression logique pourra être préférable plus tard si des
        entrées de journal alimentaire référencent déjà cet aliment.
        """
        food = self.get_food_or_404(food_id)

        if food.source is not FoodSource.MANUAL:
            raise PermissionError(
                "Seuls les aliments créés manuellement peuvent être supprimés."
            )

        if food.created_by_user_id != user.id:
            raise PermissionError(
                "Vous n'êtes pas autorisé à supprimer cet aliment."
            )

        self.db.delete(food)
        self.db.commit()