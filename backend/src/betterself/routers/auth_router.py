from fastapi import APIRouter, BackgroundTasks, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID

from betterself.repos.user_repo import UserRepository
from betterself.models.user_models import User
from betterself.core.database import get_db
from betterself.core.config import settings
from betterself.schemas.user_schemas import (
    MessageResponse,
    ResendVerificationRequest,
    UserCreate,
    VerifyEmailRequest,
)
from betterself.services.user_service import UserService
from betterself.core.security import create_access_token, verify_password
from betterself.schemas.user_schemas import Token
from betterself.prefix import AUTH_URL
from betterself.core.exceptions import DuplicateRecord, InvalidVerificationToken
from betterself.core.email import EmailSender, get_email_sender
from betterself.repos.email_verification_repo import EmailVerificationRepository
from betterself.services.email_verification_service import (
    EmailVerificationService,
    build_account_exists_email,
    send_email,
)

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


def get_email_verification_service(
    session: Session = Depends(get_db),
) -> EmailVerificationService:
    return EmailVerificationService(
        token_repository=EmailVerificationRepository(session),
        user_repository=UserRepository(session),
    )


# Message identique pour toutes les demandes qui envoient (peut-être) un courriel :
# la réponse ne révèle jamais si une adresse a déjà un compte.
CHECK_INBOX_MESSAGE = (
    "Si l'adresse est valide, un courriel vient de vous être envoyé. "
    "Consultez votre boîte de réception pour continuer."
)


# Endpoint pour l'enregistrement d'un nouvel utilisateur.
# Le compte est créé non vérifié et un lien de confirmation est envoyé par courriel.
# Si l'adresse a déjà un compte, rien n'est créé : son propriétaire reçoit plutôt un
# courriel l'en informant. Dans les deux cas, la réponse est la même.
@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
def register_user(
    user_create: UserCreate,
    background_tasks: BackgroundTasks,
    service: UserService = Depends(get_user_service),
    verification_service: EmailVerificationService = Depends(get_email_verification_service),
    email_sender: EmailSender = Depends(get_email_sender),
):
    # Une erreur de base de données passe par le gestionnaire de main.py, qui masque son détail.
    try:
        user = service.create_user(user_create)
        email = verification_service.issue(user)
    except DuplicateRecord:
        email = build_account_exists_email(user_create.email.lower())

    background_tasks.add_task(send_email, email_sender, email)
    return MessageResponse(message=CHECK_INBOX_MESSAGE)


# Endpoint pour confirmer l'adresse courriel avec le jeton reçu par courriel.
@router.post("/verify-email", response_model=MessageResponse)
def verify_email(
    payload: VerifyEmailRequest,
    verification_service: EmailVerificationService = Depends(get_email_verification_service),
):
    try:
        verification_service.verify(payload.token)
    except InvalidVerificationToken as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    return MessageResponse(message="Votre adresse courriel est confirmée. Vous pouvez vous connecter.")


# Endpoint pour recevoir un nouveau lien de vérification.
# La réponse est toujours la même, que l'adresse existe, soit déjà vérifiée ou non.
@router.post("/resend-verification", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
def resend_verification(
    payload: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    verification_service: EmailVerificationService = Depends(get_email_verification_service),
    email_sender: EmailSender = Depends(get_email_sender),
):
    email = verification_service.resend(payload.email)
    if email is not None:
        background_tasks.add_task(send_email, email_sender, email)
    return MessageResponse(message=CHECK_INBOX_MESSAGE)


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

    # Le mot de passe est correct, mais l'adresse n'est pas confirmée. Ce contrôle vient
    # après celui du mot de passe : il ne révèle rien à quelqu'un qui ne le connaît pas.
    if user.email_verified_at is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Veuillez confirmer votre adresse courriel avant de vous connecter.",
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