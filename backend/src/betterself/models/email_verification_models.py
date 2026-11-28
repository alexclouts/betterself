import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from betterself.core.database import Base

"""
Jeton de vérification de l'adresse courriel.

Le jeton envoyé par courriel n'est jamais conservé en clair : on garde seulement
son hash SHA-256. Une fuite de la base de données ne permet donc pas de valider
des comptes. Un jeton sert une seule fois (used_at) et expire (expires_at).
"""

class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    # La suppression d'un utilisateur supprime aussi ses jetons.
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Hash SHA-256 en hexadécimal : toujours 64 caractères.
    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Rempli quand le jeton est utilisé ou annulé (par exemple lors d'un renvoi).
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
