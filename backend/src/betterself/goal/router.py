from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from betterself.core.database import get_db
from betterself.core.exceptions import RecordNotFound
from betterself.goal.schemas import (
    NutritionGoalCreate,
    NutritionGoalRead,
)
from betterself.goal.service import (
    NutritionGoalAlreadyExistsError,
    GoalService)
from betterself.users.models import User
from betterself.users.utils import get_current_user

router = APIRouter(
    prefix="/nutrition-goals",
    tags=["Nutrition goals"],
)


@router.post(
    "",
    response_model=NutritionGoalRead,
    status_code=status.HTTP_201_CREATED,
)
def create_nutrition_goal(
    payload: NutritionGoalCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NutritionGoalRead:
    """
    Crée l'objectif nutritionnel de l'utilisateur durant le onboarding.

    Un utilisateur ne peut posséder qu'un seul objectif. Si un objectif existe
    déjà, la requête retourne une erreur 409 Conflict.
    """
    service = GoalService(session)

    try:
        return service.create_goal(
            user=current_user,
            data=payload,
        )
    except NutritionGoalAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="L'utilisateur possède déjà un objectif nutritionnel.",
        )


@router.get(
    "/current",
    response_model=NutritionGoalRead,
)
def get_nutritional_goal(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NutritionGoalRead:
    """
    Retourne l'objectif nutritionnel de l'utilisateur connecté.

    Cette route est utilisée notamment pour vérifier que l'utilisateur a
    complété l'étape de onboarding.
    """
    service = GoalService(session)

    try:
        return service.get_goal_or_404(user=current_user)
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun objectif nutritionnel n'a été trouvé.",
        )


@router.patch(
    "/current",
    response_model=NutritionGoalRead,
)
def update_nutrition_goal(
    payload: NutritionGoalCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NutritionGoalRead:
    """
    Met à jour l'objectif nutritionnel existant de l'utilisateur.

    L'utilisateur ne peut pas créer un second objectif : il modifie celui
    créé durant le onboarding.
    """
    service = GoalService(session)

    try:
        return service.update_goal(
            user=current_user,
            data=payload,
        )
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun objectif nutritionnel n'a été trouvé.",
        )