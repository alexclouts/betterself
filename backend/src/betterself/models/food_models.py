import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from betterself.core.database import Base


class FoodCategory(str, Enum):
    """
    Catégories alignées avec les grands groupes du Guide alimentaire
    canadien : aliments protéinés, aliments à grains entiers et légumes
    et fruits. Les catégories complémentaires couvrent les produits
    transformés, boissons et suppléments.
    """

    VEGETABLES_AND_FRUITS = "vegetables_and_fruits"
    CEREALS = "cereals"
    MEAT = "meat"
    NUTS_AND_SEEDS = "nuts_and_seeds"
    DAIRY = "dairy"
    FATS_AND_OILS = "fats_and_oils"
    BEVERAGES = "beverages"
    SWEETS = "sweets"
    PREPARED_MEALS = "prepared_meals"
    SUPPLEMENTS = "supplements"
    OTHER = "other"



class FoodSource(str, Enum):
    MANUAL = "manual"
    OPEN_FOOD_FACTS = "open_food_facts"


class Food(Base):
    """
    Aliment ou produit alimentaire disponible dans la base de données.

    Les valeurs nutritionnelles sont exprimées pour la quantité de
    référence `reference_weight_g`. Elles peuvent provenir d'une saisie
    manuelle ou d'une source externe, telle que Open Food Facts.
    """

    __tablename__ = "foods"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    brand: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    category: Mapped[FoodCategory | None] = mapped_column(
        SAEnum(
            FoodCategory,
            name="food_category",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=True,
    )

    reference_weight_g: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
    )

    calories_kcal: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
    )

    protein_g: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
    )

    carbohydrates_g: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
    )

    fat_g: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
    )

    source: Mapped[FoodSource] = mapped_column(
        SAEnum(
            FoodSource,
            name="food_source",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=FoodSource.MANUAL,
    )

    external_reference_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    created_by = relationship(
        "User",
        foreign_keys=[created_by_user_id],
    )

    food_consumptions: Mapped[list["FoodConsumption"]] = relationship(
        "FoodConsumption",
        back_populates="food",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "reference_weight_g > 0",
            name="foods_check_reference_weight",
        ),
        CheckConstraint(
            "calories_kcal >= 0",
            name="foods_check_calories",
        ),
        CheckConstraint(
            "protein_g >= 0 AND carbohydrates_g >= 0 AND fat_g >= 0",
            name="foods_check_macros",
        ),
        CheckConstraint(
            "calories_kcal <= 900 * reference_weight_g / 100",
            name="foods_check_calories_upper_bound",
        ),
        Index(
            "idx_foods_name",
            "name",
        ),
        Index(
            "idx_foods_brand",
            "brand",
        ),
        Index(
            "idx_foods_external_reference_id",
            "external_reference_id",
        ),
    )