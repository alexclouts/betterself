from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class MeasurementCreate(BaseModel):
    date: date
    weight_kg: float = Field(gt=0)


class MeasurementRead(BaseModel):
    id: int
    user_id: UUID
    date: date
    weight_kg: float

    model_config = {"from_attributes": True}