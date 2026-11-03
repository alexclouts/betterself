import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from betterself.core.database import get_db
from betterself.core.exceptions import RecordNotFound
from betterself.foods.models import FoodCategory
from betterself.foods.schemas import FoodCreate, FoodRead, FoodUpdate
from betterself.foods.service import FoodService
from betterself.users.utils import get_current_user
from betterself.users.models import User


router = APIRouter(
    prefix="/foods",
    tags=["Foods"],
)

def get_food_service(
    session: Session = Depends(get_db),
) -> FoodService:
    return FoodService(session)


# Fonction pour rechercher des aliments
@router.get("", response_model=list[FoodRead])
def search_foods(
    query: str | None = Query(
        default=None,
        max_length=255,
        description="Terme recherché dans le nom, la marque ou la référence externe.",
    ),
    category: FoodCategory | None = Query(
        default=None,
        description="Catégorie alimentaire.",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Nombre maximal de résultats à retourner.",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Nombre de résultats à ignorer avant de retourner la page.",
    ),
    service: FoodService = Depends(get_food_service),
):

    return service.search_foods(
        query=query,
        category=category,
        limit=limit,
        offset=offset,
    )


# Fonction pour créer un aliment manuellement
@router.post("", response_model=FoodRead, status_code=status.HTTP_201_CREATED)
def create_food(
    data: FoodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: FoodService = Depends(get_food_service),
):
    return service.create_food(
        user=current_user,
        data=data,
    )


# Fonction pour récupérer un aliment par son identifiant
@router.get(
    "/{food_id}",
    response_model=FoodRead,
)
def get_food(
    food_id: uuid.UUID,
    service: FoodService = Depends(get_food_service),
):
    try:
        return service.get_food_or_404(food_id)
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun aliment n'a été trouvé.",
        )


# Fonction pour modifier un aliment manuel
@router.patch(
    "/{food_id}",
    response_model=FoodRead,
)
def update_food(
    food_id: uuid.UUID,
    data: FoodUpdate,
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    try:
        return service.update_food(
            user=current_user,
            food_id=food_id,
            data=data,
        )
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun aliment n'a été trouvé.",
        )
    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )


# Fonction pour supprimer un aliment manuel
@router.delete(
    "/{food_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_food(
    food_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: FoodService = Depends(get_food_service),
):
    try:
        service.delete_food(
            user=current_user,
            food_id=food_id,
        )
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun aliment n'a été trouvé.",
        )
    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)