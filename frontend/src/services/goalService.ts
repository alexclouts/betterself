import axios from "axios";
import { getErrorMessage } from "../api/axios";
import { getNutritionGoal } from "../api/generated/endpoints/nutrition-goal/nutrition-goal";
import type { NutritionGoalRead } from "../api/generated/nutritionGoalRead";

export const goalService = {
    // Récupère l'objectif nutritionnel actif ; null si l'utilisateur n'en a pas.
    async getCurrentGoal(): Promise<NutritionGoalRead | null> {
        try {
            const { getNutritionalGoalNutritionGoalCurrentGet } = getNutritionGoal();
            return await getNutritionalGoalNutritionGoalCurrentGet();
        } catch (error) {
            if (axios.isAxiosError(error) && error.response?.status === 404) {
                return null;
            }
            throw new Error(
                getErrorMessage(error, "Impossible de charger votre objectif."),
                { cause: error }
            );
        }
    },
};
