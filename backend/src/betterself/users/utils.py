import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from betterself.core.config import settings
from betterself.core.database import get_db
from betterself.users.models import User

# Schéma d'authentification utilisé par FastAPI pour extraire le token JWT
# envoyé dans l'en-tête Authorization: Bearer <token>.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Dépendance FastAPI pour récupérer l'utilisateur authentifié
def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_db),
) -> User:
    """
    Retourne l'utilisateur authentifié à partir du token JWT fourni.

    Le token est créé par la fonction create_access_token() de
    betterself.core.security. L'identifiant de l'utilisateur est conservé
    dans le claim `sub`.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Décode le token avec la même clé et le même algorithme que ceux
        # utilisés lors de sa création.
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

    # Récupère l'utilisateur à partir de l'identifiant contenu dans le token.
    user = session.get(User, user_id)

    if user is None:
        raise credentials_exception

    return user