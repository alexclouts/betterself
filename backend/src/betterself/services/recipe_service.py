import uuid
from decimal import Decimal

from betterself.core.exceptions import (
    DuplicateRecord,
    RecordNotFound,
)
from betterself.repos.food_repo import FoodRepository
from betterself.models.recipe_models import Recipe, RecipeIngredient
from betterself.repos.recipe_repo import RecipeRepository
from betterself.schemas.recipe_schemas import (
    RecipeArchiveUpdate,
    RecipeCreate,
    RecipeIngredientCreate,
    RecipeIngredientFoodRead,
    RecipeIngredientRead,
    RecipeIngredientUpdate,
    RecipeNutritionRead,
    RecipeRead,
    RecipeUpdate,
)
from betterself.models.user_models import User


class RecipeService:
    def __init__(
        self,
        recipe_repository: RecipeRepository,
        food_repository: FoodRepository,
    ):
        self.recipe_repository = recipe_repository
        self.food_repository = food_repository


    # Liste les recettes de l'utilisateur connecté, avec options d'archivage, de limite et de décalage.
    def list_recipes(
        self,
        user: User,
        *,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> list[RecipeRead]:
        recipes = self.recipe_repository.list_for_user(
            user=user,
            include_archived=include_archived,
            limit=limit,
            offset=offset,
        )
        return [self._to_recipe_read(recipe) for recipe in recipes]


    # Récupère une recette par son identifiant pour l'utilisateur connecté.
    def get_recipe_by_id(
        self,
        user: User,
        recipe_id: uuid.UUID,
    ) -> RecipeRead:
        recipe = self._get_recipe_or_404(
            user=user,
            recipe_id=recipe_id,
        )
        return self._to_recipe_read(recipe)


    # Crée une nouvelle recette pour l'utilisateur connecté.
    def create_recipe(
        self,
        user: User,
        data: RecipeCreate,
    ) -> RecipeRead:
        recipe = Recipe(
            user_id=user.id,
            name=data.name,
            description=data.description,
            total_weight_g=data.total_weight_g,
            servings=data.servings,
            is_archived=False,
        )
        recipe = self.recipe_repository.add(recipe)

        return self.get_recipe_by_id(
            user=user,
            recipe_id=recipe.id,
        )


    # Met à jour une recette existante pour l'utilisateur connecté.
    def update_recipe(
        self,
        user: User,
        recipe_id: uuid.UUID,
        data: RecipeUpdate,
    ) -> RecipeRead:
        recipe = self._get_recipe_or_404(
            user=user,
            recipe_id=recipe_id,
        )
        update_data = data.model_dump(
            exclude_unset=True,
        )
        # Met à jour les champs de la recette avec les nouvelles valeurs fournies.
        for field, value in update_data.items():
            setattr(recipe, field, value)

        return self._to_recipe_read(recipe)


    # Met à jour le statut d'archivage d'une recette pour l'utilisateur connecté.
    def update_archive_status(
        self,
        user: User,
        recipe_id: uuid.UUID,
        data: RecipeArchiveUpdate,
    ) -> RecipeRead:
        recipe = self._get_recipe_or_404(
            user=user,
            recipe_id=recipe_id,
        )
        recipe.is_archived = data.is_archived
        
        return self._to_recipe_read(recipe)



    # Supprime une recette pour l'utilisateur connecté.
    def delete_recipe(
        self,
        user: User,
        recipe_id: uuid.UUID,
    ) -> None:
        recipe = self._get_recipe_or_404(
            user=user,
            recipe_id=recipe_id,
        )
        self.recipe_repository.delete(recipe)


    # Crée un nouvel ingrédient pour une recette de l'utilisateur connecté.
    def create_ingredient(
        self,
        user: User,
        recipe_id: uuid.UUID,
        data: RecipeIngredientCreate,
    ) -> RecipeIngredientRead:
        recipe = self._get_recipe_or_404(
            user=user,
            recipe_id=recipe_id,
        )
        # Vérifie que l'aliment existe dans la base de données.
        food = self.food_repository.get_food_or_404(
            food_id=data.food_id,
        )
        ingredient_exists = self.recipe_repository.ingredient_exists(
            recipe_id=recipe.id,
            food_id=data.food_id,
        )

        if ingredient_exists:
            raise DuplicateRecord(
                "Cet aliment est déjà présent dans cette recette."
            )

        ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            food_id=data.food_id,
            quantity_g=data.quantity_g,
        )
        ingredient = self.recipe_repository.add_ingredient(ingredient)
        ingredient.food = food
        return self._to_ingredient_read(ingredient)


    # Récupère un ingrédient d'une recette pour l'utilisateur connecté.
    def get_ingredient_by_id(
        self,
        user: User,
        recipe_id: uuid.UUID,
        ingredient_id: uuid.UUID,
    ) -> RecipeIngredientRead:
        ingredient = self._get_ingredient_or_404(
            user=user,
            recipe_id=recipe_id,
            ingredient_id=ingredient_id,
        )
        return self._to_ingredient_read(ingredient)


    # Met à jour un ingrédient existant pour une recette de l'utilisateur connecté.
    def update_ingredient(
        self,
        user: User,
        recipe_id: uuid.UUID,
        ingredient_id: uuid.UUID,
        data: RecipeIngredientUpdate,
    ) -> RecipeIngredientRead:
        ingredient = self._get_ingredient_or_404(
            user=user,
            recipe_id=recipe_id,
            ingredient_id=ingredient_id,
        )
        ingredient.quantity_g = data.quantity_g
        return self._to_ingredient_read(ingredient)


    # Supprime un ingrédient d'une recette pour l'utilisateur connecté.
    def delete_ingredient(
        self,
        user: User,
        recipe_id: uuid.UUID,
        ingredient_id: uuid.UUID,
    ) -> None:
        ingredient = self._get_ingredient_or_404(
            user=user,
            recipe_id=recipe_id,
            ingredient_id=ingredient_id,
        )
        self.recipe_repository.delete_ingredient(ingredient)


    # Récupère une recette pour l'utilisateur connecté ou lève une erreur si elle n'existe pas.
    def _get_recipe_or_404(
        self,
        user: User,
        recipe_id: uuid.UUID,
    ) -> Recipe:
        recipe = self.recipe_repository.get_for_user(
            user=user,
            recipe_id=recipe_id,
        )
        if recipe is None:
            raise RecordNotFound(
                "Aucune recette n'a été trouvée."
            )
        return recipe


    # Récupère un ingrédient de recette pour l'utilisateur connecté ou lève une erreur si il n'existe pas.
    def _get_ingredient_or_404(
        self,
        user: User,
        recipe_id: uuid.UUID,
        ingredient_id: uuid.UUID,
    ) -> RecipeIngredient:
        ingredient = self.recipe_repository.get_ingredient_for_user(
            user=user,
            recipe_id=recipe_id,
            ingredient_id=ingredient_id,
        )
        if ingredient is None:
            raise RecordNotFound(
                "Aucun ingrédient de recette n'a été trouvé."
            )
        return ingredient


    # Calcule les valeurs nutritionnelles d'un ingrédient pour sa quantité.
    def _calculate_ingredient_nutrition(
        self,
        ingredient: RecipeIngredient,
    ) -> RecipeNutritionRead:
        food = ingredient.food
        reference_weight = food.reference_weight_g
        factor = (
            ingredient.quantity_g / reference_weight
            if reference_weight > 0
            else Decimal("0")
        )
        return RecipeNutritionRead(
            calories_kcal=food.calories_kcal * factor,
            protein_g=food.protein_g * factor,
            carbohydrates_g=food.carbohydrates_g * factor,
            fat_g=food.fat_g * factor,
        )


    # Calcule la valeur nutritionnelle totale d'une recette à partir de ses ingrédients.
    def _calculate_recipe_nutrition(
        self,
        ingredients: list[RecipeIngredientRead],
    ) -> RecipeNutritionRead:
        return RecipeNutritionRead(
            calories_kcal=sum((i.nutrition.calories_kcal for i in ingredients), Decimal("0")),
            protein_g=sum((i.nutrition.protein_g for i in ingredients), Decimal("0")),
            carbohydrates_g=sum((i.nutrition.carbohydrates_g for i in ingredients), Decimal("0")),
            fat_g=sum((i.nutrition.fat_g for i in ingredients), Decimal("0")),
        )


    # Convertit un ingrédient en schéma de lecture, avec son aliment et sa nutrition.
    def _to_ingredient_read(
        self,
        ingredient: RecipeIngredient,
    ) -> RecipeIngredientRead:
        return RecipeIngredientRead(
            id=ingredient.id,
            recipe_id=ingredient.recipe_id,
            food=RecipeIngredientFoodRead.model_validate(ingredient.food),
            quantity_g=ingredient.quantity_g,
            nutrition=self._calculate_ingredient_nutrition(ingredient),
            created_at=ingredient.created_at,
            updated_at=ingredient.updated_at,
        )


    # Convertit une instance de recette en un schéma de lecture de recette.
    def _to_recipe_read(
        self,
        recipe: Recipe,
    ) -> RecipeRead:
        ingredients = [
            self._to_ingredient_read(ingredient)
            for ingredient in recipe.ingredients
        ]
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
            ingredients=ingredients,
            nutrition=self._calculate_recipe_nutrition(ingredients),
        )