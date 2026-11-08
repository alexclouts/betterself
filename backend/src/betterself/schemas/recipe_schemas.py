from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from betterself.core.custom_types import (
    NonEmptyText,
    OptionalLongText,
)


"""
Données nécessaires pour créer une recette.
Les ingrédients seront gérés séparément dans `RecipeIngredientCreate` lorsque la table `recipe_ingredients` sera intégrée.
"""
class RecipeCreate(BaseModel):
    name: NonEmptyText = Field(
        examples=["Bol de poulet et riz"],
    )

    description: OptionalLongText = Field(
        default=None,
        examples=[
            "Faire cuire le riz, puis ajouter le poulet et les légumes.",
        ],
    )

    total_weight_g: Decimal = Field(
        gt=0,
        le=100000,
        examples=[800],
        description="Poids total de la recette préparée, en grammes.",
    )

    servings: int = Field(
        gt=0,
        le=1000,
        examples=[6],
    )


"""
Données permettant de mettre à jour partiellement une recette.
Les champs non fournis conservent leur valeur actuelle.
"""
class RecipeUpdate(BaseModel):
    name: NonEmptyText | None = Field(
        default=None,
        examples=["Bol de poulet et riz v2"],
    )

    description: OptionalLongText = None

    total_weight_g: Decimal | None = Field(
        default=None,
        gt=0,
        le=100000,
    )

    servings: int | None = Field(
        default=None,
        gt=0,
        le=1000,
    )


"""
Représentation d'une recette renvoyée par l'API.
"""
class RecipeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    description: str | None
    total_weight_g: Decimal
    servings: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    ingredients: list[RecipeIngredientRead] = Field(
        default_factory=list,
        description="Liste des ingrédients de la recette.",
    )
    nutrition: RecipeNutritionRead = Field(
        description="Valeurs nutritionnelles de la recette.",
    )


"""
Données permettant d'archiver ou de désarchiver une recette.
"""
class RecipeArchiveUpdate(BaseModel):
    is_archived: bool


"""
Représentation des valeurs nutritionnelles d'une recette.
"""
class RecipeNutritionRead(BaseModel):
    calories_kcal: Decimal
    protein_g: Decimal
    carbohydrates_g: Decimal
    fat_g: Decimal


"""
Données nécessaires pour ajouter un aliment à une recette.
"""
class RecipeIngredientCreate(BaseModel):
    food_id: UUID
    recipe_id: UUID
    quantity_g: Decimal = Field(
        gt=0,
        le=100000,
        examples=[150],
        description="Quantité de l'aliment utilisée, en grammes.",
    )


"""
Données permettant de mettre à jour la quantité d'un ingrédient.
"""
class RecipeIngredientUpdate(BaseModel):
    quantity_g: Decimal = Field(
        gt=0,
        le=100000,
        examples=[200],
    )


"""
Représentation d'un ingrédient de recette renvoyé par l'API.
"""
class RecipeIngredientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recipe_id: UUID
    food_id: UUID
    quantity_g: Decimal
    created_at: datetime
    updated_at: datetime