import { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";

/**
 * Contexte pour gérer l'état de l'onboarding de l'utilisateur.
 */

// Types pour les objectifs et les données d'onboarding.
export type Goal = "lose_weight" | "maintain_weight" | "gain_muscle";
export type ActivityLevel = "sedentary" | "lightly_active" | "moderately_active" | "very_active" | "extremely_active" | ""; 

export type OnboardingData = {
  goal: Goal | "";
  name: string;
  birthYear: string;
  sex: "male" | "female" | "other" | "";
  heightCm: string;
  weightKg: string;
  activityLevel: ActivityLevel | ""; 
};

type OnboardingContextValue = {
  data: OnboardingData;
  updateData: (patch: Partial<OnboardingData>) => void;
  resetOnboarding: () => void;
};

const initialData: OnboardingData = {
  goal: "",
  name: "",
  birthYear: "",
  sex: "",
  heightCm: "",
  weightKg: "",
  activityLevel: "",
};

// Création du contexte d'onboarding.
const OnboardingContext = createContext<OnboardingContextValue | null>(null);

export function OnboardingProvider({ children }: { children: ReactNode }) {
    // État local pour stocker les données d'onboarding.
    const [data, setData] = useState<OnboardingData>(initialData);

    function updateData(patch: Partial<OnboardingData>) {
        setData((current) => ({
        ...current,
        ...patch,
        }));
    }

    function resetOnboarding() {
        setData(initialData);
    }

    return (
        <OnboardingContext.Provider
        value={{ data, updateData, resetOnboarding }}
        >
        {children}
        </OnboardingContext.Provider>
    );
}

// Hook personnalisé pour accéder au contexte d'onboarding.
export function useOnboarding() {
    const context = useContext(OnboardingContext);

    if (!context) {
        throw new Error(
        "useOnboarding doit être utilisé dans un OnboardingProvider."
        );
    }
    return context;
}