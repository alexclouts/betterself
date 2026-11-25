from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from betterself.schemas.user_schemas import UserRead
from betterself.services.onboarding_service import OnboardingService
from betterself.core.database import get_db
from betterself.core.exceptions import RecordNotFound
from betterself.core.dependencies import get_current_user
from betterself.models.user_models import User
from betterself.schemas.profile_schemas import UserProfileRead, UserProfileUpdate, UserProfileUpdatedRead
from betterself.repos.profile_repo import UserProfileRepository
from betterself.prefix import USERS_URL, PROFILE_URL
from betterself.models.profile_models import UserProfile
from betterself.services.target_refresh import refresh_active_target
from decimal import Decimal

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


def get_user_profile_repository(
    db: Session = Depends(get_db),
) -> UserProfileRepository:
    return UserProfileRepository(db)


# Fonction pour récupérer le profil de l'utilisateur connecté
@router.get(
    PROFILE_URL,
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


# Champs du profil utilisés par le calcul de la cible nutritionnelle.
# Decimal(str(...)) : 180 et 180.00 doivent être considérés égaux.
def _target_inputs(profile: UserProfile) -> tuple:
    return (
        profile.sex,
        profile.year_of_birth,
        Decimal(str(profile.height_cm)),
        profile.activity_level,
    )


# Fonction pour créer ou mettre à jour le profil de l'utilisateur connecté
@router.put(PROFILE_URL, response_model=UserProfileUpdatedRead)
def create_or_update_current_user_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    service: UserProfileRepository = Depends(get_user_profile_repository),
    db: Session = Depends(get_db),
):
    # Le repository ne retourne que le profil : on détermine avant l'appel
    # s'il s'agit d'une création (201) ou d'une mise à jour (200).
    existing = service.get_by_user(current_user)
    created = existing is None
    previous = _target_inputs(existing) if existing is not None else None

    profile = service.create_or_update_profile(
        user=current_user,
        data=data
    )

    # Recalcule la cible seulement si un champ utilisé par le calcul a changé
    # (le prénom, par exemple, n'a aucun effet).
    target_update = None
    if previous is not None and previous != _target_inputs(profile):
        target_update = refresh_active_target(db, current_user)

    response = UserProfileUpdatedRead.model_validate(profile).model_copy(
        update={"target_update": target_update}
    )
    if created:
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=response.model_dump(mode="json"),
        )
    return response