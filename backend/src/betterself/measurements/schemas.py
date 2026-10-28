from datetime import date as DateType
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class MeasurementCreate(BaseModel):
    date: DateType
    weight_kg: float = Field(gt=0)

    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, value):
        if value <= 30 or value > 500:
            raise ValueError("Poids invalide")
        return value

    @field_validator("date")
    @classmethod
    def validate_date(cls, value):
        if value > DateType.today() or value < DateType(2020, 1, 1):
            raise ValueError("Date invalide")
        return value
    
    

class MeasurementRead(BaseModel):
    id: int
    user_id: UUID
    date: DateType
    weight_kg: float

    model_config = {"from_attributes": True}

class MeasurementUpdate(BaseModel):
    date: DateType | None = None
    weight_kg: float | None = Field(default=None, gt=0)

    @field_validator("weight_kg")
    def validate_weight(cls, value):
        if value is not None and (value <= 30 or value > 500):
            raise ValueError("Poids invalide")
        return value
    
    @field_validator("date")
    def validate_date(cls, value):
        if value is not None and (value > DateType.today() or value < DateType(2020, 1, 1)):
            raise ValueError("Date invalide")
        return value

    # Doit mettre à jour au moins un champ
    @model_validator(mode="after")
    def validate_update(self) -> "MeasurementUpdate":
        if not self.model_fields_set:
            raise ValueError("Au moins un champ doit être mis à jour")
        return self