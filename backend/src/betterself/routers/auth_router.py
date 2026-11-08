from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID

from betterself.repos.user_repo import UserRepository
from betterself.models.user_models import User
from betterself.core.database import get_db
from betterself.core.config import settings
from betterself.schemas.user_schemas import UserCreate, UserRead
from betterself.services.user_service import UserService
from betterself.core.security import create_access_token, verify_password
from betterself.schemas.user_schemas import Token
from betterself.prefix import AUTH_URL

from jose import JWTError, jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{AUTH_URL}/login")

router = APIRouter(
    prefix=AUTH_URL, 
    tags=["Authentication"]
)

def get_user_service(
    session: Session = Depends(get_db),
) -> UserService:
    return UserService(
        user_repository=UserRepository(session),
    )


# Endpoint pour l'enregistrement d'un nouvel utilisateur
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    user_create: UserCreate, 
    service: UserService = Depends(get_user_service),
):
    try:
        return service.create_user(user_create)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Endpoint pour la connexion d'un utilisateur
@router.post("/login", response_model=Token)
def login_user(
    form_data: OAuth2PasswordRequestForm=Depends(), 
    service: UserService = Depends(get_user_service)
):
    # Récupère l'utilisateur par son email et vérifie le mot de passe
    user = service.get_user_by_email(form_data.username)

    # Vérifie si l'utilisateur existe et si le mot de passe est correct
    if not user or not verify_password(form_data.password, user.pwd_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Les informations entrées sont invalides.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crée un jeton d'accès pour l'utilisateur et le retourne
    access_token = create_access_token(subject=str(user.id))
    return Token(access_token=access_token)


# Fonction utilitaire pour récupérer l'utilisateur actuellement connecté à partir du jeton d'accès
def read_current_user(
        token: str = Depends(oauth2_scheme), 
        service: UserService = Depends(get_user_service),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les informations d'identification.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = service.get_user_by_id(UUID(user_id))
    if user is None:
        raise credentials_exception
    return user