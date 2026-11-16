
import { getErrorMessage } from "../api/axios";
import type { FoodConsumptionCreate } from "../api/generated/foodConsumptionCreate";
import { getFoodConsumptions } from "../api/generated/food-consumptions/food-consumptions";
import { getFoods } from "../api/generated/foods/foods";
import type { FoodCreate } from "../api/generated/foodCreate";
import type { FoodRead } from "../api/generated/foodRead";
import type { SearchFoodsFoodsGetParams } from "../api/generated/searchFoodsFoodsGetParams";

export const foodService = {
    // Recherche des aliments par nom, marque ou référence externe
    // `signal` permet d'annuler la requête (ex. : recherche devenue inutile).
    async searchFoods(
        query: string,
        options: Omit<SearchFoodsFoodsGetParams, "query"> = {},
        signal?: AbortSignal,
    ): Promise<FoodRead[]> {
        try {
            // Récupère la fonction de recherche des aliments depuis l'API.
            const { searchFoodsFoodsGet } = getFoods();
            return await searchFoodsFoodsGet(
                {
                    query: query.trim(),
                    limit: 20,
                    ...options,
                },
                { signal },
            );
        } catch (error) {
            throw new Error(
                getErrorMessage(
                    error,
                    "Impossible de rechercher les aliments."
                )
            );
        }
    },

    // Crée un aliment manuel
    async createFood(payload: FoodCreate): Promise<FoodRead> {
        try {
            const { createFoodFoodsPost } = getFoods();
            return await createFoodFoodsPost(payload);
        } catch (error) {
            throw new Error(
            getErrorMessage(
                error,
                "Impossible de créer cet aliment."
            )
            );
        }
    },

    // Récupère un aliment par son identifiant
    async getFood(foodId: string): Promise<FoodRead> {
        try {
            const { getFoodFoodsFoodIdGet } = getFoods();
            return await getFoodFoodsFoodIdGet(foodId);
        } catch (error) {
            throw new Error(
            getErrorMessage(
                error,
                "Impossible de charger cet aliment."
            )
            );
        }
    },

    // Ajoute un aliment au journal alimentaire
    async addFoodToJournal(
        payload: FoodConsumptionCreate,
    ): Promise<void> {
        try {
            const { createFoodConsumptionFoodConsumptionsPost } = getFoodConsumptions();
            await createFoodConsumptionFoodConsumptionsPost(payload);
        } catch (error) {
            throw new Error(
            getErrorMessage(
                error,
                "Impossible d’ajouter cet aliment au journal."
            )
            );
        }
    }
}
