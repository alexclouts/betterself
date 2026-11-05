import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from betterself.recipes.models import Recipe
from betterself.foods.models import Food
from betterself.users.models import User
from betterself.core.database import Base


# Enum qui représente les types de repas (petit-déjeuner, déjeuner, dîner, collation)
class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class FoodConsumption(Base):
    __tablename__ = "food_consumptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    food_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("foods.id", ondelete="RESTRICT"),
        nullable=True,
    )

    recipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recipes.id", ondelete="RESTRICT"),
        nullable=True,
    )

    item_name_snapshot: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    quantity_g: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        CheckConstraint("quantity_g > 0"),
        nullable=False,
    )

    calories_kcal: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        CheckConstraint("calories_kcal >= 0"),
        nullable=False,
    )

    protein_g: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        CheckConstraint("protein_g >= 0"),
        nullable=False,
    )

    fat_g: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        CheckConstraint("fat_g >= 0"),
        nullable=False,
    )

    carbohydrates_g: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        CheckConstraint("carbohydrates_g >= 0"),
        nullable=False,
    )

    meal_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    consumed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    notes: Mapped[str] = mapped_column(
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "(food_id IS NOT NULL AND recipe_id IS NULL) OR (food_id IS NULL AND recipe_id IS NOT NULL)",
            name="ck_food_consumptions_one_source",
        ),
    )

    user: Mapped["User"] = relationship(
        "User", 
        back_populates="food_consumptions"
    )
    food: Mapped["Food"] = relationship(
        "Food", 
        back_populates="food_consumptions"
    )
    recipe: Mapped["Recipe"] = relationship(
        "Recipe",
        back_populates="food_consumptions"
    )