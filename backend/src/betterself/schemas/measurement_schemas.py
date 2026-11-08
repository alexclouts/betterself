from datetime import date as DateType
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator
from betterself.core.validation import validate_date_not_future

class MeasurementCreate(BaseModel):
    date: DateType
    weight_kg: float = Field(gt=30, le=500)

    @field_validator("date")
    @classmethod
    def validate_date(cls, value):
        return validate_date_not_future(value)
    
    

class MeasurementRead(BaseModel):
    id: int
    user_id: UUID
    date: DateType
    weight_kg: float

    model_config = {"from_attributes": True}


class MeasurementUpdate(BaseModel):
    date: DateType | None = None
    weight_kg: float | None = Field(default=None, gt=30, le=500)
    
    @field_validator("date")
    def validate_date(cls, value):
        if value is not None:
            return validate_date_not_future(value)
        return value

    # Doit mettre à jour au moins un champ
    @model_validator(mode="after")
    def validate_update(self) -> "MeasurementUpdate":
        if not self.model_fields_set:
            raise ValueError("Au moins un champ doit être mis à jour")
        return self