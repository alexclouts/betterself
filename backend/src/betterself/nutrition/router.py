from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from betterself.core.exceptions import RecordNotFound
from betterself.core.database import get_db
from betterself.nutrition.schemas import (
    NutritionGoalCreate,
    NutritionGoalRead,
)
from betterself.nutrition.service import NutritionService
from betterself.users.models import User
from betterself.users.router import read_current_user

router = APIRouter(
    prefix="/nutrition-goal",
    tags=["Nutrition goal"],
)

def get_nutrition_service(db: Session = Depends(get_db)) -> NutritionService:
    return NutritionService(db)

# Endpoint pour créer un nouvel objectif nutritionnel
@router.post("", response_model=NutritionGoalRead, status_code=status.HTTP_201_CREATED)
def create_nutrition_goal(
    data: NutritionGoalCreate,
    current_user: User = Depends(read_current_user),
    service: NutritionService = Depends(get_nutrition_service),
) -> NutritionGoalRead:
    return service.create_goal(
        user=current_user,
        data=data
    )

# Endpoint pour récupérer un objectif nutritionnel spécifique par ID pour l'utilisateur courant
@router.get("/{goal_id}",response_model=NutritionGoalRead,status_code=status.HTTP_200_OK)
def get_nutrition_goal(
    goal_id: int,
    current_user: User = Depends(read_current_user),
    service: NutritionService = Depends(get_nutrition_service),
) -> NutritionGoalRead:
    try:
        goal = service.get_goal_by_id(user=current_user, goal_id=goal_id)
    # On catch l'exception générée par le service lorsqu'un objectif n'est pas trouvé
    except RecordNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objectif introuvable.")
    return goal


