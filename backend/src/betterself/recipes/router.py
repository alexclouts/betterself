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
from betterself.recipes.schemas import (
    RecipeArchiveUpdate,
    RecipeCreate,
    RecipeRead,
    RecipeUpdate,
)
from betterself.recipes.service import RecipeService
from betterself.users.utils import get_current_user
from betterself.users.models import User


router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)


# Dépendance pour construire le service de recettes à partir de la session
def get_recipe_service(
    db: Session = Depends(get_db),
) -> RecipeService:
    return RecipeService(db)


# Fonction pour lister les recettes de l'utilisateur connecté
@router.get("",response_model=list[RecipeRead])
def list_recipes(
    include_archived: bool = Query(
        default=False,
        description="Inclure les recettes archivées.",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Nombre maximal de recettes à retourner.",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Nombre de recettes à ignorer avant de retourner la page.",
    ),
    current_user: User = Depends(get_current_user),
    recipe_service: RecipeService = Depends(get_recipe_service),
):
    return recipe_service.list_recipes(
        user=current_user,
        include_archived=include_archived,
        limit=limit,
        offset=offset,
    )


# Fonction pour créer une recette
@router.post("", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
def create_recipe(
    data: RecipeCreate,
    current_user: User = Depends(get_current_user),
    recipe_service: RecipeService = Depends(get_recipe_service),
):
    return recipe_service.create_recipe(
        user=current_user,
        data=data,
    )


# Fonction pour récupérer une recette par son identifiant
@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(
    recipe_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    recipe_service: RecipeService = Depends(get_recipe_service),
):
    try:
        return recipe_service.get_recipe_or_404(
            user=current_user,
            recipe_id=recipe_id,
        )
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune recette n'a été trouvée.",
        )


# Fonction pour mettre à jour une recette
@router.patch("/{recipe_id}", response_model=RecipeRead)
def update_recipe(
    recipe_id: uuid.UUID,
    data: RecipeUpdate,
    current_user: User = Depends(get_current_user),
    recipe_service: RecipeService = Depends(get_recipe_service),
):
    try:
        return recipe_service.update_recipe(
            user=current_user,
            recipe_id=recipe_id,
            data=data,
        )
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune recette n'a été trouvée.",
        )
    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )


# Fonction pour archiver ou désarchiver une recette
@router.patch("/{recipe_id}/archive", response_model=RecipeRead)
def update_recipe_archive_status(
    recipe_id: uuid.UUID,
    data: RecipeArchiveUpdate,
    current_user: User = Depends(get_current_user),
    recipe_service: RecipeService = Depends(get_recipe_service),
):
    try:
        return recipe_service.update_archive_status(
            user=current_user,
            recipe_id=recipe_id,
            data=data,
        )
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune recette n'a été trouvée.",
        )
    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )


# Fonction pour supprimer une recette
@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    recipe_service: RecipeService = Depends(get_recipe_service),
):
    try:
        recipe_service.delete_recipe(
            user=current_user,
            recipe_id=recipe_id,
        )
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune recette n'a été trouvée.",
        )
    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)