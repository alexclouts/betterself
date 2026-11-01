from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from betterself.core.validation import validate_weight_kg


class GoalTargetRead(BaseModel):
    """
    Représentation d'une cible nutritionnelle.

    Une cible est valide pour une période donnée. La cible active est celle
    dont `valid_until` est `None`; les cibles antérieures sont conservées
    comme historique lorsque le poids de l'utilisateur change.
    """

    id: UUID
    user_id: UUID
    valid_from: date
    valid_until: date | None
    reference_weight_kg: Decimal
    maintenance_calories_kcal: int
    calories_target_kcal: int
    calories_adjustment_kcal: int
    protein_target_g: int
    carbs_target_g: int
    fat_target_g: int
    calculation_method: str

    model_config = {"from_attributes": True}


class GoalTargetRecalculate(BaseModel):
    """
    Payload temporaire pour le recalcul d'une cible nutritionnelle.

    TODO: Lorsque la table `user_profiles` sera implémentée, seuls
    `reference_weight_kg` devrait rester dans ce payload. Les paramètres
    biométriques seront récupérés depuis le profil de l'utilisateur.
    """

    reference_weight_kg: Decimal = Field(
        ge=30,
        le=300,
        examples=[85],
    )

    # Champs temporaires jusqu'à l'implémentation de user_profiles.
    sex: str = Field(
        examples=["M"],
        description="Sexe utilisé pour le calcul du BMR.",
    )
    birth_year: int = Field(
        ge=1900,
        le=date.today().year,
        examples=[1996],
    )
    height_cm: Decimal = Field(
        ge=100,
        le=250,
        examples=[175],
    )
    activity_level: str = Field(
        examples=["moderate"],
        description="Niveau d'activité physique.",
    )

    @field_validator("reference_weight_kg")
    @classmethod
    def validate_weight(cls, value: Decimal) -> Decimal:
        return validate_weight_kg(value)