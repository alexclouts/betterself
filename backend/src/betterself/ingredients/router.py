import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from requests import Session

from betterself.core.database import get_db
from betterself.core.exceptions import DuplicateRecord, RecordNotFound
from betterself.ingredients.schemas import (
    RecipeIngredientCreate,
    RecipeIngredientRead,
    RecipeIngredientUpdate,
)
from betterself.ingredients.service import RecipeIngredientService
from betterself.users.utils import get_current_user
from betterself.users.models import User


# Aucun préfixe n'est défini pour ce routeur, les routes sont relatives à /recipes/{recipe_id}/ingredients
router = APIRouter(
    prefix="/recipes",
    tags=["ingredients"],
)


"""
Construit le service des ingrédients de recette.
"""
def get_recipe_ingredient_service(
    db: Session = Depends(get_db),
) -> RecipeIngredientService:
    return RecipeIngredientService(db)


"""
Ajoute un aliment à une recette.
"""
@router.post("/{recipe_id}/ingredients", response_model=RecipeIngredientRead, status_code=status.HTTP_201_CREATED,)
def create_recipe_ingredient(
    recipe_id: uuid.UUID,
    data: RecipeIngredientCreate,
    current_user: User = Depends(get_current_user),
    ingredient_service: RecipeIngredientService = Depends(
        get_recipe_ingredient_service,
    )
):
    try:
        return ingredient_service.create_ingredient(
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
    ingredient_service: RecipeIngredientService = Depends(
        get_recipe_ingredient_service,
    ),
):
    try:
        return ingredient_service.get_ingredient_or_404(
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
    ingredient_service: RecipeIngredientService = Depends(
        get_recipe_ingredient_service,
    ),
):
    try:
        return ingredient_service.update_ingredient(
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
    ingredient_service: RecipeIngredientService = Depends(
        get_recipe_ingredient_service,
    ),
):
    try:
        ingredient_service.delete_ingredient(
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