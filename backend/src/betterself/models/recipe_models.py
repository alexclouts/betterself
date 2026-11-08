import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from betterself.core.database import Base

"""
Recette créée par un utilisateur.

Une recette est un assemblage d'aliments. Elle n'est pas traitée
comme un aliment : ses valeurs nutritionnelles sont calculées à partir
de sa composition au moment où elle est ajoutée au journal alimentaire.
"""

class Recipe(Base):

    __tablename__ = "recipes"

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

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    total_weight_g: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    servings: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
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

    # Attribut Python permettant de naviguer entre les recettes et l'utilisateur à qui elle appartient.
    # back_populates relie cet attribut à user.recipes
    user = relationship(
        "User",
        back_populates="recipes",
    )

    # Attribut Python permettant de naviguer entre les recettes et leurs ingrédients
    ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeIngredient.created_at",
    )

    # Attribut Python permettant de naviguer entre les recettes et leurs consommations alimentaires
    food_consumptions = relationship(
        "FoodConsumption",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )

    
    __table_args__ = (
        # Vérifie que le poids total de la recette est positif
        CheckConstraint(
            "total_weight_g > 0",
            name="recipes_check_total_weight",
        ),
        # Vérifie que le nombre de portions est positif si renseigné
        CheckConstraint(
            "servings IS NULL OR servings > 0",
            name="recipes_check_servings",
        ),
        # Index pour accélérer les requêtes filtrant par utilisateur et date de création
        Index(
            "idx_recipes_user_created_at",
            "user_id",
            "created_at",
        ),
        # Index pour accélérer les requêtes filtrant par utilisateur et statut archivé
        Index(
            "idx_recipes_user_archived",
            "user_id",
            "is_archived",
        )
    )


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