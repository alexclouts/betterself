import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from betterself.core.database import Base



"""
Aliment associé à une recette, avec la quantité utilisée.
La quantité est exprimée en grammes du produit tel que consommé ou utilisé dans la recette. 
Les valeurs nutritionnelles ne sont pas dupliquées ici : elles sont lues depuis `foods` lors du calcul.
"""
class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    recipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    )

    food_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("foods.id", ondelete="RESTRICT"),
        nullable=False,
    )

    quantity_g: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
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

    # Attribut Python permettant de naviguer entre un ingrédient de recette et sa recette
    # recipe_ingredient.recipe = recipe : ajout de l'ingrédient à recipe.ingredients
    # back_populates relie cet attribut à Recipe.ingredients
    recipe = relationship(
        "Recipe",
        back_populates="ingredients",
    )

    # Attribut Python permettant de naviguer entre un ingrédient de recette et son aliment
    # Un aliment n'a aucun ingrédient, donc pas de back_populates nécessaire
    food = relationship(
        "Food"
    )

    __table_args__ = (
        # Vérifie que la quantité de l'ingrédient est positive
        CheckConstraint(
            "quantity_g > 0",
            name="recipe_ingredients_check_quantity",
        ),
        # Vérifie que la combinaison recette-aliment est unique
        UniqueConstraint(
            "recipe_id",
            "food_id",
            name="uq_recipe_ingredient_food",
        ),
        # Index pour accélérer les requêtes filtrant par un ID d'aliment
        Index(
            "idx_recipe_ingredients_food",
            "food_id",
        )
    )