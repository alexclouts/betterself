from decimal import Decimal
from typing import Optional

from betterself.models.profile_models import ActivityLevel
from pydantic import BaseModel, model_validator
from datetime import date
from enum import Enum
from pydantic import BaseModel, Field
from betterself.schemas.goal_schemas import GoalType, GoalPace
from betterself.schemas.profile_schemas import Sex

# Schéma de lecture du statut d'intégration d'un utilisateur, indiquant quelles étapes ont été complétées et lesquelles manquent.
class OnboardingStatusRead(BaseModel):
    is_complete: bool
    missing_steps: list[str]
    steps: dict[str, bool]


class OnboardingCreate(BaseModel):
    goal_type: GoalType
    pace: GoalPace | None
    first_name: str = Field(min_length=1, max_length=100)
    birth_year: int = Field(ge=1900, le=date.today().year)
    sex: Sex
    height_cm: int = Field(ge=100, le=250)
    current_weight_kg: float = Field(ge=30, le=300)
    target_weight_kg: float | None = Field(default=None, ge=30, le=300)
    activity_level: ActivityLevel

    # Validateur pour s'assurer que les objectifs et les poids sont cohérents.
    @model_validator(mode="after")
    def validate_goal_consistency(self) -> "OnboardingCreate":
        if self.goal_type == GoalType.MAINTAIN_WEIGHT:
            if self.pace is not None:
                raise ValueError(
                    "Un rythme ne doit pas être fourni pour un objectif de maintien."
                )

            if self.target_weight_kg is not None:
                raise ValueError(
                "Un poids cible ne doit pas être fourni pour un objectif de maintien."
            )
            return self

        if self.pace is None:
            raise ValueError(
                "Un rythme est requis pour les objectifs de perte de poids ou de gain musculaire."
            )
        if self.target_weight_kg is None:
            raise ValueError(
                "Un poids cible est requis pour les objectifs de perte de poids ou de gain musculaire."
            )

        if self.goal_type == GoalType.LOSE_WEIGHT:
            if self.target_weight_kg >= self.current_weight_kg:
                raise ValueError(
                    "Le poids cible doit être inférieur au poids actuel pour une perte de poids."
                )
        if self.goal_type == GoalType.GAIN_MUSCLE:
            if self.target_weight_kg <= self.current_weight_kg:
                raise ValueError(
                    "Le poids cible doit être supérieur au poids actuel pour un gain musculaire."
                )
        return self

# Schéma de lecture de la prévisualisation d'un objectif, incluant le poids actuel, le poids cible, le rythme et les calories estimées.
class GoalPreviewRead(BaseModel):
    goal_type: GoalType
    current_weight_kg: Decimal
    target_weight_kg: Optional[Decimal]
    pace: Optional[GoalPace]
    estimated_weeks: Optional[Decimal]
    estimated_completion_date: Optional[date]
    first_target_calories_kcal: Decimal

    model_config = {"from_attributes": True}


# Schéma de lecture de la timeline estimée pour un objectif, incluant les semaines estimées et la date cible.
class GoalTimeline(BaseModel):
    estimated_weeks: Optional[Decimal] = None
    target_date: Optional[date] = None

    model_config = {"from_attributes": True}
