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
from betterself.core.exceptions import DuplicateRecord, RecordNotFound
from betterself.schemas.recipe_schemas import (
    RecipeArchiveUpdate,
    RecipeCreate,
    RecipeIngredientCreate,
    RecipeIngredientRead,
    RecipeIngredientUpdate,
    RecipeRead,
    RecipeUpdate,
)
from betterself.repos.recipe_repo import RecipeRepository
from betterself.repos.food_repo import FoodRepository
from betterself.services.recipe_service import RecipeService
from betterself.core.dependencies import get_current_user
from betterself.models.user_models import User
from betterself.prefix import RECIPES_URL


router = APIRouter(
    prefix=RECIPES_URL,
    tags=["Recipes"],
)


# Dépendance pour construire le service de recettes à partir de la session
def get_recipe_service(
    db: Session = Depends(get_db),
) -> RecipeService:
    return RecipeService(
        recipe_repository=RecipeRepository(db),
        food_repository=FoodRepository(db),
    )


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
    service: RecipeService = Depends(get_recipe_service),
):
    return service.list_recipes(
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
    service: RecipeService = Depends(get_recipe_service),
):
    return service.create_recipe(
        user=current_user,
        data=data,
    )


# Fonction pour récupérer une recette par son identifiant
@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(
    recipe_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: RecipeService = Depends(get_recipe_service)
):
    try:
        return service.get_recipe_by_id(
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
    service: RecipeService = Depends(get_recipe_service),
):
    try:
        return service.update_recipe(
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
    service: RecipeService = Depends(get_recipe_service),
):
    try:
        return service.update_archive_status(
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
    service: RecipeService = Depends(get_recipe_service),
):
    try:
        service.delete_recipe(
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


"""
Ajoute un aliment à une recette.
"""
@router.post("/{recipe_id}/ingredients", response_model=RecipeIngredientRead, status_code=status.HTTP_201_CREATED,)
def create_recipe_ingredient(
    recipe_id: uuid.UUID,
    data: RecipeIngredientCreate,
    current_user: User = Depends(get_current_user),
    service: RecipeService = Depends(get_recipe_service)
):
    try:
        return service.create_ingredient(
            user=current_user,
            recipe_id=recipe_id,
            data=data,
        )
    except RecordNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    except DuplicateRecord as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


"""
Retourne un ingrédient précis d'une recette.
"""
@router.get("/{recipe_id}/ingredients/{ingredient_id}", response_model=RecipeIngredientRead)
def get_recipe_ingredient(
    recipe_id: uuid.UUID,
    ingredient_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: RecipeService = Depends(get_recipe_service),
):
    try:
        return service.get_ingredient_by_id(
            user=current_user,
            recipe_id=recipe_id,
            ingredient_id=ingredient_id,
        )
    except RecordNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


"""
Met à jour la quantité d'un ingrédient.
"""
@router.patch("/{recipe_id}/ingredients/{ingredient_id}", response_model=RecipeIngredientRead)
def update_recipe_ingredient(
    recipe_id: uuid.UUID,
    ingredient_id: uuid.UUID,
    data: RecipeIngredientUpdate,
    current_user: User = Depends(get_current_user),
    service: RecipeService = Depends(get_recipe_service),
):
    try:
        return service.update_ingredient(
            user=current_user,
            recipe_id=recipe_id,
            ingredient_id=ingredient_id,
            data=data,
        )
    except RecordNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


"""
Supprime un ingrédient d'une recette.
"""
@router.delete("/{recipe_id}/ingredients/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe_ingredient(
    recipe_id: uuid.UUID,
    ingredient_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: RecipeService = Depends(get_recipe_service),
):
    try:
        service.delete_ingredient(
            user=current_user,
            recipe_id=recipe_id,
            ingredient_id=ingredient_id,
        )
    except RecordNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)