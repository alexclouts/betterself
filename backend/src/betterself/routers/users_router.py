from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from betterself.schemas.onboarding_schemas import OnboardingStatusRead
from betterself.schemas.user_schemas import UserRead
from betterself.services.onboarding_service import OnboardingService
from betterself.core.database import get_db
from betterself.core.exceptions import RecordNotFound
from betterself.core.dependencies import get_current_user
from betterself.models.user_models import User
from betterself.schemas.profile_schemas import UserProfileRead, UserProfileUpdate
from betterself.repos.profile_repo import UserProfileRepository
from betterself.prefix import USERS_URL

router = APIRouter(
    prefix=USERS_URL,
    tags=["Users"],
)

def get_onboarding_service(
    session: Session = Depends(get_db),
) -> OnboardingService:
    return OnboardingService(session)

    
# Endpoint pour récupérer les informations de l'utilisateur actuellement connecté
@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/me/onboarding-status", response_model=OnboardingStatusRead)
def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    service: OnboardingService = Depends(get_onboarding_service),
) -> OnboardingStatusRead:
    return service.get_status(current_user)

def get_user_profile_repository(
    db: Session = Depends(get_db),
) -> UserProfileRepository:
    return UserProfileRepository(db)


# Fonction pour récupérer le profil de l'utilisateur connecté
@router.get(
    "/me/profile",
    response_model=UserProfileRead,
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    service: UserProfileRepository = Depends(get_user_profile_repository),
):
    try:
        return service.get_profile_or_404(current_user)
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun profil utilisateur n'a été trouvé.",
        )


# Fonction pour créer ou mettre à jour le profil de l'utilisateur connecté
@router.put(
    "/me/profile",
    response_model=UserProfileRead,
)
def create_or_update_current_user_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    service: UserProfileRepository = Depends(get_user_profile_repository),
):
    profile, created = service.create_or_update_profile(
        user=current_user,
        data=data,
    )

    if created:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=UserProfileRead.model_validate(profile).model_dump(mode="json"),
        )
    return profile