import axios from "axios";
import { getErrorMessage } from "../api/axios";
import { getFoodConsumptions } from "../api/generated/endpoints/food-consumptions/food-consumptions";
import type { FoodConsumptionRead } from "../api/generated/foodConsumptionRead";
import type { FoodConsumptionUpdate } from "../api/generated/foodConsumptionUpdate";
import type { GoalTargetRead } from "../api/generated/goalTargetRead";
import { getNutritionGoal } from "../api/generated/endpoints/nutrition-goal/nutrition-goal";
import { getDayBoundsIso } from "../lib/date";

// Nombre maximal d'entrées accepté par l'API pour une page.
const MAX_ENTRIES_PER_DAY = 100;

export const journalService = {
    // Récupère les consommations d'une journée locale ("YYYY-MM-DD").
    async getEntriesForDay(dayKey: string): Promise<FoodConsumptionRead[]> {
        try {
            const { listFoodConsumptionsFoodConsumptionsGet } = getFoodConsumptions();
            const { start, end } = getDayBoundsIso(dayKey);
            return await listFoodConsumptionsFoodConsumptionsGet({
                start_date: start,
                end_date: end,
                limit: MAX_ENTRIES_PER_DAY,
            });
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de charger le journal.")
            );
        }
    },

    // Récupère une consommation du journal.
    async getEntry(consumptionId: string): Promise<FoodConsumptionRead> {
        try {
            const { getFoodConsumptionFoodConsumptionsConsumptionIdGet } = getFoodConsumptions();
            return await getFoodConsumptionFoodConsumptionsConsumptionIdGet(consumptionId);
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de charger cette entrée.")
            );
        }
    },

    // Modifie une consommation (les nutriments sont recalculés par l'API).
    async updateEntry(
        consumptionId: string,
        payload: FoodConsumptionUpdate,
    ): Promise<FoodConsumptionRead> {
        try {
            const { updateFoodConsumptionFoodConsumptionsConsumptionIdPatch } = getFoodConsumptions();
            return await updateFoodConsumptionFoodConsumptionsConsumptionIdPatch(consumptionId, payload);
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de modifier cette entrée.")
            );
        }
    },

    // Supprime une consommation du journal.
    async deleteEntry(consumptionId: string): Promise<void> {
        try {
            const { deleteFoodConsumptionFoodConsumptionsConsumptionIdDelete } = getFoodConsumptions();
            await deleteFoodConsumptionFoodConsumptionsConsumptionIdDelete(consumptionId);
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de supprimer cette entrée.")
            );
        }
    },

    // Récupère la cible nutritionnelle active ; null si l'utilisateur n'en a pas.
    async getCurrentTarget(): Promise<GoalTargetRead | null> {
        try {
            const { getCurrentGoalTargetNutritionGoalCurrentTargetGet } = getNutritionGoal();
            return await getCurrentGoalTargetNutritionGoalCurrentTargetGet();
        } catch (error) {
            if (axios.isAxiosError(error) && error.response?.status === 404) {
                return null;
            }
            throw new Error(
                getErrorMessage(error, "Impossible de charger votre cible nutritionnelle.")
            );
        }
    },
};
