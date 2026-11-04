import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from betterself.core.exceptions import RecordNotFound, DuplicateRecord
from betterself.foods.models import Food
from betterself.recipes.models import Recipe
from betterself.ingredients.models import RecipeIngredient
from betterself.ingredients.schemas import (
    RecipeIngredientCreate,
    RecipeIngredientUpdate,
)
from betterself.users.models import User


class RecipeIngredientService:
    """
    Service responsable de la logique métier liée aux ingrédients
    d'une recette.
    """

    def __init__(self, db: Session):
        self.db = db


    def _get_recipe_or_404(
        self,
        user: User,
        recipe_id: uuid.UUID,
    ) -> Recipe:
        """
        Retourne une recette appartenant à l'utilisateur authentifié.
        """
        # Recherche de la recette dans la base de données pour l'utilisateur donné
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


    def _get_ingredient_or_404(
        self,
        user: User,
        recipe_id: uuid.UUID,
        ingredient_id: uuid.UUID,
    ) -> RecipeIngredient:
        """
        Retourne un ingrédient appartenant à une recette de l'utilisateur authentifié.
        """
        # Recherche de l'ingrédient dans la base de données pour la recette et l'utilisateur donné
        ingredient = self.db.scalar(
            select(RecipeIngredient)
            .join(Recipe, RecipeIngredient.recipe_id == Recipe.id)
            .where(
                RecipeIngredient.id == ingredient_id,
                RecipeIngredient.recipe_id == recipe_id,
                Recipe.user_id == user.id,
            )
        )
        # Aucun résultat trouvé, levée de l'exception RecordNotFound
        if ingredient is None:
            raise RecordNotFound(
                "Aucun ingrédient de recette n'a été trouvé."
            )
        return ingredient


    def _get_food_or_404(
        self,
        food_id: uuid.UUID,
    ) -> Food:
        """
        Vérifie que l'aliment référencé existe dans la base de données.
        """
        food = self.db.scalar(
            select(Food).where(
                Food.id == food_id,
            )
        )

        if food is None:
            raise RecordNotFound(
                "Aucun aliment n'a été trouvé."
            )

        return food


    def create_ingredient(
        self,
        user: User,
        recipe_id: uuid.UUID,
        data: RecipeIngredientCreate,
    ) -> RecipeIngredient:
        """
        Ajoute un aliment à une recette.

        Un même aliment ne peut apparaître qu'une seule fois
        dans une même recette.
        """
        # Vérification de l'existence de la recette et de l'aliment pour l'utilisateur donné
        recipe = self._get_recipe_or_404(
            user=user,
            recipe_id=recipe_id,
        )
        self._get_food_or_404(
            food_id=data.food_id,
        )
        # Vérification de l'existence d'un ingrédient identique dans la recette pour éviter les doublons
        existing_ingredient = self.db.scalar(
            select(RecipeIngredient).where(
                RecipeIngredient.recipe_id == recipe.id,
                RecipeIngredient.food_id == data.food_id,
            )
        )
        # Levée de l'exception en cas de doublon
        if existing_ingredient is not None:
            raise DuplicateRecord(
                "Cet aliment est déjà présent dans cette recette."
            )
        # Création de l'objet RecipeIngredient avec les données fournies
        ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            food_id=data.food_id,
            quantity_g=data.quantity_g,
        )

        # Ajout de l'ingrédient à la base de données
        self.db.add(ingredient)
        self.db.commit()
        self.db.refresh(ingredient)

        return ingredient


    def get_ingredient_or_404(
        self,
        user: User,
        recipe_id: uuid.UUID,
        ingredient_id: uuid.UUID,
    ) -> RecipeIngredient:
        """
        Retourne un ingrédient précis d'une recette.
        """
        return self._get_ingredient_or_404(
            user=user,
            recipe_id=recipe_id,
            ingredient_id=ingredient_id,
        )


    def update_ingredient(
        self,
        user: User,
        recipe_id: uuid.UUID,
        ingredient_id: uuid.UUID,
        data: RecipeIngredientUpdate,
    ) -> RecipeIngredient:
        """
        Met à jour la quantité d'un ingrédient.
        """
        ingredient = self._get_ingredient_or_404(
            user=user,
            recipe_id=recipe_id,
            ingredient_id=ingredient_id,
        )
        # Mise à jour de la quantité de l'ingrédient
        ingredient.quantity_g = data.quantity_g

        self.db.commit()
        self.db.refresh(ingredient)

        return ingredient


    def delete_ingredient(
        self,
        user: User,
        recipe_id: uuid.UUID,
        ingredient_id: uuid.UUID,
    ) -> None:
        """
        Supprime un ingrédient d'une recette.
        """
        ingredient = self._get_ingredient_or_404(
            user=user,
            recipe_id=recipe_id,
            ingredient_id=ingredient_id,
        )

        # Suppression de l'ingrédient de la base de données
        self.db.delete(ingredient)
        self.db.commit()