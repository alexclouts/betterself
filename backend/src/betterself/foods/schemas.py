from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from betterself.foods.models import FoodCategory, FoodSource


class FoodCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    brand: str | None = Field(default=None, max_length=255)
    description: str | None = None
    category: FoodCategory | None = None

    reference_weight_g: Decimal = Field(gt=0, le=100000)
    calories_kcal: Decimal = Field(ge=0)
    protein_g: Decimal = Field(ge=0)
    carbohydrates_g: Decimal = Field(ge=0)
    fat_g: Decimal = Field(ge=0)

    source: FoodSource = FoodSource.MANUAL
    external_reference_id: str | None = Field(
        default=None,
        max_length=255,
    )

    # Supprime les espaces superflus pour certains champs de texte.
    @field_validator("name", "brand", "external_reference_id")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()
        return value or None


    # Valide que le nom de l'aliment n'est pas vide.
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value:
            raise ValueError("Le nom de l'aliment est obligatoire.")

        return value


    # Valide et nettoie la description de l'aliment.
    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()
        return value or None


    # Vérifie que les champs numériques ne sont pas négatifs.
    @field_validator("reference_weight_g", "calories_kcal")
    @classmethod
    def validate_non_negative_decimal(
        cls,
        value: Decimal,
        info,
    ) -> Decimal:
        if value < 0:
            raise ValueError(
                f"Le champ {info.field_name} ne peut pas être négatif."
            )

        return value


    # Valide que les macronutriments sont corrects et dans des limites raisonnables.
    @field_validator("protein_g", "carbohydrates_g", "fat_g")
    @classmethod
    def validate_macros(cls, value: Decimal, info) -> Decimal:
        if value < 0:
            raise ValueError(
                f"Le champ {info.field_name} ne peut pas être négatif."
            )

        # Évite les valeurs manifestement aberrantes pour 100 g.
        if value > 100000:
            raise ValueError(
                f"Le champ {info.field_name} dépasse la limite autorisée."
            )

        return value


    # Valide que les calories correspondent aux macronutriments pour les aliments manuels.
    @model_validator(mode="after")
    def validate_manual_food_macros(self) -> "FoodCreate":
        if self.source is not FoodSource.MANUAL:
            return self

        calculated_calories = (
            self.protein_g * 4
            + self.carbohydrates_g * 4
            + self.fat_g * 9
        )

        # La tolérance de 10% vise à accepter de légères différences entre les calories 
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


class FoodUpdate(BaseModel):
    """
    Données permettant de mettre à jour les informations descriptives
    d'un aliment manuel.

    Les valeurs nutritionnelles sont immuables : elles ne peuvent pas
    être modifiées après la création de l'aliment.
    """

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    brand: str | None = Field(
        default=None,
        max_length=255,
        examples=["Marque exemple"],
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
        examples=["Yogourt grec nature, 2 % matière grasse."],
    )


    @field_validator("brand", "description")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()
        return value or None


    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        value = value.strip()

        if not value:
            raise ValueError(
                "Le nom de l'aliment ne peut pas être vide."
            )
        return value


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