from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from betterself.core.security import hash_password
from betterself.users.models import User
from betterself.users.schemas import UserCreate

"""
Le service User est responsable de la logique métier liée aux utilisateurs. Il interagit avec la base de données pour créer et récupérer des utilisateurs.

"""
class UserService:
    def __init__(self, db: Session):
        self.db = db

    # Récupère un utilisateur par son email
    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email.lower()).first()

    # Récupère un utilisateur par son ID
    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_create: UserCreate) -> User:
        # Vérifie si l'utilisateur existe déjà
        existing_user = self.get_user_by_email(user_create.email)

        if existing_user:
            # On lève une exception HTTP 400 si l'utilisateur existe déjà
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Les informations entrées sont invalides.",
            )

        # Hache le mot de passe avant de le stocker
        hashed_password = hash_password(user_create.password)

        # Crée un nouvel utilisateur
        new_user = User(email=user_create.email, pwd_hash=hashed_password)

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user