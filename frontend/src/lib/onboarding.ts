import type { OnboardingCreate } from "../api/generated/onboardingCreate";
import type { OnboardingFormState,} from "../context/OnboardingContext";

/**
 * Librairie pour la gestion de l’onboarding.
 */

const LB_TO_KG = 0.45359237;

export function poundsToKilograms(pounds: number): number {
  return Number((pounds * LB_TO_KG).toFixed(2));
}

export function buildOnboardingCreate(
    form: OnboardingFormState,
): OnboardingCreate {
    return {
        goal_type: form.goalType as OnboardingCreate["goal_type"],
        pace: form.pace === ""? null: (form.pace as NonNullable<OnboardingCreate["pace"]>),
        first_name: form.firstName,
        birth_year: Number(form.birthYear),
        sex: form.sex as OnboardingCreate["sex"],
        height_cm: Number(form.heightCm),
        current_weight_kg: poundsToKilograms(Number(form.currentWeightKg),),
        target_weight_kg: poundsToKilograms(Number(form.targetWeightKg),),
        activity_level:
        form.activityLevel as OnboardingCreate["activity_level"],
    };
}