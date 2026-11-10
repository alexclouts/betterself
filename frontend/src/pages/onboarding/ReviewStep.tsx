import { useOnboarding } from "../../context/OnboardingContext";
import Button from "../../components/Button";
import { onboardingService } from "../../services/onboardingService";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

const goalLabels: Record<string, string> = {
  lose_weight: "Perdre du poids",
  maintain_weight: "Maintenir mon poids",
  gain_muscle: "Prendre du muscle",
};

export function ReviewStep() {

    // Récupération de la navigation pour rediriger l'utilisateur après la complétion.
    const navigate = useNavigate();

    // Récupération des données d'onboarding et de la fonction de réinitialisation.
    const { data, resetOnboarding } = useOnboarding();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Fonction pour gérer la complétion de l'onboarding.
    async function handleFinish() {
        setIsLoading(true);
        setError(null);

        try {
            await onboardingService.completeOnboarding({
                goal: data.goal,
                firstName: data.firstName,
                lastName: data.lastName,
                birthDate: data.birthDate,
                sex: data.sex,
                heightCm: Number(data.heightCm),
                weightKg: Number(data.weightKg),
            });
            resetOnboarding();
            navigate("/", { replace: true });

        } catch (err) {
            setError(
                err instanceof Error
                ? err.message
                : "Impossible d’enregistrer votre profil."
            );
        } finally {
            setIsLoading(false);
        }
    }

    return (
        <section>
        <h1 className="mb-4 text-2xl font-bold">Récapitulatif</h1>

        {/* Récapitulatif des informations de l'utilisateur */}
        <ul className="space-y-2">
            <li>
            <strong>Objectif :</strong> {goalLabels[data.goal] || "Non défini"}
            </li>
            <li>
            <strong>Nom :</strong> {data.name || "Non défini"}
            </li>
            <li>
            <strong>Année de naissance :</strong>{" "}
            {data.birthYear || "Non définie"}
            </li>
            <li>
            <strong>Taille :</strong> {data.heightCm || "Non définie"} cm
            </li>
            <li>
            <strong>Poids :</strong> {data.weightKg || "Non défini"} kg
            </li>
            <li>
            <strong>Niveau d'activité :</strong> {data.activityLevel || "Non défini"}
            </li>
        </ul>

        {error && <p role="alert">{error}</p>}

        <Button
            variant="primary"
            onClick={handleFinish}
            disabled={isLoading}
        >
            {isLoading ? "Enregistrement..." : "Terminer"}
        </Button>
        </section>
    );
}