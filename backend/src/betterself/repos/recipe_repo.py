import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from betterself.core.exceptions import RecordNotFound
from betterself.models.recipe_models import Recipe, RecipeIngredient
from betterself.models.user_models import User


class RecipeRepository:
    def __init__(self, db: Session):
        self.db = db

    # Liste toutes les recettes pour un utilisateur donné, avec options de pagination et d'inclusion des recettes archivées.
    def list_for_user(
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
        return list(self.db.scalars(query).all())


    # Récupère une recette spécifique pour un utilisateur donné, avec ses ingrédients et les aliments associés.
    def get_for_user(
        self,
        user: User,
        recipe_id: uuid.UUID,
    ) -> Recipe | None:
        query = (
            select(Recipe)
            .where(
                Recipe.id == recipe_id,
                Recipe.user_id == user.id,
            )
            .options(
                selectinload(Recipe.ingredients).selectinload(
                    RecipeIngredient.food
                ),
            )
        )
        return self.db.scalar(query)


    # Récupère un ingrédient spécifique pour une recette d'un utilisateur donné.
    def get_ingredient_for_user(
        self,
        user: User,
        recipe_id: uuid.UUID,
        ingredient_id: uuid.UUID,
    ) -> RecipeIngredient | None:
        query = (
            select(RecipeIngredient)
            .join(Recipe, RecipeIngredient.recipe_id == Recipe.id)
            .where(
                RecipeIngredient.id == ingredient_id,
                RecipeIngredient.recipe_id == recipe_id,
                Recipe.user_id == user.id,
            )
        )
        return self.db.scalar(query)


    # Vérifie si un ingrédient existe pour une recette donnée.
    # Retourne True si l'ingrédient existe, False sinon.
    def ingredient_exists(
        self,
        recipe_id: uuid.UUID,
        food_id: uuid.UUID,
    ) -> bool:
        query = select(RecipeIngredient).where(
            RecipeIngredient.recipe_id == recipe_id,
            RecipeIngredient.food_id == food_id,
        )
        return self.db.scalar(query) is not None


    # Ajoute une nouvelle recette à la base de données.
    def add(self, recipe: Recipe) -> Recipe:
        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)
        return recipe


    # Ajoute un nouvel ingrédient à la base de données.
    def add_ingredient(
        self,
        ingredient: RecipeIngredient,
    ) -> RecipeIngredient:
        self.db.add(ingredient)
        self.db.commit()
        self.db.refresh(ingredient)
        return ingredient


    # Sauvegarde les modifications apportées à une recette existante.
    def save(self, recipe: Recipe) -> Recipe:
        self.db.commit()
        self.db.refresh(recipe)
        return recipe


    # Sauvegarde les modifications apportées à un ingrédient existant.
    def save_ingredient(
        self,
        ingredient: RecipeIngredient,
    ) -> RecipeIngredient:
        self.db.commit()
        self.db.refresh(ingredient)
        return ingredient


    # Supprime une recette de la base de données.
    def delete(self, recipe: Recipe) -> None:
        self.db.delete(recipe)
        self.db.commit()


    # Supprime un ingrédient de la base de données.
    def delete_ingredient(
        self,
        ingredient: RecipeIngredient,
    ) -> None:
        self.db.delete(ingredient)
        self.db.commit()

    """
    Retourne une recette appartenant à l'utilisateur.
    Lève `RecordNotFound` si la recette n'existe pas ou n'appartient pas à l'utilisateur.
    """
    def get_recipe_or_404(
        self,
        user: User,
        recipe_id: uuid.UUID,
    ) -> Recipe:
        recipe = self.db.scalar(
            select(Recipe).where(
                Recipe.id == recipe_id,
                Recipe.user_id == user.id,
        )
        )
        # Aucun résultat trouvé, levée de l'exception RecordNotFound
        if recipe is None:
            raise RecordNotFound(
                "Aucune recette n'a été trouvée."
            )
        return recipe