import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from betterself.recipes.models import Recipe
from betterself.recipes.queries import get_recipe_or_404
from betterself.recipes.schemas import (
    RecipeArchiveUpdate,
    RecipeCreate,
    RecipeUpdate,
)
from betterself.users.models import User


"""
Service responsable de la logique métier liée aux recettes.
"""
class RecipeService:
    def __init__(self, db: Session):
        self.db = db


    """
    Retourne les recettes de l'utilisateur, paginées. Par défaut, les recettes archivées sont exclues.
    """
    def list_recipes(
        self,
        user: User,
        *,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Recipe]:

        query = select(Recipe).where(
            Recipe.user_id == user.id,
        )
        # Filtrage des recettes archivées si nécessaire
        if not include_archived:
            query = query.where(
                Recipe.is_archived.is_(False),
            )
        # Exécution de la requête avec pagination et tri par date de création
        query = (
            query
            .order_by(Recipe.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(
            self.db.scalars(query).all()
        )

    """
    Crée une nouvelle recette pour l'utilisateur authentifié.
    """
    def create_recipe(
        self,
        user: User,
        data: RecipeCreate,
    ) -> Recipe:

        recipe = Recipe(
            user_id=user.id,
            name=data.name,
            description=data.description,
            total_weight_g=data.total_weight_g,
            servings=data.servings,
            is_archived=False,
        )
        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)

        return recipe


    """
    Met à jour partiellement une recette. Seuls les champs fournis dans `data` sont modifiés.
    """
    def update_recipe(
        self,
        user: User,
        recipe_id: uuid.UUID,
        data: RecipeUpdate,
    ) -> Recipe:

        recipe = self.get_recipe_by_id(
            recipe_id=recipe_id,
            user=user,
        )
        # Récupération de la recette à mettre à jour
        update_data = data.model_dump(
            exclude_unset=True,
        )
        # Application des mises à jour sur la recette existante
        for field, value in update_data.items():
            setattr(recipe, field, value)

        self.db.commit()
        self.db.refresh(recipe)

        return recipe


    """
    Archive ou désarchive une recette.
    L'archivage retire la recette des ajouts rapides, sans la supprimer.
    """
    def update_archive_status(
        self,
        user: User,
        recipe_id: uuid.UUID,
        data: RecipeArchiveUpdate,
    ) -> Recipe:

        recipe = self.get_recipe_by_id(
            recipe_id=recipe_id,
            user=user
        )
        # Mise à jour du statut d'archivage de la recette
        recipe.is_archived = data.is_archived

        self.db.commit()
        self.db.refresh(recipe)

        return recipe


    """
    Supprime définitivement une recette appartenant à l'utilisateur.
    """
    def delete_recipe(
        self,
        recipe_id: uuid.UUID,
        user: User,
    ) -> None:

        recipe = self.get_recipe_by_id(
            recipe_id=recipe_id,
            user=user,
        )
        # Suppression de la recette
        self.db.delete(recipe)
        self.db.commit()



    # FOnction utilisée par le routeur
    def get_recipe_by_id(
        self,
        user: User,
        recipe_id: uuid.UUID,
    ) -> Recipe:
        return get_recipe_or_404(
            self=self,
            user=user,
            recipe_id=recipe_id,
        )