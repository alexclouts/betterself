import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from betterself.core.exceptions import RecordNotFound
from betterself.recipes.models import Recipe
from betterself.recipes.schemas import (
    RecipeArchiveUpdate,
    RecipeCreate,
    RecipeUpdate,
)
from betterself.users.models import User


class RecipeService:
    """
    Service responsable de la logique métier liée aux recettes.
    """

    def __init__(self, db: Session):
        self.db = db


    def list_recipes(
        self,
        user: User,
        *,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Recipe]:
        """
        Retourne les recettes de l'utilisateur, paginées. Par défaut, les recettes archivées sont exclues.
        """
        query = select(Recipe).where(
            Recipe.user_id == user.id,
        )

        if not include_archived:
            query = query.where(
                Recipe.is_archived.is_(False),
            )

        query = (
            query
            .order_by(Recipe.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(
            self.db.scalars(query).all()
        )


    def create_recipe(
        self,
        user: User,
        data: RecipeCreate,
    ) -> Recipe:
        """
        Crée une nouvelle recette pour l'utilisateur authentifié.
        """
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


    def get_recipe_or_404(
        self,
        user: User,
        recipe_id: uuid.UUID,
    ) -> Recipe:
        """
        Retourne une recette appartenant à l'utilisateur.
        Lève `RecordNotFound` si la recette n'existe pas ou n'appartient pas à l'utilisateur.
        """
        recipe = self.db.scalar(
            select(Recipe).where(
                Recipe.id == recipe_id,
                Recipe.user_id == user.id,
            )
        )

        if recipe is None:
            raise RecordNotFound(
                "Aucune recette n'a été trouvée."
            )

        return recipe


    def update_recipe(
        self,
        user: User,
        recipe_id: uuid.UUID,
        data: RecipeUpdate,
    ) -> Recipe:
        """
        Met à jour partiellement une recette. Seuls les champs fournis dans `data` sont modifiés.
        """
        recipe = self.get_recipe_or_404(
            user=user,
            recipe_id=recipe_id,
        )

        update_data = data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(recipe, field, value)

        self.db.commit()
        self.db.refresh(recipe)

        return recipe


    def update_archive_status(
        self,
        user: User,
        recipe_id: uuid.UUID,
        data: RecipeArchiveUpdate,
    ) -> Recipe:
        """
        Archive ou désarchive une recette.
        L'archivage retire la recette des ajouts rapides, sans la supprimer.
        """
        recipe = self.get_recipe_or_404(
            user=user,
            recipe_id=recipe_id,
        )

        recipe.is_archived = data.is_archived

        self.db.commit()
        self.db.refresh(recipe)

        return recipe


    def delete_recipe(
        self,
        user: User,
        recipe_id: uuid.UUID,
    ) -> None:
        """
        Supprime définitivement une recette appartenant à l'utilisateur.
        """
        recipe = self.get_recipe_or_404(
            user=user,
            recipe_id=recipe_id,
        )

        self.db.delete(recipe)
        self.db.commit()