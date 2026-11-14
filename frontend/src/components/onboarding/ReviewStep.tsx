import { useOnboarding } from "../../context/OnboardingContext";
import Button from "../../components/ui/Button";
import Card from "../ui/Card";

type ReviewStepProps = {
  onBack: () => void;
  onFinish: () => Promise<void> | void;
  isSubmitting?: boolean;
};

const goalLabels: Record<string, string> = {
  lose_weight: "Perdre du poids",
  maintain_weight: "Maintenir mon poids",
  gain_muscle: "Prendre du muscle",
};

const activityLabels: Record<string, string> = {
  sedentary: "Sédentaire",
  lightly_active: "Légèrement actif",
  moderately_active: "Modérément actif",
  very_active: "Très actif",
  extremely_active: "Extrêmement actif",
};

const sexLabels: Record<string, string> = {
  male: "Homme",
  female: "Femme",
  other: "Autre",
};

export function ReviewStep({
  onBack,
  onFinish,
  isSubmitting = false,
}: ReviewStepProps) {
  const { goalPreview, form, error, completeOnboarding } = useOnboarding();


  const handleSubmit = async (
    event: React.SubmitEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    try {
      const nextStatus = await completeOnboarding();
      if (nextStatus.is_complete) {
        await onFinish();
      }
    } catch {
      // L’erreur est déjà enregistrée dans le contexte.
    }
  };
  

  // Si l'aperçu de l'objectif n'est pas disponible, afficher un message d'erreur et un bouton de retour.
  if (!goalPreview) {
    return (
      <section className="space-y-4">
        <h2 className="mb-4 text-2xl font-bold">
          Récapitulatif
        </h2>

        <p className="text-sm text-red-600">
          L’aperçu de votre objectif n’est pas disponible.
          Retournez à l’étape précédente pour le générer.
        </p>

        <Button
          variant="secondary"
          type="button"
          className="font-bold mt-4 px-8"
          onClick={onBack}
          disabled={isSubmitting}
        >
          Retour
        </Button>
      </section>
    );
  }
  // Affichage du récapitulatif de l'onboarding.
  return (
    <section className="space-y-4">
      <h2 className="mb-4 text-2xl font-bold">
        Récapitulatif
      </h2>
        <form
        className="space-y-4"
        onSubmit={handleSubmit}
        noValidate
        >
          <Card className="w-full p-6 bg-surface">
            <ul className="space-y-2">
              <li>
                <strong>Prénom :</strong>{" "}
                {form.firstName || "Non défini"}
              </li>

              <li>
                <strong>Année de naissance :</strong>{" "}
                {form.birthYear || "Non définie"}
              </li>

              <li>
                <strong>Sexe :</strong>{" "}
                {sexLabels[form.sex] || "Non défini"}
              </li>

              <li>
                <strong>Taille :</strong>{" "}
                {form.heightCm || "Non définie"} cm
              </li>

              <li>
                <strong>Niveau d’activité :</strong>{" "}
                {activityLabels[form.activityLevel] || "Non défini"}
              </li>

              <li>
                <strong>Objectif :</strong>{" "}
                {goalLabels[goalPreview.goal_type] || "Non défini"}
              </li>

              <li>
                <strong>Poids :</strong>{" "}
                {form.currentWeightKg || "Non défini"} kg
              </li>

              <li>
                <strong>Poids cible :</strong>{" "}
                {form.targetWeightKg || "Non défini"} kg
              </li>

              <li>
                <strong>Calories quotidiennes cibles :</strong>{" "}
                {goalPreview.first_target_calories_kcal || "Non défini"} kcal
              </li>

              <li>
                <strong>Durée :</strong>{" "}
                {goalPreview.estimated_weeks || "Non défini"} semaines
              </li>

              <li>
                <strong>Date de fin :</strong>{" "}
                {goalPreview.estimated_completion_date || "Non défini"}
              </li>
            </ul>
          </Card>

          {error ? (
            <p role="alert">
              {error}
            </p>
          ) : null}

          <div className="flex justify-center gap-3">
            <Button
              variant="secondary"
              type="button"
              className="font-bold mt-4 px-8"
              onClick={onBack}
              disabled={isSubmitting}
            >
              Retour
            </Button>

            <Button
              variant="primary"
              type="submit"
              className="font-bold mt-4 px-8"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Enregistrement…" : "Terminer"}
            </Button>
          </div>
        </form>
    </section>
  );
}