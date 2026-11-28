import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from betterself.models.email_verification_models import EmailVerificationToken


class EmailVerificationRepository:
    def __init__(self, db: Session):
        self.db = db


    # Ajoute un nouveau jeton à la base de données.
    def add(self, token: EmailVerificationToken) -> EmailVerificationToken:
        self.db.add(token)
        self.db.flush()
        return token


    # Récupère un jeton par son hash. Retourne None si le jeton n'existe pas.
    def get_by_hash(self, token_hash: str) -> EmailVerificationToken | None:
        query = select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash,
        )
        return self.db.scalar(query)


    # Récupère le jeton le plus récent d'un utilisateur, utilisé ou non.
    def get_latest_for_user(self, user_id: uuid.UUID) -> EmailVerificationToken | None:
        query = (
            select(EmailVerificationToken)
            .where(EmailVerificationToken.user_id == user_id)
            .order_by(EmailVerificationToken.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(query)


    # Annule les jetons encore valides d'un utilisateur : seul le dernier lien envoyé fonctionne.
    def invalidate_for_user(self, user_id: uuid.UUID, now: datetime) -> None:
        self.db.execute(
            update(EmailVerificationToken)
            .where(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.used_at.is_(None),
            )
            .values(used_at=now)
        )
