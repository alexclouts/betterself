from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from betterself.schemas.target_schemas import GoalTargetCalculationInput, GoalTargetRead
from betterself.services.goal_service import GoalService
from betterself.core.database import get_db
from betterself.core.exceptions import RecordNotFound
from betterself.schemas.goal_schemas import (
    NutritionGoalCreate,
    NutritionGoalRead,
)
from betterself.services.goal_service import GoalService, GoalTargetCalculationError
from betterself.services.goal_service import NutritionGoalAlreadyExistsError
from betterself.models.user_models import User
from betterself.core.dependencies import get_current_user
from betterself.repos.goal_repo import GoalRepository
from betterself.repos.target_repo import TargetRepository
from betterself.prefix import NUTRITION_GOAL_URL, TARGET_URL

router = APIRouter(
    prefix=NUTRITION_GOAL_URL,
    tags=["Nutrition goal"],
)


def get_goal_service(
    session: Session = Depends(get_db),
) -> GoalService:
    return GoalService(
        goal_repository=GoalRepository(session),
        target_repository=TargetRepository(session),
    )


"""
Crée l'objectif nutritionnel de l'utilisateur durant le onboarding.
Un utilisateur ne peut posséder qu'un seul objectif. Si un objectif existe déjà, la requête retourne une erreur 409 Conflict.
"""
@router.post("", response_model=NutritionGoalRead, status_code=status.HTTP_201_CREATED)
def create_nutrition_goal(
    payload: NutritionGoalCreate,
    service: GoalService = Depends(get_goal_service),
    current_user: User = Depends(get_current_user),
) -> NutritionGoalRead:
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


"""
Retourne l'objectif nutritionnel de l'utilisateur connecté.
Cette route est utilisée notamment pour vérifier que l'utilisateur a complété l'étape de onboarding.
"""
@router.get("/current", response_model=NutritionGoalRead)
def get_nutritional_goal(
    service: GoalService = Depends(get_goal_service),
    current_user: User = Depends(get_current_user),
) -> NutritionGoalRead:
    try:
        return service.get_goal_or_404(user=current_user)
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun objectif nutritionnel n'a été trouvé.",
        )


"""
Met à jour l'objectif nutritionnel existant de l'utilisateur.
L'utilisateur ne peut pas créer un second objectif : il modifie celui créé durant le onboarding.
"""
@router.patch("/current", response_model=NutritionGoalRead)
def update_nutrition_goal(
    payload: NutritionGoalCreate,
    service: GoalService = Depends(get_goal_service),
    current_user: User = Depends(get_current_user),
) -> NutritionGoalRead:
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


"""
Retourne la cible nutritionnelle active de l'utilisateur.
Cette cible contient notamment les calories et macronutriments à consommer pour la période courante.
"""
@router.get(TARGET_URL, response_model=GoalTargetRead)
def get_current_goal_target(
    service: GoalService = Depends(get_goal_service),
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
@router.post(f"{TARGET_URL}/recalculate", response_model=GoalTargetRead, status_code=status.HTTP_201_CREATED)
def recalculate_current_goal_target(
    payload: GoalTargetCalculationInput,
    service: GoalService = Depends(get_goal_service),
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