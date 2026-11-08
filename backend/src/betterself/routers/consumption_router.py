import uuid
from datetime import date, datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from betterself.routers.auth_router import read_current_user
from betterself.core.database import get_db
from betterself.core.exceptions import RecordNotFound
from betterself.schemas.consumption_schemas import (
    DailyNutritionSummaryRead,
    FoodConsumptionCreate,
    FoodConsumptionRead,
    FoodConsumptionUpdate,
)
from betterself.core.dependencies import get_current_user
from betterself.services.consumption_service import FoodConsumptionService
from betterself.models.user_models import User
from betterself.prefix import CONSUMPTIONS_URL


router = APIRouter(
    prefix=CONSUMPTIONS_URL,
    tags=["Food Consumptions"],
)


"""
Construit le service des consommations alimentaires.
"""
def get_food_consumption_service(
    db: Session = Depends(get_db),
) -> FoodConsumptionService:
    return FoodConsumptionService(db)


"""
Ajoute une consommation au journal alimentaire.
Fournir soit `food_id`, soit `recipe_id`, mais pas les deux.
"""
@router.post("", response_model=FoodConsumptionRead, status_code=status.HTTP_201_CREATED)
def create_food_consumption(
    data: FoodConsumptionCreate,
    current_user: User = Depends(get_current_user),
    consumption_service: FoodConsumptionService = Depends(get_food_consumption_service),

):
    try:
        return consumption_service.create_consumption(
            user=current_user,
            data=data,
        )
    except RecordNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )


"""
Retourne les consommations de l'utilisateur authentifié.
"""
@router.get("", response_model=list[FoodConsumptionRead])
def list_food_consumptions(
    start_date: datetime | None = Query(
        default=None,
        description="Date et heure de début.",
    ),
    end_date: datetime | None = Query(
        default=None,
        description="Date et heure de fin.",
    ),
    meal_type: str | None = Query(
        default=None,
        description="Type de repas : breakfast, lunch, dinner ou snack.",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    current_user: User = Depends(get_current_user),
    consumption_service: FoodConsumptionService = Depends(
        get_food_consumption_service,
    ),
):
    return consumption_service.list_consumptions(
        user=current_user,
        start_date=start_date,
        end_date=end_date,
        meal_type=meal_type,
        limit=limit,
        offset=offset,
    )

"""
Retourne les calories et macronutriments consommés
par l'utilisateur pour une journée donnée.
"""
@router.get("/summary", response_model=DailyNutritionSummaryRead, status_code=200)
def get_daily_summary(
    date: date = Query(
        ...,
        description="Date du résumé nutritionnel, au format YYYY-MM-DD.",
    ),
    current_user: User = Depends(read_current_user),
    service: FoodConsumptionService = Depends(get_food_consumption_service),
) -> DailyNutritionSummaryRead:

    return service.get_daily_summary(
        user=current_user,
        summary_date=date,
    )

"""
Retourne une consommation précise du journal.
 """
@router.get("/{consumption_id}", response_model=FoodConsumptionRead)
def get_food_consumption(
    consumption_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    consumption_service: FoodConsumptionService = Depends(
        get_food_consumption_service,
    ),
):
    try:
        return consumption_service._get_consumption_or_404(
            user=current_user,
            consumption_id=consumption_id,
        )
    except RecordNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


"""
Met à jour une consommation.
Si la quantité change, l'instantané nutritionnel est recalculé.
"""
@router.patch("/{consumption_id}", response_model=FoodConsumptionRead)
def update_food_consumption(
    consumption_id: uuid.UUID,
    data: FoodConsumptionUpdate,
    current_user: User = Depends(get_current_user),
    consumption_service: FoodConsumptionService = Depends(
        get_food_consumption_service,
    )
):
    try:
        return consumption_service.update_consumption(
            user=current_user,
            consumption_id=consumption_id,
            data=data,
        )
    except RecordNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )


"""
Supprime une consommation du journal.
"""
@router.delete("/{consumption_id}", status_code=status.HTTP_204_NO_CONTENT,)
def delete_food_consumption(
    consumption_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    consumption_service: FoodConsumptionService = Depends(
        get_food_consumption_service,
    ),
):
    try:
        consumption_service.delete_consumption(
            user=current_user,
            consumption_id=consumption_id,
        )
    except RecordNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
