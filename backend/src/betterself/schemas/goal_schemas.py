from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator
from betterself.models.goal_models import GoalType
from betterself.core.validation import validate_date_not_future, validate_date_within_allowed_range
    

class NutritionGoalCreate(BaseModel):
    goal_type: GoalType = Field(example="lose_weight")
    
    start_weight_kg: Decimal = Field(gt=30, le=500)
    target_weight_kg: Decimal = Field(gt=30, le=500)

    
    start_date: date
    target_date: date | None = None
    
    @field_validator("start_date")
    def validate_start_date(cls, value):
        return validate_date_not_future(value)

    
    @field_validator("target_date")
    def validate_target_date(cls, value):
        if value is not None:
            return validate_date_within_allowed_range(value)
        return value

    @model_validator(mode="after")
    def validate_dates(self) -> "NutritionGoalCreate":
        if (
            self.start_date is not None
            and self.target_date is not None
            and self.target_date < self.start_date
        ):
            raise ValueError(
                "La date cible doit être postérieure à la date de début."
            )
        return self

    model_config = {"from_attributes": True}


class NutritionGoalRead(BaseModel):
    user_id: UUID
    goal_type: GoalType
    start_weight_kg: Decimal
    target_weight_kg: Decimal | None
    start_date: date
    target_date: date | None
    status: str

    model_config = {"from_attributes": True}
