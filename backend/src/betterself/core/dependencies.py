import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from betterself.repos.user_repo import UserRepository
from betterself.core.config import settings
from betterself.core.database import get_db
from betterself.models.user_models import User
from betterself.services.user_service import UserService


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)

# Fournit une instance de UserService avec la dépendance de la base de données.
def get_user_service(
    db: Session = Depends(get_db),
) -> UserService:
    return UserService(
        user_repository=UserRepository(db),
    )


# Récupère l'utilisateur actuellement authentifié à partir du token. Lève une exception HTTP 401 si le token est invalide ou si l'utilisateur n'existe pas.
def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les informations d'identification.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Décode le token JWT et récupère l'ID de l'utilisateur.
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = uuid.UUID(user_id)
    except (JWTError, ValueError):
        raise credentials_exception

    user = user_service.get_user_by_id(user_id)

    if user is None:
        raise credentials_exception

    return user