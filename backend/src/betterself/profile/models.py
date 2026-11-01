import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from betterself.core.database import Base

from enum import Enum
from sqlalchemy import Enum as SAEnum


class ActivityLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"

class UserProfile(Base):
    """
    Profil biométrique et préférences d'un utilisateur.

    Une seule ligne de profil existe par utilisateur. Ces informations
    servent notamment au calcul du BMR et des cibles nutritionnelles.
    """

    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    first_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    year_of_birth: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    sex: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
    )

    height_cm: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    activity_level: Mapped[ActivityLevel] = mapped_column(
        SAEnum(
            ActivityLevel,
            name="activity_level",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relation vers l'utilisateur associé. Un profil appartient à un utilisateur unique.
    user = relationship(
        "User",
        back_populates="profile"
    )

    __table_args__ = (
        # Le sexe doit correspondre aux valeurs attendues par le calcul BMR.
        CheckConstraint(
            "sex IN ('M', 'F', 'X')",
            name="user_profiles_check_sex",
        ),

        # Taille plausible en centimètres.
        CheckConstraint(
            "height_cm >= 100 AND height_cm <= 250",
            name="user_profiles_check_height",
        ),

        # Année de naissance plausible : après 1900
        # La borne supérieure est calculée dynamiquement par Pydantic en fonction de l'année courante.
        CheckConstraint(
                "year_of_birth >= 1900",
                name="user_profiles_check_year_of_birth_minimum",
            )
    )