from datetime import datetime
from decimal import Decimal
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from betterself.core.custom_types import (
    NonEmptyText,
    OptionalLongText,
    OptionalText,
)
from betterself.models.food_models import Food, FoodCategory, FoodSource
from betterself.repos.off_catalog_repo import CatalogProduct


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

    # Les aliments Open Food Facts sont créés seulement par l'import du catalogue.
    source: Literal[FoodSource.MANUAL] = FoodSource.MANUAL
    external_reference_id: OptionalText = None


    """
    Valide que les calories déclarées correspondent aux macronutriments pour les aliments manuels.
    """
    @model_validator(mode="after")
    def validate_manual_food_macros(self) -> "FoodCreate":
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
    serving_g: Decimal | None
    # Unité propre à l'aliment (« tranche », 25 g), ou None.
    unit_name: str | None
    unit_name_plural: str | None
    unit_g: Decimal | None
    # La portion ou l'unité est convertie en grammes sans poids sur l'étiquette.
    weight_is_estimated: bool
    calories_kcal: Decimal
    protein_g: Decimal
    carbohydrates_g: Decimal
    fat_g: Decimal
    source: FoodSource
    external_reference_id: str | None
    created_by_user_id: UUID | None
    created_at: datetime
    updated_at: datetime


"""
Résultat de la recherche : un aliment de la base (`food_id`) ou un produit du
catalogue Open Food Facts pas encore importé (`catalog_code`).
"""
class FoodSearchResult(BaseModel):
    food_id: UUID | None
    catalog_code: str | None
    source: FoodSource
    # L'utilisateur a déjà consigné ou créé cet aliment.
    in_history: bool

    name: str
    brand: str | None
    reference_weight_g: Decimal
    serving_g: Decimal | None
    # Unité propre à l'aliment (« tranche », 25 g), ou None.
    unit_name: str | None
    unit_name_plural: str | None
    unit_g: Decimal | None
    # La portion ou l'unité est convertie en grammes sans poids sur l'étiquette.
    weight_is_estimated: bool
    calories_kcal: Decimal
    protein_g: Decimal
    carbohydrates_g: Decimal
    fat_g: Decimal

    @classmethod
    def _from_nutrition(cls, item: Food | CatalogProduct, **values) -> Self:
        return cls(
            name=item.name,
            brand=item.brand,
            reference_weight_g=item.reference_weight_g,
            serving_g=item.serving_g,
            unit_name=item.unit_name,
            unit_name_plural=item.unit_name_plural,
            unit_g=item.unit_g,
            weight_is_estimated=item.weight_is_estimated,
            calories_kcal=item.calories_kcal,
            protein_g=item.protein_g,
            carbohydrates_g=item.carbohydrates_g,
            fat_g=item.fat_g,
            **values,
        )

    @classmethod
    def from_food(cls, food: Food, in_history: bool) -> Self:
        return cls._from_nutrition(
            food, food_id=food.id, catalog_code=None, source=food.source, in_history=in_history
        )

    @classmethod
    def from_product(cls, product: CatalogProduct) -> Self:
        return cls._from_nutrition(
            product,
            food_id=None,
            catalog_code=product.code,
            source=FoodSource.OPEN_FOOD_FACTS,
            in_history=False,
        )


class FoodSearchRead(BaseModel):
    results: list[FoodSearchResult]
    # Faux si le catalogue Open Food Facts est absent ou illisible.
    catalog_available: bool
