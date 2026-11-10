from betterself.models.profile_models import ActivityLevel
from pydantic import BaseModel
from datetime import date
from enum import Enum
from pydantic import BaseModel, Field
from betterself.schemas.goal_schemas import GoalType
from betterself.schemas.profile_schemas import Sex

# Schéma de lecture du statut d'intégration d'un utilisateur, indiquant quelles étapes ont été complétées et lesquelles manquent.
class OnboardingStatusRead(BaseModel):
    is_complete: bool
    missing_steps: list[str]
    steps: dict[str, bool]


class OnboardingCreate(BaseModel):
    goal: GoalType
    name: str = Field(min_length=1, max_length=100)
    birth_year: int = Field(ge=1900, le=date.today().year)
    sex: Sex
    height_cm: int = Field(ge=100, le=250)
    weight_kg: float = Field(ge=30, le=300)
    activity_level: ActivityLevel
    