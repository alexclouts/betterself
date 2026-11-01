

from decimal import Decimal
from enum import Enum
from sqlalchemy import UUID, Enum as SAEnum, select
from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, Index, Integer, Numeric, String, func
import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


from betterself.core.database import Base
from sqlalchemy import ForeignKey

class GoalType(str, Enum):
    LOSE_WEIGHT = "lose_weight"
    MAINTAIN_WEIGHT = "maintain_weight"
    GAIN_MUSCLE = "gain_muscle"
    BODY_RECOMPOSITION = "body_recomposition"

class NutritionGoal(Base):
    __tablename__ = "nutrition_goals"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    goal_type: Mapped[GoalType] = mapped_column(
        SAEnum(GoalType, name="goal_type"), 
        nullable=False
    )
    start_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(6,2),
        nullable=False
    )
    target_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(6,2),
        nullable=True
    )
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now()
    )
    target_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=True, # L'utilisateur a le choix de ne pas définir de date cible
        server_default=func.now()
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now(),
        onupdate=func.now()
    )


    __table_args__ = (
        # Contraintes de validation des données
        CheckConstraint('target_date IS NULL OR target_date > start_date',
                        name="nutrition_goals_check_target_date"
        ),
        CheckConstraint('target_weight_kg IS NULL OR target_weight_kg > 30 OR target_weight_kg < 500',
                        name="nutrition_goals_check_target_weight"
        ),
        CheckConstraint("status IN ('active', 'completed', 'cancelled')",
                        name="nutrition_goals_check_status",
        ),
        # Index pour accélérer les requêtes par utilisateur et date de début
        Index("idx_nutrition_goals_user",
              "user_id",
              "start_date",
              unique=False
        )
    )

    @classmethod
    def for_user(cls, user_id: uuid.UUID):
        # Retourne une requête sélectionnant des objets NutritionGoal complets
        return select(cls).where(cls.user_id == user_id)


"""
Modèle représentant les cibles nutritionnelles associées à un objectif de nutrition.
"""
class GoalTarget(Base):
    __tablename__ = "goal_targets"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    goal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("nutrition_goals.id", ondelete="CASCADE"), 
        nullable=False
    )
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now()
    )
    valid_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    reference_weight_kg: Mapped[Decimal] = mapped_column(
        Numeric(6,2),
        nullable=False
    )
    maintenance_calories_kcal: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    calories_target_kcal: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    calories_adjustment_kcal: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    protein_target_g: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    carbs_target_g: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    fat_target_g: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    calculation_method: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint('valid_until IS NULL OR valid_until > valid_from',
                        name="goal_targets_check_valid_until"
        ),
        CheckConstraint('maintenance_calories_kcal >= 1200 AND calories_target_kcal >= 1200 AND calories_adjustment_kcal >= 1200',
                        name="goal_targets_check_calories"
        ),
        CheckConstraint('protein_target_g >= 0 AND carbs_target_g >= 0 AND fat_target_g >= 0',
                        name="goal_targets_check_macros"
        ),
        CheckConstraint('reference_weight_kg >= 30',
                        name="goal_targets_check_reference_weight"
        ),
        # Index pour accélérer la requête permettant de voir quel objectif est actif pour un goal donné
        Index("idx_goal_targets_valid_until",
              "goal_id",
              "valid_until"
        )
    )

    
