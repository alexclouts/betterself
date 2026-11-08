from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from betterself.core.custom_types import (
    NonEmptyText,
    OptionalLongText,
    OptionalText,
)
from betterself.models.food_models import FoodCategory, FoodSource


class FoodCreate(BaseModel):
    name: NonEmptyText
    brand: OptionalText = None
    description: OptionalLongText = None
    category: FoodCategory | None = None

    reference_weight_g: Decimal = Field(gt=0, le=100000)
    calories_kcal: Decimal = Field(ge=0)
    protein_g: Decimal = Field(ge=0, le=100000)
    carbohydrates_g: Decimal = Field(ge=0, le=100000)
    fat_g: Decimal = Field(ge=0, le=100000)

    source: FoodSource = FoodSource.MANUAL
    external_reference_id: OptionalText = None


    """
    Valide que les calories déclarées correspondent aux macronutriments pour les aliments manuels.
    """
    @model_validator(mode="after")
    def validate_manual_food_macros(self) -> "FoodCreate":
        if self.source is not FoodSource.MANUAL:
            return self

        calculated_calories = (
            self.protein_g * 4
            + self.carbohydrates_g * 4
            + self.fat_g * 9
        )

        # Accepte une différence raisonnable entre les calories
        # déclarées et celles calculées à partir des macronutriments.
        tolerance = max(
            Decimal("10"),
            calculated_calories * Decimal("0.10"),
        )

        if abs(self.calories_kcal - calculated_calories) > tolerance:
            raise ValueError(
                "Les calories ne correspondent pas aux macronutriments fournis."
            )

        return self


"""
Données permettant de mettre à jour les informations descriptives d'un aliment manuel.
Les valeurs nutritionnelles sont immuables : elles ne peuvent pas être modifiées après la création de l'aliment.
"""
class FoodUpdate(BaseModel):
    name: NonEmptyText | None = None
    brand: OptionalText = None
    description: OptionalLongText = None


class FoodRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    brand: str | None
    description: str | None
    category: FoodCategory | None
    reference_weight_g: Decimal
    calories_kcal: Decimal
    protein_g: Decimal
    carbohydrates_g: Decimal
    fat_g: Decimal
    source: FoodSource
    external_reference_id: str | None
    created_by_user_id: UUID | None
    created_at: datetime
    updated_at: datetime