import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";

import { useAuthStore } from "../stores/authStore";
import { getOnboardingStatus } from "../services/onboardingService";    
import { api } from "../api/axios";


// Types et contexte pour la gestion de l'onboarding utilisateur.a
export type GoalType =
  | "lose_weight"
  | "maintain_weight"
  | "gain_muscle";

export type GoalPace =
  | "slow"
  | "moderate"
  | "aggressive";

export type ActivityLevel =
  | "sedentary"
  | "lightly_active"
  | "moderately_active"
  | "very_active"
  | "extremely_active";

export type Sex = "male" | "female" | "other";

export type OnboardingStep =
  | "profile"
  | "goal"
  | "review";

// Réponse de l'API pour le statut de l'onboarding.
export type OnboardingStatusResponse = {
    is_complete: boolean;
    missing_steps: string[];
};


// Données collectées lors de l'onboarding utilisateur.
export type OnboardingData = {
    goal: GoalType | "";
    pace: GoalPace | "";
    firstName: string;
    birthYear: string;
    sex: Sex | "";
    heightCm: string;
    currentWeightKg: string;
    targetWeightKg: string;
    activityLevel: ActivityLevel | "";
};

// Statut de l'onboarding utilisateur.
export type OnboardingStatus = {
    isComplete: boolean;
    missingSteps: string[];
};

// Contexte et fonctions pour gérer l'onboarding utilisateur.
type OnboardingContextValue = {
    data: OnboardingData;
    status: OnboardingStatus | null;
    currentStep: OnboardingStep;
    isLoadingStatus: boolean;
    isSubmitting: boolean;
    error: string | null;

    updateData: (patch: Partial<OnboardingData>) => void;
    setCurrentStep: (step: OnboardingStep) => void;
    refreshStatus: () => Promise<OnboardingStatus>;
    submitProfile: () => Promise<boolean>;
    submitGoal: () => Promise<boolean>;
    completeOnboarding: () => Promise<boolean>;
    resetOnboarding: () => void;
};

// Valeurs initiales pour l'onboarding utilisateur.
const initialData: OnboardingData = {
    goal: "",
    pace: "",
    firstName: "",
    birthYear: "",
    sex: "",
    heightCm: "",
    currentWeightKg: "",
    targetWeightKg: "",
    activityLevel: "",
};

const initialStep: OnboardingStep = "profile";

const OnboardingContext = createContext<OnboardingContextValue | null>(null);

/*
 * Fournit le contexte et le fournisseur pour l'onboarding utilisateur.
 */
export function OnboardingProvider({
  children,
}: {
    children: ReactNode;
    }) {
        // États locaux pour l'onboarding utilisateur.
        const [data, setData] = useState<OnboardingData>(initialData);
        const [status, setStatus] = useState<OnboardingStatus | null>(null);
        const [currentStep, setCurrentStep] = useState<OnboardingStep>(initialStep);
        const [isLoadingStatus, setIsLoadingStatus] = useState(true);
        const [isSubmitting, setIsSubmitting] = useState(false);
        const [error, setError] = useState<string | null>(null);

        // Met à jour les données d'onboarding avec un patch partiel.
        const updateData = useCallback((patch: Partial<OnboardingData>) => {
            setData((current) => ({
                ...current,
                ...patch,
            }));
        },
        []
    );

        // Rafraîchit le statut de l'onboarding utilisateur.
    const refreshStatus = useCallback(async (): Promise<OnboardingStatus> => {
        const accessToken = useAuthStore.getState().accessToken;

        if (!accessToken) {
            throw new Error("Utilisateur non authentifié.");
        }

        setIsLoadingStatus(true);
        setError(null);

        try {
            const response = await getOnboardingStatus(accessToken);

            const nextStatus: OnboardingStatus = {
                isComplete: response.is_complete,
                missingSteps: response.missing_steps,
        };

        setStatus(nextStatus);

        return nextStatus;
        } catch (error) {
            setError(
                error instanceof Error
                ? error.message
                : "Impossible de récupérer l'état de l'onboarding."
            );

            throw error;
        } finally {
            setIsLoadingStatus(false);
        }
        },
  []
);


    // Soumet les informations du profil utilisateur.
    const submitProfile = useCallback(async () => {
        setIsSubmitting(true);
        setError(null);

        try {
            await api.post("/profiles", {
                first_name: data.firstName,
                year_of_birth: Number(data.birthYear),
                sex: data.sex,
                height_cm: Number(data.heightCm),
                activity_level: data.activityLevel,
            });
            await refreshStatus();
            return true;
        } catch {
            setError("Impossible d'enregistrer votre profil.");
            return false;
        } finally {
            setIsSubmitting(false);
        }
    }, [data, refreshStatus]);

    // Soumet l'objectif nutritionnel de l'utilisateur.
    const submitGoal = useCallback(async () => {
        setIsSubmitting(true);
        setError(null);

        try {
            await api.post("/goal-targets/recalculate", {
                reference_weight_kg: Number(data.weightKg),
                sex: data.sex,
                birth_year: Number(data.birthYear),
                height_cm: Number(data.heightCm),
                activity_level: data.activityLevel,
            });
            await refreshStatus();
            return true;

        } catch {
            setError("Impossible de calculer votre objectif nutritionnel.");
            return false;
            
        } finally {
            setIsSubmitting(false);
        }
    }, [data, refreshStatus]);

    // Marque l'onboarding comme complet.
    const completeOnboarding = useCallback(async () => {
        await refreshStatus();
        return status?.isComplete ?? false;
    }, [refreshStatus, status]);

    // Réinitialise l'onboarding utilisateur.
    const resetOnboarding = useCallback(() => {
        setData(initialData);
        setStatus(null);
        setCurrentStep(initialStep);
        setError(null);
    }, []);

    // Valeur du contexte pour l'onboarding utilisateur.
    const value = useMemo(
        () => ({
        data,
        status,
        currentStep,
        isLoadingStatus,
        isSubmitting,
        error,

        updateData,
        setCurrentStep,
        refreshStatus,
        submitProfile,
        submitGoal,
        completeOnboarding,
        resetOnboarding,
        }),
        [
        data,
        status,
        currentStep,
        isLoadingStatus,
        isSubmitting,
        error,

        updateData,
        refreshStatus,
        submitProfile,
        submitGoal,
        completeOnboarding,
        resetOnboarding,
        ]
    );

    return (
        <OnboardingContext.Provider value={value}>
        {children}
        </OnboardingContext.Provider>
    );
}

// Hook pour accéder au contexte d'onboarding utilisateur.
export function useOnboarding() {
  const context = useContext(OnboardingContext);

  if (!context) {
    throw new Error(
      "useOnboarding doit être utilisé dans un OnboardingProvider."
    );
  }

  return context;
}