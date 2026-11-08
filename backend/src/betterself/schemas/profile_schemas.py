import re
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from betterself.models.profile_models import ActivityLevel


"""
Représentation d'un profil utilisateur renvoyée par l'API.
"""
class UserProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    first_name: str | None
    year_of_birth: int
    sex: str
    height_cm: Decimal
    activity_level: ActivityLevel
    updated_at: datetime


class UserProfileUpdate(BaseModel):
    first_name: str | None = Field(
        default=None,
        max_length=100,
        examples=["Alex"],
    )

    year_of_birth: int = Field(
        ge=1900,
        le=date.today().year,
        examples=[1996],
    )

    sex: str = Field(
        pattern="^[MFX]$",
        examples=["M"],
    )

    height_cm: Decimal = Field(
        ge=100,
        le=250,
        examples=[175],
    )

    activity_level: ActivityLevel = Field(
        examples=["moderate"],
    )


    @field_validator("year_of_birth")
    @classmethod
    def validate_year_of_birth(cls, value: int) -> int:
        current_year = date.today().year

        if value > current_year:
            raise ValueError(
                "L'année de naissance ne peut pas être dans le futur."
            )

        # Refuse les nourrissons et les années manifestement invalides.
        if value > current_year - 13:
            raise ValueError(
                "L'année de naissance est trop récente."
            )

        return value

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            return None

        # Lettres Unicode, espaces, apostrophes typographiques/droites,
        # tirets simples et points.
        allowed_pattern = re.compile(
            r"^[^\W\d_]+(?:[ '\-\.][^\W\d_]+)*$",
            re.UNICODE,
        )

        if not allowed_pattern.fullmatch(value):
            raise ValueError(
                "Le prénom contient des caractères non autorisés."
            )
        return value