from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from betterself.core.database import get_db
from betterself.core.exceptions import RecordNotFound
from betterself.users.utils import get_current_user
from betterself.users.models import User
from betterself.profile.schemas import UserProfileRead, UserProfileUpdate
from betterself.profile.service import UserProfileService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def get_user_profile_service(
    db: Session = Depends(get_db),
) -> UserProfileService:
    return UserProfileService(db)


# Fonction pour récupérer le profil de l'utilisateur connecté
@router.get(
    "/me/profile",
    response_model=UserProfileRead,
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    service: UserProfileService = Depends(get_user_profile_service),
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
    service: UserProfileService = Depends(get_user_profile_service),
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