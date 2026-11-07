import uuid
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from betterself.core.exceptions import RecordNotFound
from betterself.consumptions.models import FoodConsumption
from betterself.foods.models import Food
from betterself.recipes.models import Recipe
from betterself.users.models import User
from betterself.foods.queries import get_food_or_404
from betterself.recipes.queries import get_recipe_or_404

from betterself.consumptions.schemas import (
    DailyNutritionSummaryRead,
    FoodConsumptionCreate,
    FoodConsumptionUpdate,
)

"""
Service responsable des entrées du journal alimentaire.

Les valeurs nutritionnelles sont calculées à partir de `quantity_g`,
puis conservées comme instantané.
"""
class FoodConsumptionService:

    def __init__(self, db: Session):
        self.db = db


    def _get_consumption_or_404(
        self,
        user: User,
        consumption_id: uuid.UUID,
    ) -> FoodConsumption:
        consumption = self.db.scalar(
            select(FoodConsumption).where(
                FoodConsumption.id == consumption_id,
                FoodConsumption.user_id == user.id,
            )
        )
        if consumption is None:
            raise RecordNotFound(
                "Aucune consommation n'a été trouvée."
            )
        return consumption


    """
    Calcule les valeurs nutritionnelles pour une quantité donnée
    d'un aliment, à partir de sa valeur de référence.
    """
    def _calculate_food_nutrition(
        self,
        food: Food,
        quantity_g: Decimal,
    ) -> dict[str, Decimal]:
        reference_weight = Decimal(food.reference_weight_g)

        if reference_weight <= 0:
            raise ValueError(
                "Le poids de référence de l'aliment doit être supérieur à zéro."
            )
        ratio = quantity_g / reference_weight

        return {
            "calories_kcal": Decimal(food.calories_kcal) * ratio,
            "protein_g": Decimal(food.protein_g) * ratio,
            "fat_g": Decimal(food.fat_g) * ratio,
            "carbohydrates_g": Decimal(food.carbohydrates_g) * ratio,
        }


    """
    Calcule les valeurs nutritionnelles d'une portion de recette.
    La recette entière correspond à `recipe.total_weight_g`.
    """
    def _calculate_recipe_nutrition(
        self,
        recipe: Recipe,
        quantity_g: Decimal,
    ) -> dict[str, Decimal]:

        total_weight = Decimal(recipe.total_weight_g)

        if total_weight <= 0:
            raise ValueError(
                "Le poids total de la recette doit être supérieur à zéro."
            )

        totals = {
            "calories_kcal": Decimal("0"),
            "protein_g": Decimal("0"),
            "fat_g": Decimal("0"),
            "carbohydrates_g": Decimal("0"),
        }

        for ingredient in recipe.ingredients:
            food = ingredient.food

            ingredient_ratio = (
                Decimal(ingredient.quantity_g)
                / Decimal(food.reference_weight_g)
            )

            totals["calories_kcal"] += (
                Decimal(food.calories_kcal) * ingredient_ratio
            )
            totals["protein_g"] += (
                Decimal(food.protein_g) * ingredient_ratio
            )
            totals["fat_g"] += (
                Decimal(food.fat_g) * ingredient_ratio
            )
            totals["carbohydrates_g"] += (
                Decimal(food.carbohydrates_g) * ingredient_ratio
            )

        recipe_ratio = quantity_g / total_weight

        return {
            field: value * recipe_ratio
            for field, value in totals.items()
        }


    """
    Prépare une consommation et calcule son instantané (snapshot) nutritionnel.
    """
    def _build_snapshot(
        self,
        user: User,
        data: FoodConsumptionCreate,
    ) -> tuple[FoodConsumption, dict[str, Decimal]]:
        
        # Si l'ID de l'aliment est fourni, on calcule la nutrition à partir de l'aliment.
        if data.food_id is not None:
            food = get_food_or_404(
                self,
                food_id=data.food_id,
            )

            nutrition = self._calculate_food_nutrition(
                food=food,
                quantity_g=data.quantity_g,
            )

            consumption = FoodConsumption(
                user_id=user.id,
                food_id=food.id,
                recipe_id=None,
                item_name_snapshot=food.name,
                quantity_g=data.quantity_g,
                meal_type=data.meal_type.value,
                consumed_at=data.consumed_at or datetime.now(timezone.utc),
                notes=data.notes,
                **nutrition,
            )
            return consumption, nutrition
        
        # Si l'ID de la recette est fourni, on calcule la nutrition à partir de la recette.
        recipe = get_recipe_or_404(
            self,
            user=user,
            recipe_id=data.recipe_id,
        )

        nutrition = self._calculate_recipe_nutrition(
            recipe=recipe,
            quantity_g=data.quantity_g,
        )

        consumption = FoodConsumption(
            user_id=user.id,
            food_id=None,
            recipe_id=recipe.id,
            item_name_snapshot=recipe.name,
            quantity_g=data.quantity_g,
            meal_type=data.meal_type.value,
            consumed_at=data.consumed_at or datetime.now(timezone.utc),
            notes=data.notes,
            **nutrition,
        )
        # Retourne la consommation et son instantané nutritionnel.
        return consumption, nutrition


    """
    Ajoute une consommation au journal.
    La source doit être soit un aliment, soit une recette.
    """
    def create_consumption(
        self,
        user: User,
        data: FoodConsumptionCreate,
    ) -> FoodConsumption:
        consumption, _ = self._build_snapshot(
            user=user,
            data=data,
        )

        self.db.add(consumption)
        self.db.commit()
        self.db.refresh(consumption)

        return consumption
    

    """
    Retourne les consommations de l'utilisateur, avec filtres facultatifs.
    """
    def list_consumptions(
        self,
        user: User,
        *,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        meal_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[FoodConsumption]:
        # Construire la requête de base pour récupérer les consommations de l'utilisateur.
        query = select(FoodConsumption).where(
            FoodConsumption.user_id == user.id,
        )

        # Appliquer les filtres facultatifs.
        if start_date is not None:
            query = query.where(
                FoodConsumption.consumed_at >= start_date,
            )

        if end_date is not None:
            query = query.where(
                FoodConsumption.consumed_at <= end_date,
            )

        if meal_type is not None:
            query = query.where(
                FoodConsumption.meal_type == meal_type,
            )

        # Appliquer l'ordre, la limite et l'offset.
        query = (
            query
            .order_by(FoodConsumption.consumed_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(
            self.db.scalars(query).all()
        )


    """
    Met à jour une consommation.
    Si la quantité change, l'instantané nutritionnel est recalculé à partir de la source d'origine.
    """
    def update_consumption(
        self,
        user: User,
        consumption_id: uuid.UUID,
        data: FoodConsumptionUpdate,
    ) -> FoodConsumption:
 
        consumption = self._get_consumption_or_404(
            user=user,
            consumption_id=consumption_id,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )
        # Récupérer la nouvelle quantité, en utilisant la valeur existante si elle n'est pas fournie.
        new_quantity = update_data.get(
            "quantity_g",
            consumption.quantity_g,
        )

        # Si la quantité a changé, recalculer l'instantané nutritionnel.
        if Decimal(new_quantity) != Decimal(consumption.quantity_g):
            if consumption.food_id is not None:
                food = get_food_or_404(
                    self,
                    food_id=consumption.food_id,
                )

                nutrition = self._calculate_food_nutrition(
                    food=food,
                    quantity_g=Decimal(new_quantity),
                )
            else:
                recipe = get_recipe_or_404(
                    self,
                    user=user,
                    recipe_id=consumption.recipe_id,
                )

                nutrition = self._calculate_recipe_nutrition(
                    recipe=recipe,
                    quantity_g=Decimal(new_quantity),
                )

            for field, value in nutrition.items():
                setattr(consumption, field, value)

        # Mettre à jour les autres champs de la consommation.
        for field, value in update_data.items():
            setattr(consumption, field, value)

        self.db.commit()
        self.db.refresh(consumption)

        return consumption


    """
    Supprime une consommation du journal.
    """
    def delete_consumption(
        self,
        user: User,
        consumption_id: uuid.UUID,
    ) -> None:
        consumption = self._get_consumption_or_404(
            user=user,
            consumption_id=consumption_id,
        )
        self.db.delete(consumption)
        self.db.commit()


    """
    Retourne les totaux nutritionnels consommés par l'utilisateur
    pour une journée civile donnée.
    """
    def get_daily_summary(
        self,
        user: User,
        summary_date: date,
    ) -> DailyNutritionSummaryRead:
        # Définir l'intervalle de temps pour la journée civile donnée.
        start = datetime.combine(
            summary_date,
            time.min,
            tzinfo=timezone.utc,
        )
        end = start + timedelta(days=1)
        # Construire la requête pour agréger les totaux nutritionnels.
        query = select(
            func.coalesce(
                func.sum(FoodConsumption.calories_kcal),
                0,
            ).label("calories_kcal"),
            func.coalesce(
                func.sum(FoodConsumption.protein_g),
                0,
            ).label("protein_g"),
            func.coalesce(
                func.sum(FoodConsumption.carbohydrates_g),
                0,
            ).label("carbohydrates_g"),
            func.coalesce(
                func.sum(FoodConsumption.fat_g),
                0,
            ).label("fat_g"),
        ).where(
            FoodConsumption.user_id == user.id,
            FoodConsumption.consumed_at >= start,
            FoodConsumption.consumed_at < end,
        )
        # Exécuter la requête et récupérer le résultat.
        result = self.db.execute(query).one()

        return DailyNutritionSummaryRead(
            date=summary_date,
            calories_kcal=result.calories_kcal,
            protein_g=result.protein_g,
            carbohydrates_g=result.carbohydrates_g,
            fat_g=result.fat_g,
        )