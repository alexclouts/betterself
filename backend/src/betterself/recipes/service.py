from decimal import Decimal
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from betterself.ingredients.schemas import RecipeIngredientRead
from betterself.recipes.models import Recipe
from betterself.recipes.queries import get_recipe_or_404
from betterself.recipes.schemas import (
    RecipeArchiveUpdate,
    RecipeCreate,
    RecipeRead,
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

        return self.get_recipe_by_id(
            recipe_id=recipe.id,
            user=user
        )


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


    """
    Calcule les valeurs nutritionnelles d'une recette.
    """
    def _calculate_recipe_nutrition(
        self,
        recipe: Recipe,
    ) -> dict:
        total_calories = Decimal("0")
        total_protein = Decimal("0")
        total_carbohydrates = Decimal("0")
        total_fat = Decimal("0")

        # Pour chaque ingrédient, on calcule sa contribution aux valeurs nutritionnelles totales de la recette.
        for ingredient in recipe.ingredients:
            food = ingredient.food
            reference_weight = food.reference_weight_g

            if reference_weight <= 0:
                continue

            factor = ingredient.quantity_g / reference_weight
            # Calcul des valeurs nutritionnelles de l'ingrédient en fonction de sa quantité.
            total_calories += food.calories_kcal * factor
            total_protein += food.protein_g * factor
            total_carbohydrates += food.carbohydrates_g * factor
            total_fat += food.fat_g * factor

        return {
            "calories_kcal": total_calories,
            "protein_g": total_protein,
            "carbohydrates_g": total_carbohydrates,
            "fat_g": total_fat
        }


    """
    Fonction utilisée par le routeur pour récupérer une recette et ses valeurs nutritionnelles.
    RecipeRead comprend les informations nutritionnelles qui ne sont pas stockées directement dans la recette.
    RecipeRead comprend l'addition de plusieurs sources de données qui sont retournées par l'API.
    """
    def get_recipe_by_id(
        self,
        user: User,
        recipe_id: uuid.UUID,
    ) -> RecipeRead:
        # Récupération de la recette depuis la base de données.
        recipe = get_recipe_or_404(
            self=self,
            user=user,
            recipe_id=recipe_id,
        )
        # Calcul des valeurs nutritionnelles de la recette.
        nutrition = self._calculate_recipe_nutrition(recipe)

        return RecipeRead(
            id=recipe.id,
            user_id=recipe.user_id,
            name=recipe.name,
            description=recipe.description,
            total_weight_g=recipe.total_weight_g,
            servings=recipe.servings,
            is_archived=recipe.is_archived,
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
            ingredients=[RecipeIngredientRead(
                id=ingredient.id,
                food_id=ingredient.food_id,
                recipe_id=recipe_id,
                quantity_g=ingredient.quantity_g,
                created_at=ingredient.created_at,
                updated_at=ingredient.updated_at,
            ) for ingredient in recipe.ingredients],
            nutrition=nutrition
        )