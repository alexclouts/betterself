from datetime import date
from decimal import Decimal
from enum import Enum
import uuid

from sqlalchemy import (
    CheckConstraint,
    Date,
    Enum as SAEnum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from betterself.core.database import Base


class GoalType(str, Enum):
    LOSE_WEIGHT = "lose_weight"
    MAINTAIN_WEIGHT = "maintain_weight"
    GAIN_MUSCLE = "gain_muscle"
    BODY_RECOMPOSITION = "body_recomposition"


class NutritionGoal(Base):
    """
    Objectif nutritionnel d'un utilisateur.

    L'objectif est créé durant le processus de onboarding. Il peut ensuite
    être modifié, mais chaque utilisateur ne peut en posséder qu'un seul.

    L'objectif est une extension du profil fonctionnel de l'utilisateur :
    sa clé primaire est directement `user_id`, plutôt qu'un identifiant
    autonome. Cela garantit, au niveau de la base de données, qu'un
    utilisateur ne peut avoir qu'un seul objectif.
    """

    __tablename__ = "nutrition_goals"

    # La clé primaire est l'identifiant de l'utilisateur.
    # Il ne peut donc exister qu'une seule ligne d'objectif par utilisateur.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    goal_type: Mapped[GoalType] = mapped_column(
        SAEnum(GoalType, name="goal_type"),
        nullable=False,
    )

    start_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        nullable=False,
    )

    # L'utilisateur peut choisir de ne pas définir de poids cible.
    target_weight_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
         server_default=func.current_date(),
    )

    # L'utilisateur a le choix de ne pas définir de date cible.
    target_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # TODO: Définir un Enum pour le statut de l'objectif (actif, complété)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    created_at: Mapped[date] = mapped_column(
        Date,
        nullable=False,
         server_default=func.current_date(),
    )

    updated_at: Mapped[date] = mapped_column(
        Date,
        nullable=False,
         server_default=func.current_date(),
        onupdate=func.current_date(),
    )

    user = relationship(
        "User",
        back_populates="nutrition_goal",
    )

    __table_args__ = (
        # Contraintes de validation des données
        CheckConstraint(
            "target_date IS NULL OR target_date > start_date",
            name="nutrition_goals_check_target_date",
        ),
        # Vérifie que le poids cible est soit nul, soit compris dans une plage plausible
        CheckConstraint(
            "target_weight_kg IS NULL OR (target_weight_kg > 30 AND target_weight_kg <= 500)",
            name="nutrition_goals_check_target_weight",
        ),
        CheckConstraint(
            "start_weight_kg > 30 AND start_weight_kg <= 500",
            name="nutrition_goals_check_start_weight",
        ),

        CheckConstraint(
            "status IN ('active', 'completed', 'cancelled')",
            name="nutrition_goals_check_status",
        ),
    )