import { useOnboarding } from "../../context/OnboardingContext";
import Button from "../../components/ui/Button";

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
  const { data, error } = useOnboarding();

  return (
    <section className="space-y-4">
      <h2 className="mb-4 text-2xl font-bold">
        Récapitulatif
      </h2>

      <ul className="space-y-2 mt-10">
        <li>
          <strong>Prénom :</strong>{" "}
          {data.firstName || "Non défini"}
        </li>

        <li>
          <strong>Objectif :</strong>{" "}
          {goalLabels[data.goal] || "Non défini"}
        </li>

        <li>
          <strong>Année de naissance :</strong>{" "}
          {data.birthYear || "Non définie"}
        </li>

        <li>
          <strong>Sexe :</strong>{" "}
          {sexLabels[data.sex] || "Non défini"}
        </li>

        <li>
          <strong>Taille :</strong>{" "}
          {data.heightCm || "Non définie"} cm
        </li>

        <li>
          <strong>Poids :</strong>{" "}
          {data.weightKg || "Non défini"} kg
        </li>

        <li>
          <strong>Niveau d’activité :</strong>{" "}
          {activityLabels[data.activityLevel] || "Non défini"}
        </li>
      </ul>

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
          type="button"
          className="font-bold mt-4 px-8"
          onClick={() => {
            void onFinish();
          }}
          disabled={isSubmitting}
        >
          {isSubmitting ? "Enregistrement…" : "Terminer"}
        </Button>
      </div>
    </section>
  );
}