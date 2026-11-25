from datetime import date as DateType
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator
from betterself.core.validation import validate_date_not_future
from betterself.schemas.target_update_schemas import TargetUpdateRead

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


"""
Réponse à la création d'une mesure : la mesure, plus le résultat du recalcul
automatique de la cible nutritionnelle (null si aucun recalcul n'a été tenté).
"""
class MeasurementCreatedRead(MeasurementRead):
    target_update: TargetUpdateRead | None = None


"""
Réponse à la modification d'une mesure : la mesure modifiée, plus le résultat
du recalcul de la cible (null si la mesure n'est pas, et n'était pas, la plus récente).
"""
class MeasurementUpdatedRead(MeasurementRead):
    target_update: TargetUpdateRead | None = None


"""
Réponse à la suppression d'une mesure : seulement le résultat du recalcul de la
cible (null si la mesure supprimée n'était pas la plus récente).
"""
class MeasurementDeletedRead(BaseModel):
    target_update: TargetUpdateRead | None = None


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