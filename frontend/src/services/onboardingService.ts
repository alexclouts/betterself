import type { GoalPace, OnboardingStatusResponse } from "../context/OnboardingContext";
import { getOnboarding } from "../api/generated/onboarding/onboarding";
import { getErrorMessage } from "../api/axios";
import type { GoalType } from "../api/generated/goalType";

const API_URL = import.meta.env.VITE_API_URL;

/**
 * Service pour gérer l'onboarding de l'utilisateur.
 */
export const onboardingService = {
    // Complète l'onboarding de l'utilisateur avec les informations fournies.
    async completeOnboarding(payload: {
        goal: GoalType;
        pace: GoalPace;
        name: string;
        birthYear: string;
        sex: string;
        heightCm: number;
        currentWeightKg: number;
        targetWeightKg: number;
    }) {
        try {
            const { completeOnboardingOnboardingPost } = getOnboarding();
            await completeOnboardingOnboardingPost(payload);
        }
        catch (error) {
            throw new Error(getErrorMessage(error, "Impossible de compléter l’onboarding."));
        }
    }
};

export async function getOnboardingStatus(): Promise<OnboardingStatusResponse> {
    try {
        const { getOnboardingStatusOnboardingStatusGet } = getOnboarding();
        return await getOnboardingStatusOnboardingStatusGet();
    } catch (error) {
        throw new Error(getErrorMessage(error, "Impossible de récupérer le statut d’onboarding."));
    }
}