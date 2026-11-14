import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";

import { onboardingService} from "../services/onboardingService";

import type { OnboardingStatusRead } from "../api/generated/onboardingStatusRead";
import type { GoalPreviewRead } from "../api/generated/goalPreviewRead";
import type { GoalType } from "../api/generated/goalType";
import type { GoalPace } from "../api/generated/goalPace";
import type { Sex } from "../api/generated/sex";
import type { ActivityLevel } from "../api/generated/activityLevel";

import { useAuthStore } from "../stores/authStore";
import { buildOnboardingCreate } from "../lib/onboarding";

export type OnboardingStep =
  | "profile"
  | "goal"
  | "review";

// État du formulaire d’onboarding.
export type OnboardingFormState = {
    goalType: GoalType | "";
    pace: GoalPace | "";
    firstName: string;
    birthYear: string;
    sex: Sex | "";
    heightCm: string;
    currentWeightKg: string;
    targetWeightKg: string;
    activityLevel: ActivityLevel | "";
};

type OnboardingContextValue = {
    form: OnboardingFormState;
    status: OnboardingStatusRead | null;
    goalPreview: GoalPreviewRead | null;
    currentStep: OnboardingStep;
    isLoadingStatus: boolean;
    isSubmitting: boolean;
    error: string | null;

    updateForm: (
        patch: Partial<OnboardingFormState>,
    ) => void;

    setCurrentStep: (step: OnboardingStep) => void;
    refreshStatus: () => Promise<OnboardingStatusRead>;
    previewGoal: () => Promise<GoalPreviewRead>;
    completeOnboarding: () => Promise<OnboardingStatusRead>;
    resetOnboarding: () => void;
};

// État initial du formulaire d’onboarding.
const initialForm: OnboardingFormState = {
  goalType: "",
  pace: "",
  firstName: "",
  birthYear: "",
  sex: "",
  heightCm: "",
  currentWeightKg: "",
  targetWeightKg: "",
  activityLevel: "",
};

// Étape initiale de l’onboarding.
const initialStep: OnboardingStep = "profile";

const OnboardingContext = createContext<OnboardingContextValue | null>(
  null,
);

// Fournit le contexte pour l’onboarding, incluant l’état du formulaire, le statut, l’aperçu de l’objectif et les actions associées.
export function OnboardingProvider({
  children,
}: {
  children: ReactNode;
}) {
    const [form, setForm] = useState<OnboardingFormState>(initialForm);
    const [status, setStatus] = useState<OnboardingStatusRead | null>(null);
    const [goalPreview, setGoalPreview] = useState<GoalPreviewRead | null>(
        null,
    );
    const [currentStep, setCurrentStep] = useState<OnboardingStep>(
        initialStep,
    );
    const [isLoadingStatus, setIsLoadingStatus] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const updateForm = useCallback(
        (patch: Partial<OnboardingFormState>) => {
        setForm((current) => ({
            ...current,
            ...patch,
        }));
        },
        [],
    );

    // Rafraîchit le statut de l’onboarding.
    const refreshStatus = useCallback(async (): Promise<OnboardingStatusRead> => {
        const accessToken = useAuthStore.getState().accessToken;

        if (!accessToken) {
            throw new Error("Utilisateur non authentifié.");
        }
        setIsLoadingStatus(true);
        setError(null);

        try {
            const nextStatus = await onboardingService.getOnboardingStatus();
            console.log("Refreshing onboarding status:");
            setStatus(nextStatus);
            return nextStatus;

        } catch (caughtError) {
            const message =
                caughtError instanceof Error? caughtError.message: "Impossible de récupérer l’état de l’onboarding.";

            setError(message);
            throw caughtError;
        } finally {
            setIsLoadingStatus(false);
        }
    }, []);

    // Prévisualise l’objectif basé sur le formulaire actuel.
    const previewGoal = useCallback(async (): Promise<GoalPreviewRead> => {
        setIsSubmitting(true);
        setError(null);

        try {
            const payload = buildOnboardingCreate(form);
            const preview = await onboardingService.getGoalPreview(payload);

            setGoalPreview(preview);
            return preview;

        } catch (caughtError) {
            const message =
                caughtError instanceof Error? caughtError.message: "Impossible de calculer l’aperçu de votre objectif.";

            setError(message);
            throw caughtError;

        } finally {
            setIsSubmitting(false);
        }
    }, [form]);

    const submitOnboarding = useCallback(
        async (): Promise<OnboardingStatusRead> => {
            setIsSubmitting(true);
            setError(null);

            try {
                const payload = buildOnboardingCreate(form);
                const nextStatus = await onboardingService.completeOnboarding(payload);

                setStatus(nextStatus);
                return nextStatus;

            } catch (caughtError) {
                const message = caughtError instanceof Error? caughtError.message :"Impossible de compléter l’onboarding.";

            setError(message);
                throw caughtError;
            } finally {
                setIsSubmitting(false);
            }
        },  
        [form],
    );
        // Réinitialise l’onboarding à son état initial.
    const resetOnboarding = useCallback(() => {
        setForm(initialForm);
        setStatus(null);
        setGoalPreview(null);
        setCurrentStep(initialStep);
        setError(null);
    }, []);

    // Valeur du contexte à fournir aux composants enfants.
    const value = useMemo(
        () => ({
        form,
        status,
        goalPreview,
        currentStep,
        isLoadingStatus,
        isSubmitting,
        error,

        updateForm,
        setCurrentStep,
        refreshStatus,
        previewGoal,
        completeOnboarding: submitOnboarding,
        resetOnboarding,
        }),
        [
        form,
        status,
        goalPreview,
        currentStep,
        isLoadingStatus,
        isSubmitting,
        error,

        updateForm,
        refreshStatus,
        previewGoal,
        submitOnboarding,
        resetOnboarding,
        ],
    );

    return (
        <OnboardingContext.Provider value={value}>
        {children}
        </OnboardingContext.Provider>
    );
}

// Hook personnalisé pour accéder au contexte de l’onboarding.
export function useOnboarding() {
    const context = useContext(OnboardingContext);

    if (!context) {
        throw new Error(
        "useOnboarding doit être utilisé dans un OnboardingProvider.",
        );
    }

    return context;
}