import uuid

from betterself.core.exceptions import DuplicateRecord
from betterself.core.security import hash_password
from betterself.models.user_models import User
from betterself.repos.user_repo import UserRepository
from betterself.schemas.user_schemas import UserCreate


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
    ):
        self.user_repository = user_repository


    # Récupère un utilisateur par son email. Retourne None si l'utilisateur n'existe pas.
    def get_user_by_email(
        self,
        email: str,
    ) -> User | None:
        return self.user_repository.get_by_email(email)


    # Récupère un utilisateur par son ID. Retourne None si l'utilisateur n'existe pas.
    def get_user_by_id(
        self,
        user_id: uuid.UUID,
    ) -> User | None:
        return self.user_repository.get_by_id(user_id)


    # Crée un nouvel utilisateur.
    # Lève une exception DuplicateRecord si un utilisateur avec le même email existe déjà.
    def create_user(
        self,
        data: UserCreate,
    ) -> User:
        email = data.email.lower()

        if self.user_repository.exists_by_email(email):
            raise DuplicateRecord(
                "Les informations entrées sont invalides."
            )

        user = User(
            email=email,
            pwd_hash=hash_password(data.password),
        )
        return self.user_repository.add(user)