import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from betterself.core.config import settings
from betterself.core.database import get_db
from betterself.core.exceptions import CatalogUnavailable, RecordNotFound
from betterself.models.food_models import FoodCategory
from betterself.schemas.food_schemas import (
    FoodCreate,
    FoodRead,
    FoodSearchRead,
    FoodSearchResult,
    FoodUpdate,
)
from betterself.repos.food_repo import FoodRepository
from betterself.repos.off_catalog_repo import OffCatalogRepository
from betterself.services.food_search_service import FoodSearchService
from betterself.core.dependencies import get_current_user
from betterself.models.user_models import User
from betterself.prefix import FOODS_URL


router = APIRouter(
    prefix=FOODS_URL,
    tags=["Foods"],
)

def get_food_service(
    session: Session = Depends(get_db),
) -> FoodRepository:
    return FoodRepository(session)

def get_off_catalog() -> OffCatalogRepository:
    return OffCatalogRepository(settings.off_catalog_path)


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
    service: FoodRepository = Depends(get_food_service),
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
    service: FoodRepository = Depends(get_food_service),
):
    return service.create_food(
        user=current_user,
        data=data,
    )


# Fonction pour rechercher à la fois dans les aliments et dans le catalogue Open Food
# Facts. Sans terme, retourne l'historique. Doit rester déclarée avant "/{food_id}".
@router.get("/search", response_model=FoodSearchRead)
def search_all_foods(
    query: str = Query(
        default="",
        max_length=255,
        description="Nom, marque ou code-barres.",
    ),
    limit: int = Query(default=20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    foods: FoodRepository = Depends(get_food_service),
    catalog: OffCatalogRepository = Depends(get_off_catalog),
):
    return FoodSearchService(foods, catalog).search(current_user, query, limit=limit)


# Retrouve l'aliment ou le produit Open Food Facts correspondant à un code-barres scanné
# (EAN-13, EAN-8, UPC-A). Un produit du catalogue n'est pas importé : le client
# l'importe s'il est choisi, comme pour la recherche.
@router.get(
    "/barcode/{code}",
    response_model=FoodSearchResult,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Code-barres inconnu."},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Catalogue indisponible."},
    },
)
def find_food_by_barcode(
    code: str = Path(pattern=r"^[0-9]{8,14}$", description="Code-barres de 8 à 14 chiffres."),
    current_user: User = Depends(get_current_user),
    foods: FoodRepository = Depends(get_food_service),
    catalog: OffCatalogRepository = Depends(get_off_catalog),
):
    try:
        result = FoodSearchService(foods, catalog).find_by_barcode(current_user, code)
    except CatalogUnavailable:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le catalogue Open Food Facts est indisponible pour le moment.",
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun aliment ne correspond à ce code-barres.",
        )
    return result


# Fonction pour importer un produit Open Food Facts dans les aliments.
# Retourne 201 si l'aliment est créé, 200 s'il avait déjà été importé.
@router.post(
    "/catalog/{code}/import",
    response_model=FoodRead,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_200_OK: {"model": FoodRead}},
)
def import_catalog_product(
    response: Response,
    code: str = Path(pattern=r"^[0-9]{1,24}$"),
    _current_user: User = Depends(get_current_user),
    service: FoodRepository = Depends(get_food_service),
    catalog: OffCatalogRepository = Depends(get_off_catalog),
):
    # Un produit déjà importé reste disponible même s'il a quitté le catalogue.
    food = service.get_by_external_reference(code)
    created = False

    if food is None:
        try:
            product = catalog.get(code)
        except CatalogUnavailable:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Le catalogue Open Food Facts est indisponible pour le moment.",
            )

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ce produit n'a pas été trouvé dans le catalogue.",
            )
        food, created = service.get_or_import_product(product)

    if not created:
        response.status_code = status.HTTP_200_OK
    return food


# Fonction pour récupérer un aliment par son identifiant
@router.get("/{food_id}", response_model=FoodRead)
def get_food(
    food_id: uuid.UUID,
    service: FoodRepository = Depends(get_food_service),
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
    service: FoodRepository = Depends(get_food_service),
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
    service: FoodRepository = Depends(get_food_service),
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