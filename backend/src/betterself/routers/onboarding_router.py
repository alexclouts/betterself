from betterself.core.database import get_db
from betterself.core.dependencies import get_current_user
from betterself.models.user_models import User
from betterself.services.goal_service import GoalService
from betterself.services.onboarding_service import OnboardingService
from betterself.prefix import ONBOARDING_URL
from betterself.routers.users_router import get_onboarding_service
from fastapi import APIRouter, Depends, status
from betterself.schemas.onboarding_schemas import OnboardingCreate, OnboardingStatusRead

router = APIRouter(prefix=ONBOARDING_URL, tags=["Onboarding"])


# Endpoint pour récupérer le statut de Onboarding de l'utilisateur connecté
@router.get("/status", response_model=OnboardingStatusRead)
def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    service: OnboardingService = Depends(get_onboarding_service),
) -> OnboardingStatusRead:
    return service.get_status(current_user)


# Endpoint pour compléter le processus de Onboarding de l'utilisateur connecté
@router.post("", status_code=status.HTTP_201_CREATED)
def complete_onboarding(
    onboarding_data: OnboardingCreate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    service = OnboardingService(db)

    payload = {
        "name": onboarding_data.name,
        "birthYear": onboarding_data.birth_year,
        "sex": onboarding_data.sex,
        "goal": onboarding_data.goal,
        "heightCm": onboarding_data.height_cm,
        "weightKg": onboarding_data.weight_kg,
        "activityLevel": onboarding_data.activity_level,
    }
    service.save_onboarding(current_user, payload)

    return {"status": "onboarding_completed"}