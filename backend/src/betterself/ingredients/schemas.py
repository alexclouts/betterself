from decimal import Decimal
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RecipeIngredientCreate(BaseModel):
    """
    Données nécessaires pour ajouter un aliment à une recette.
    """
    food_id: UUID
    recipe_id: UUID
    quantity_g: Decimal = Field(
        gt=0,
        le=100000,
        examples=[150],
        description="Quantité de l'aliment utilisée, en grammes.",
    )


class RecipeIngredientUpdate(BaseModel):
    """
    Données permettant de mettre à jour la quantité d'un ingrédient.
    """
    quantity_g: Decimal = Field(
        gt=0,
        le=100000,
        examples=[200],
    )


class RecipeIngredientRead(BaseModel):
    """
    Représentation d'un ingrédient de recette renvoyé par l'API.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recipe_id: UUID
    food_id: UUID
    quantity_g: Decimal
    created_at: datetime
    updated_at: datetime