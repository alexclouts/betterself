from datetime import date

from uuid import UUID

from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column

from betterself.core.database import Base

class Measurement(Base):
    __tablename__ = "measurements"

    # Ajout d'une contrainte pour s'assurer que la date et le poids sont dans des plages réalistes
    __table_args__ = (
        # Faire attention: la date d'aujourd'hui selon SQL doit être la même que celle utilisée dans la validation côté application, sinon il pourrait y avoir des incohérences
        CheckConstraint("date >= '2020-01-01' AND date <= CURRENT_DATE",name="ck_measurement_date_range",),
        CheckConstraint("weight_kg > 30 AND weight_kg <= 500", name="ck_measurement_weight_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)

    @classmethod
    def for_user(cls, user_id: UUID):
        # Retourne une requête sélectionnant des objets Measurement complets
        return select(cls).where(cls.user_id == user_id)
