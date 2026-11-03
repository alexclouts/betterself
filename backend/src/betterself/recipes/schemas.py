from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

"""
RecipeCreate n’accepte pas user_id, is_archived, created_at ou updated_at : ces valeurs sont définies par le serveur.
"""

class RecipeCreate(BaseModel):
    """
    Données nécessaires pour créer une recette.
    Les ingrédients seront gérés séparément dans `RecipeIngredientCreate`
    lorsque la table `recipe_ingredients` sera intégrée.
    """

    name: str = Field(
        min_length=1,
        max_length=255,
        examples=["Bol de poulet et riz"],
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
        examples=[
            "Faire cuire le riz, puis ajouter le poulet et les légumes."
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

    # Validateur pour le nom de la recette lors de la création
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Le nom de la recette ne peut pas être vide."
            )
        return value

    # Validateur pour la description de la recette lors de la création
    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()
        return value or None


class RecipeUpdate(BaseModel):
    """
    Données permettant de mettre à jour partiellement une recette.
    Les champs non fournis conservent leur valeur actuelle.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        examples=["Bol de poulet et riz v2"],
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

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

    # Validateur pour le nom de la recette lors de la mise à jour
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        value = value.strip()

        if not value:
            raise ValueError(
                "Le nom de la recette ne peut pas être vide."
            )
        return value


    # Validateur pour la description de la recette lors de la mise à jour
    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()
        return value or None


class RecipeRead(BaseModel):
    """
    Représentation d'une recette renvoyée par l'API.
    """

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


class RecipeArchiveUpdate(BaseModel):
    """
    Données permettant d'archiver ou de désarchiver une recette.
    """
    is_archived: bool