from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from betterself.core.database import get_db
from betterself.core.exceptions import RecordNotFound
from betterself.targets.schemas import (
    GoalTargetRead,
    GoalTargetRecalculate,
)
from betterself.targets.service import (
    GoalTargetCalculationError,
    TargetService,
)
from betterself.users.models import User
from betterself.users.utils import get_current_user

router = APIRouter(
    prefix="/nutrition-goal/current/target",
    tags=["Nutrition goal targets"],
)


def get_target_service(
    session: Session = Depends(get_db),
) -> TargetService:
    return TargetService(session)


"""
Retourne la cible nutritionnelle active de l'utilisateur.
Cette cible contient notamment les calories et macronutriments à consommer pour la période courante.
"""
@router.get("", response_model=GoalTargetRead)
def get_current_goal_target(
    service: TargetService = Depends(get_target_service),
    current_user: User = Depends(get_current_user),
) -> GoalTargetRead:
    try:
        return service.get_active_goal_target(current_user)
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune cible nutritionnelle active n'a été trouvée.",
        )


"""
Recalcule la cible nutritionnelle active à partir d'un nouveau poids.
La cible précédente est fermée et conservée dans l'historique. La nouvelle cible devient la seule cible active de l'utilisateur.
"""
@router.post("/recalculate", response_model=GoalTargetRead, status_code=status.HTTP_201_CREATED)
def recalculate_current_goal_target(
    payload: GoalTargetRecalculate,
    service: TargetService = Depends(get_target_service),
    current_user: User = Depends(get_current_user),
) -> GoalTargetRead:
    try:
        return service.recalculate_goal_target(
            user=current_user,
            data=payload,
        )
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun objectif nutritionnel n'a été trouvé.",
        )
    except GoalTargetCalculationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )