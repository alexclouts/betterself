import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from betterself.models.recipe_models import Recipe
from betterself.models.goal_models import NutritionGoal
from betterself.models.profile_models import UserProfile
from betterself.core.database import Base

""" 
On déclare le modèle User qui représente un utilisateur dans la base de données. 
Chaque utilisateur a un identifiant unique (UUID), un email, un mot de passe haché, 
un statut d'activité et une date de création.

C'est celle qui permet d'authentifier les utilisateurs dans l'application.
"""

# Génère un UUID unique pour chaque utilisateur
def generate_uuid() -> uuid.UUID:
    return uuid.uuid4()

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=generate_uuid,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        nullable=False,
        index=True,
    )

    pwd_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_date(),
        nullable=False,
    )

    # Relation vers le profil utilisateur associé. Un utilisateur peut avoir au maximum un profil.
    profile: Mapped["UserProfile | None"] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Relation vers l'objectif nutritionnel associé. Un utilisateur peut avoir au maximum un objectif.
    nutrition_goal: Mapped["NutritionGoal | None"] = relationship(
        "NutritionGoal",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Relation vers les recettes associées à l'utilisateur. Un utilisateur peut avoir plusieurs recettes.
    recipes: Mapped[list["Recipe"]] = relationship(
        "Recipe",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Relation vers les consommations alimentaires associées à l'utilisateur. Un utilisateur peut avoir plusieurs consommations.
    food_consumptions: Mapped[list["FoodConsumption"]] = relationship(
        "FoodConsumption",
        back_populates="user",
        cascade="all, delete-orphan",
    )