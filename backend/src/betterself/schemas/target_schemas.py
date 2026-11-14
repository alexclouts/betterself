from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from betterself.models.goal_models import GoalType, GoalPace
from betterself.schemas.profile_schemas import ActivityLevel, Sex
from pydantic import BaseModel, Field, field_validator


"""
Représentation d'une cible nutritionnelle.
Une cible est valide pour une période donnée. La cible active est celle dont `valid_until` est `None`; 
les cibles antérieures sont conservées comme historique lorsque le poids de l'utilisateur change.
"""
class GoalTargetRead(BaseModel):
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



class GoalTargetCalculationInput(BaseModel):
    goal_type: GoalType
    pace: Optional[GoalPace] = Field(default=None)
    reference_weight_kg: Decimal
    target_weight_kg: Optional[Decimal] = Field(default=None)
    sex: Sex
    birth_year: int
    height_cm: Decimal
    activity_level: ActivityLevel

    model_config = {"from_attributes": True}