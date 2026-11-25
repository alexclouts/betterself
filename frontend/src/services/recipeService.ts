import { getErrorMessage } from "../api/axios";
import { getRecipes } from "../api/generated/endpoints/recipes/recipes";
import type { RecipeCreate } from "../api/generated/recipeCreate";
import type { RecipeIngredientRead } from "../api/generated/recipeIngredientRead";
import type { RecipeRead } from "../api/generated/recipeRead";
import type { RecipeUpdate } from "../api/generated/recipeUpdate";

// Nombre maximal de recettes accepté par l'API pour une page.
const MAX_RECIPES = 100;

export const recipeService = {
    // Liste les recettes de l'utilisateur; les recettes archivées sont exclues par défaut.
    async listRecipes(includeArchived = false): Promise<RecipeRead[]> {
        try {
            const { listRecipesRecipesGet } = getRecipes();
            return await listRecipesRecipesGet({
                include_archived: includeArchived,
                limit: MAX_RECIPES,
            });
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de charger les recettes."),
                { cause: error },
            );
        }
    },

    // Récupère une recette avec ses ingrédients et ses valeurs nutritionnelles.
    async getRecipe(recipeId: string): Promise<RecipeRead> {
        try {
            const { getRecipeRecipesRecipeIdGet } = getRecipes();
            return await getRecipeRecipesRecipeIdGet(recipeId);
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de charger cette recette."),
                { cause: error },
            );
        }
    },

    // Crée une recette, sans ingrédients.
    async createRecipe(payload: RecipeCreate): Promise<RecipeRead> {
        try {
            const { createRecipeRecipesPost } = getRecipes();
            return await createRecipeRecipesPost(payload);
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de créer cette recette."),
                { cause: error },
            );
        }
    },

    // Modifie le nom, la description, le poids total ou les portions d'une recette.
    async updateRecipe(recipeId: string, payload: RecipeUpdate): Promise<RecipeRead> {
        try {
            const { updateRecipeRecipesRecipeIdPatch } = getRecipes();
            return await updateRecipeRecipesRecipeIdPatch(recipeId, payload);
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de modifier cette recette."),
                { cause: error },
            );
        }
    },

    // Archive ou désarchive une recette. L'archivage la retire des choix courants
    // sans toucher aux entrées du journal qui y font référence.
    async setArchived(recipeId: string, isArchived: boolean): Promise<RecipeRead> {
        try {
            const { updateRecipeArchiveStatusRecipesRecipeIdArchivePatch } = getRecipes();
            return await updateRecipeArchiveStatusRecipesRecipeIdArchivePatch(recipeId, {
                is_archived: isArchived,
            });
        } catch (error) {
            throw new Error(
                getErrorMessage(
                    error,
                    isArchived
                        ? "Impossible d’archiver cette recette."
                        : "Impossible de réactiver cette recette.",
                ),
                { cause: error },
            );
        }
    },

    // Supprime définitivement une recette et ses ingrédients. Préférer l'archivage.
    async deleteRecipe(recipeId: string): Promise<void> {
        try {
            const { deleteRecipeRecipesRecipeIdDelete } = getRecipes();
            await deleteRecipeRecipesRecipeIdDelete(recipeId);
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de supprimer cette recette."),
                { cause: error },
            );
        }
    },

    // Ajoute un aliment à la recette.
    async addIngredient(
        recipeId: string,
        foodId: string,
        quantityG: number,
    ): Promise<RecipeIngredientRead> {
        try {
            const { createRecipeIngredientRecipesRecipeIdIngredientsPost } = getRecipes();
            return await createRecipeIngredientRecipesRecipeIdIngredientsPost(recipeId, {
                recipe_id: recipeId,
                food_id: foodId,
                quantity_g: quantityG,
            });
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible d’ajouter cet ingrédient."),
                { cause: error },
            );
        }
    },

    // Modifie la quantité d'un ingrédient.
    async updateIngredient(
        recipeId: string,
        ingredientId: string,
        quantityG: number,
    ): Promise<RecipeIngredientRead> {
        try {
            const { updateRecipeIngredientRecipesRecipeIdIngredientsIngredientIdPatch } = getRecipes();
            return await updateRecipeIngredientRecipesRecipeIdIngredientsIngredientIdPatch(
                recipeId,
                ingredientId,
                { quantity_g: quantityG },
            );
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de modifier cet ingrédient."),
                { cause: error },
            );
        }
    },

    // Retire un ingrédient de la recette.
    async removeIngredient(recipeId: string, ingredientId: string): Promise<void> {
        try {
            const { deleteRecipeIngredientRecipesRecipeIdIngredientsIngredientIdDelete } = getRecipes();
            await deleteRecipeIngredientRecipesRecipeIdIngredientsIngredientIdDelete(
                recipeId,
                ingredientId,
            );
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de retirer cet ingrédient."),
                { cause: error },
            );
        }
    },
};
