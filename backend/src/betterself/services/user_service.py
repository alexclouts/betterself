import uuid

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


    # Inscrit un utilisateur. Retourne (utilisateur, True) si le compte est créé, ou
    # (compte existant, False) si l'adresse a déjà un compte. Ne lève pas d'erreur pour
    # un doublon : le routeur répond la même chose dans les deux cas.
    #
    # Si le compte existant n'est pas encore vérifié, la dernière inscription remplace
    # son mot de passe. Quelqu'un qui aurait inscrit l'adresse d'une autre personne
    # ne garde donc pas le contrôle du compte : la vraie propriétaire se réinscrit,
    # et la confirmation exige le mot de passe qu'elle vient de choisir.
    def register(
        self,
        data: UserCreate,
    ) -> tuple[User, bool]:
        email = data.email.lower()
        # Le hachage se fait dans tous les cas : la réponse prend le même temps,
        # que l'adresse ait déjà un compte ou non.
        pwd_hash = hash_password(data.password)

        # Le verrou évite que deux inscriptions simultanées de la même adresse
        # envoient chacune un courriel.
        existing = self.user_repository.get_by_email_for_update(email)
        if existing is not None:
            if existing.email_verified_at is None:
                existing.pwd_hash = pwd_hash
            return existing, False

        user = User(
            email=email,
            pwd_hash=pwd_hash,
        )
        return self.user_repository.add(user), True
