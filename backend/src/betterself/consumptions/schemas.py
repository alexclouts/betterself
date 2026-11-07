from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from betterself.consumptions.models import MealType

"""
Données nécessaires pour ajouter une consommation au journal.
L'utilisateur doit fournir soit un aliment, soit une recette, mais jamais les deux.
"""
class FoodConsumptionCreate(BaseModel):
    food_id: UUID | None = None
    recipe_id: UUID | None = None

    quantity_g: Decimal = Field(
        gt=0,
        le=5000,
        examples=[150],
    )

    meal_type: MealType
    consumed_at: datetime | None = None

    notes: str | None = Field(
        default=None,
        max_length=2000,
    )

    @model_validator(mode="after")
    def validate_single_source(self):
        if self.food_id is not None and self.recipe_id is not None:
            raise ValueError(
                "Fournissez soit food_id, soit recipe_id, mais pas les deux."
            )

        if self.food_id is None and self.recipe_id is None:
            raise ValueError(
                "Fournissez food_id ou recipe_id."
            )

        return self

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()
        return value or None


"""
Met à jour une consommation existante.
La source ne peut pas être changée : un aliment ne devient pas une recette.
La quantité peut être modifiée; l'instantané nutritionnel est recalculé.
"""
class FoodConsumptionUpdate(BaseModel):
    quantity_g: Decimal | None = Field(
        default=None,
        gt=0,
        le=100000,
    )
    meal_type: MealType | None = None
    consumed_at: datetime | None = None

    notes: str | None = Field(
        default=None,
        max_length=2000,
    )

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()
        return value or None


"""
Représentation d'une consommation enregistrée dans le journal.
"""
class FoodConsumptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    food_id: UUID | None
    recipe_id: UUID | None
    item_name_snapshot: str
    quantity_g: Decimal
    calories_kcal: Decimal
    protein_g: Decimal
    fat_g: Decimal
    carbohydrates_g: Decimal
    meal_type: MealType
    consumed_at: datetime
    notes: str | None
    created_at: datetime
    updated_at: datetime


"""
Résumé nutritionnel agrégé pour une journée.
"""
class DailyNutritionSummaryRead(BaseModel):
    date: date
    calories_kcal: Decimal
    protein_g: Decimal
    carbohydrates_g: Decimal
    fat_g: Decimal