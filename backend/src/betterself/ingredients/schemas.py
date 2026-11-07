from decimal import Decimal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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