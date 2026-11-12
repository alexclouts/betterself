import { getOnboarding } from "../api/generated/onboarding/onboarding";

import { getErrorMessage } from "../api/axios";

import type { OnboardingCreate } from "../api/generated/onboardingCreate";
import type { OnboardingStatusRead } from "../api/generated/onboardingStatusRead";
import type { GoalPreviewRead } from "../api/generated/goalPreviewRead";

const DEFAULT_ERROR = "Une erreur est survenue.";


// Récupère le statut actuel de l’onboarding.
export async function getOnboardingStatus(): Promise<OnboardingStatusRead> {
  try {
        const { getOnboardingStatusOnboardingStatusGet } = getOnboarding();
        const response = await getOnboardingStatusOnboardingStatusGet();
    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Impossible de récupérer l’état de l’onboarding.",
      ),
    );
  }
}

// Récupère un aperçu de l’objectif basé sur les informations de l’onboarding.
export async function getGoalPreview(
  payload: OnboardingCreate,
): Promise<GoalPreviewRead> {
  try {
    const { previewGoalOnboardingPreviewPost } = getOnboarding();
    const response = await previewGoalOnboardingPreviewPost(payload);
    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Impossible de calculer l’aperçu de votre objectif.",
      )
    );
  }
}

// Envoie les informations de l’onboarding pour le compléter.
export async function completeOnboarding(
  payload: OnboardingCreate,
): Promise<OnboardingStatusRead> {
  try {
    const { completeOnboardingOnboardingPost } = getOnboarding();
    const response = await completeOnboardingOnboardingPost(payload);
    return response.data;

  } catch (error) {
    throw new Error(
        getErrorMessage(  
            error,
            "Impossible de compléter l’onboarding.",
        )
    );
  }
}