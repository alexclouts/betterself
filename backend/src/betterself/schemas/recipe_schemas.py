from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from betterself.core.custom_types import (
    NonEmptyText,
    OptionalLongText,
)


"""
Aliment et quantité d'un ingrédient fourni à la création d'une recette.
"""
class RecipeIngredientInput(BaseModel):
    food_id: UUID
    quantity_g: Decimal = Field(
        gt=0,
        le=100000,
        examples=[150],
        description="Quantité de l'aliment utilisée, en grammes.",
    )


"""
Données nécessaires pour créer une recette avec ses ingrédients.
Le poids total n'est pas fourni : il est la somme des quantités des ingrédients.
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

    servings: int = Field(
        gt=0,
        le=1000,
        examples=[6],
    )

    ingredients: list[RecipeIngredientInput] = Field(
        min_length=1,
        description="Ingrédients de la recette; au moins un, sans aliment en double.",
    )

    # Un aliment ne peut apparaître qu'une fois dans une recette.
    @field_validator("ingredients")
    @classmethod
    def reject_duplicate_foods(
        cls,
        ingredients: list[RecipeIngredientInput],
    ) -> list[RecipeIngredientInput]:
        food_ids = [ingredient.food_id for ingredient in ingredients]
        if len(food_ids) != len(set(food_ids)):
            raise ValueError("Un aliment ne peut apparaître qu'une fois dans une recette.")
        return ingredients


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
    total_weight_g: Decimal = Field(
        description="Poids total de la recette : somme des quantités des ingrédients, en grammes.",
    )
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
    id: UUID
    recipe_id: UUID
    food: RecipeIngredientFoodRead = Field(
        description="Aliment utilisé comme ingrédient.",
    )
    quantity_g: Decimal
    nutrition: RecipeNutritionRead = Field(
        description="Valeurs nutritionnelles pour la quantité de l'ingrédient.",
    )
    created_at: datetime
    updated_at: datetime


"""
Aliment d'un ingrédient de recette, avec ses valeurs nutritionnelles
pour sa quantité de référence. Évite une requête par aliment côté client.
"""
class RecipeIngredientFoodRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    brand: str | None
    reference_weight_g: Decimal
    calories_kcal: Decimal
    protein_g: Decimal
    carbohydrates_g: Decimal
    fat_g: Decimal