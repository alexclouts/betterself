from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID



from betterself.users.models import User
from betterself.core.database import get_db
from betterself.core.config import settings
from betterself.users.schemas import UserCreate, UserRead
from betterself.users.service import UserService
from betterself.core.security import create_access_token, verify_password
from betterself.users.schemas import Token

from jose import JWTError, jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Endpoint pour l'enregistrement d'un nouvel utilisateur
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_create: UserCreate, db: Session=Depends(get_db)):
    service = UserService(db)
    return service.create_user(user_create)


# Endpoint pour la connexion d'un utilisateur
@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm=Depends(), db: Session=Depends(get_db)):
    # Récupère l'utilisateur par son email et vérifie le mot de passe
    service = UserService(db)
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
def read_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
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

    user = UserService(db).get_user_by_id(UUID(user_id))
    if user is None:
        raise credentials_exception
    return user


# Endpoint pour récupérer les informations de l'utilisateur actuellement connecté
@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(read_current_user)) -> User:
    return current_user