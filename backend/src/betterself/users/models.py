import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func, Uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

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
        server_default=func.now(),
        nullable=False,
    )