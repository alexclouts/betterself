import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from betterself.models.user_models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    # Récupère un utilisateur par son email. Retourne None si l'utilisateur n'existe pas.
    def get_by_email(self, email: str) -> User | None:
        query = select(User).where(
            User.email == email.lower(),
        )
        return self.db.scalar(query)


    # Récupère un utilisateur par son ID. Retourne None si l'utilisateur n'existe pas.
    def get_by_id(self,user_id: uuid.UUID) -> User | None:
        return self.db.get(User, user_id)


    # Ajoute un nouvel utilisateur à la base de données.
    def add(self,user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user


    # Vérifie si un utilisateur existe par son email.
    def exists_by_email(self,email: str) -> bool:
        return self.get_by_email(email) is not None