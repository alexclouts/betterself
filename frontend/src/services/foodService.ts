
import axios from "axios";
import { getErrorMessage } from "../api/axios";
import type { FoodConsumptionCreate } from "../api/generated/foodConsumptionCreate";
import { getFoodConsumptions } from "../api/generated/endpoints/food-consumptions/food-consumptions";
import { getFoods } from "../api/generated/endpoints/foods/foods";
import type { FoodCreate } from "../api/generated/foodCreate";
import type { FoodRead } from "../api/generated/foodRead";
import type { FoodSearchRead } from "../api/generated/foodSearchRead";
import type { FoodSearchResult } from "../api/generated/foodSearchResult";

// Résultat d'un scan : produit trouvé, code inconnu, ou catalogue impossible à consulter.
export type BarcodeLookup =
    | { status: "found"; result: FoodSearchResult }
    | { status: "unknown" }
    | { status: "catalog_unavailable" };

export const foodService = {
    // Recherche dans tous les aliments, peu importe leur provenance. Sans terme,
    // retourne l'historique de l'utilisateur.
    // `signal` permet d'annuler la requête (ex. : recherche devenue inutile).
    async searchFoods(query: string, signal?: AbortSignal): Promise<FoodSearchRead> {
        try {
            const { searchAllFoodsFoodsSearchGet } = getFoods();
            return await searchAllFoodsFoodsSearchGet(
                { query: query.trim(), limit: 20 },
                { signal },
            );
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de rechercher les aliments."),
                { cause: error },
            );
        }
    },

    // Cherche l'aliment ou le produit du catalogue portant ce code-barres.
    async findByBarcode(code: string): Promise<BarcodeLookup> {
        try {
            const { findFoodByBarcodeFoodsBarcodeCodeGet } = getFoods();
            return { status: "found", result: await findFoodByBarcodeFoodsBarcodeCodeGet(code) };
        } catch (error) {
            const status = axios.isAxiosError(error) ? error.response?.status : undefined;
            if (status === 404) return { status: "unknown" };
            if (status === 503) return { status: "catalog_unavailable" };
            throw new Error(
                getErrorMessage(error, "Impossible de rechercher ce code-barres."),
                { cause: error },
            );
        }
    },

    // Copie un produit du catalogue dans les aliments (sans doublon)
    async importCatalogProduct(code: string): Promise<FoodRead> {
        try {
            const { importCatalogProductFoodsCatalogCodeImportPost } = getFoods();
            return await importCatalogProductFoodsCatalogCodeImportPost(code);
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible d’ajouter ce produit."),
                { cause: error },
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
