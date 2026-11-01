from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator
from betterself.nutrition.models import GoalType
from betterself.core.validation import validate_weight_kg, validate_date_not_future, validate_date_in_future, RangeValidationError


class NutritionGoalCreate(BaseModel):
    goal_type: GoalType = Field(example="lose_weight")
    start_weight_kg: Decimal = Field(gt=0)
    target_weight_kg: Decimal = Field(gt=0)

    @field_validator("start_weight_kg", "target_weight_kg")
    def validate_weight(cls, value):
        return validate_weight_kg(value)

    
    start_date: date
    target_date: date | None = None
    
    @field_validator("start_date")
    def validate_start_date(cls, value):
        return validate_date_not_future(value)

    
    @field_validator("target_date")
    def validate_target_date(cls, value):
        if value is not None:
            return validate_date_in_future(value)
        return value

    @model_validator(mode="after")
    def validate_dates(self) -> "NutritionGoalCreate":
        if (
            self.start_date is not None
            and self.target_date is not None
            and self.target_date < self.start_date
        ):
            raise RangeValidationError(
                "La date cible doit être postérieure à la date de début."
            )
        return self

    model_config = {"from_attributes": True}


class NutritionGoalRead(BaseModel):
    id: UUID
    user_id: UUID
    goal_type: GoalType
    start_weight_kg: Decimal
    target_weight_kg: Decimal | None
    start_date: date
    target_date: date | None
    status: str

    model_config = {"from_attributes": True}

class GoalTargetRead(BaseModel):
    id: UUID
    goal_id: UUID
    valid_from: date
    valid_until: date | None
    reference_weight_kg: Decimal
    maintenance_calories_kcal: int
    calorie_target_kcal: int
    calorie_adjustment_kcal: int
    protein_target_g: Decimal
    carbs_target_g: Decimal
    fat_target_g: Decimal
    calculation_method: str

    model_config = {"from_attributes": True}

class GoalTargetRecalculate(BaseModel):
    reference_weight_kg: Decimal = Field(gt=0)

