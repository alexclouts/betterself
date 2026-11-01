from datetime import date
from decimal import Decimal
import uuid

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from betterself.core.database import Base


class GoalTarget(Base):
    """
    Cible nutritionnelle associée à l'objectif d'un utilisateur.

    Une cible représente l'objectif micro à atteindre pour une période donnée :
    calories de maintien, calories cibles, ajustement calorique et
    macronutriments.

    Une seule cible peut être active à la fois. Lorsque le poids de
    l'utilisateur change, une nouvelle cible est créée et la cible précédente
    est fermée en renseignant `valid_until`. L'ancienne cible reste ainsi
    disponible dans l'historique.
    """

    __tablename__ = "goal_targets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # La cible est rattachée directement à l'utilisateur, puisqu'il ne
    # possède qu'un seul objectif nutritionnel.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    valid_from: Mapped[date] = mapped_column(
        Date,
        nullable=False,
         server_default=func.current_date(),
    )

    # Une cible dont `valid_until` est NULL est la cible active.
    valid_until: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    reference_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(6, 2),
        nullable=False,
    )

    maintenance_calories_kcal: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    calories_target_kcal: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    calories_adjustment_kcal: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    protein_target_g: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    carbs_target_g: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    fat_target_g: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    calculation_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[date] = mapped_column(
        Date,
        nullable=False,
         server_default=func.current_date(),
    )

    __table_args__ = (
        # TODO: En production, valid_until devra être toujours supérieur ou égal à valid_from
        CheckConstraint(
            "valid_until IS NULL OR valid_until >= valid_from",
            name="goal_targets_check_valid_until",
        ),
        CheckConstraint(
            "maintenance_calories_kcal >= 1200 AND calories_target_kcal >= 1200",
            name="goal_targets_check_calories",
        ),
        CheckConstraint(
            "protein_target_g >= 0 AND carbs_target_g >= 0 AND fat_target_g >= 0",
            name="goal_targets_check_macros",
        ),
        CheckConstraint(
            "reference_weight_kg >= 30",
            name="goal_targets_check_reference_weight",
        ),
        # Garantit qu'un utilisateur ne peut avoir qu'une seule cible active.
        # Les cibles fermées restent conservées pour l'historique.
        Index(
            "uq_one_active_goal_target_per_user",
            "user_id",
            unique=True,
            postgresql_where=text("valid_until IS NULL"),
            sqlite_where=text("valid_until IS NULL"),
        ),
        # Index pour accélérer la recherche de l'historique des cibles
        Index(
            "idx_goal_targets_user_valid_from",
            "user_id",
            "valid_from",
        )
    )