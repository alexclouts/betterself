import { useOnboarding } from "../../context/OnboardingContext";
import Button from "../../components/ui/Button";
import Select from "../../components/ui/Select";
import { useState } from "react";
import Input from "../ui/Input";

type GoalStepProps = {
    onBack: () => void;
    onNext: () => void;
    isSubmitting?: boolean;
};

const goals = [
    {
        value: "lose_weight",
        label: "Perdre du poids",
    },
    {
        value: "maintain_weight",
        label: "Maintenir mon poids",
    },
    {
        value: "gain_muscle",
        label: "Prendre du muscle",
    },
];

const paceOptions = [
  {
    value: "slow",
    label: "0,5 lb / semaine",
  },
  {
    value: "moderate",
    label: "1 lb / semaine",
  },
  {
    value: "aggressive",
    label: "1,5 lb / semaine",
  },
];

export function GoalStep({
    onBack,
    onNext,
}: GoalStepProps) {
    const { 
        form, 
        updateForm,
        previewGoal,
        isSubmitting,
        error
    } = useOnboarding();

    // Vérifie si l'objectif sélectionné est un objectif de changement de poids (perte de poids ou gain de muscle)
    const isWeightChangeGoal = form.goalType === "lose_weight" || form.goalType === "gain_muscle";

    const handleSubmit = async (event: React.SubmitEvent<HTMLFormElement>) => {
        event.preventDefault();
    
        try {
            await previewGoal();
            onNext();
        } catch {
        // L’erreur est déjà enregistrée dans le contexte.
        }
    };

  return (
    <form
      className="space-y-4 space-x-4"
      onSubmit={handleSubmit}
    >
      <h2 className="text-2xl font-bold">
        Votre objectif principal
      </h2>

      <div>
        <label
          htmlFor="goal"
          className="mb-2 mt-10 block"
        >
          Choisis ton objectif
        </label>

       <Select
          id="goal"
          name="goal"
          value={form.goalType}
          onChange={(event) => {
            updateForm({
              goalType: event.target.value as typeof form.goalType,
              pace: "",
              targetWeightKg: "",
            });
          }}
          required
        >
          <option value="" disabled>
            Sélectionne un objectif
          </option>

          {goals.map((goal) => (
            <option
              key={goal.value}
              value={goal.value}
            >
              {goal.label}
            </option>
          ))}
        </Select>
      </div>

      <div>
        <label
          htmlFor="currentWeight"
          className="mb-2 block"
        >
          Poids actuel (lb)
        </label>

        <Input
          id="currentWeight"
          name="currentWeight"
          type="number"
          min="1"
          step="0.1"
          value={form.currentWeightKg}
          onChange={(event) => {
            updateForm({
              currentWeightKg: event.target.value,
            });
          }}
          required
        />
      </div>

      {isWeightChangeGoal && (
        <>
          <div>
            <label
              htmlFor="targetWeight"
              className="mb-2 block"
            >
              Poids cible (lb)
            </label>

            <Input
              id="targetWeight"
              name="targetWeight"
              type="number"
              min="1"
              step="0.1"
              value={form.targetWeightKg}
              onChange={(event) => {
                updateForm({
                  targetWeightKg: event.target.value,
                });
              }}
              required
            />
          </div>

          <div>
            <label
              htmlFor="pace"
              className="mb-2 block"
            >
              Rythme souhaité
            </label>

            <Select
              id="pace"
              name="pace"
              value={form.pace}
              onChange={(event) => {
                updateForm({
                  pace: event.target.value as typeof form.pace,
                });
              }}
              required
            >
              <option value="" disabled>
                Sélectionne un rythme
              </option>

              {paceOptions.map((pace) => (
                <option
                  key={pace.value}
                  value={pace.value}
                >
                  {pace.label}
                </option>
              ))}
            </Select>
          </div>
        </>
      )}

        {error && (
            <p className="text-sm text-danger" role="alert">
                {error}
            </p>
        )}

      <div className="flex gap-3 justify-center">
        <Button
          variant="secondary"
          className="font-bold mt-4 px-8"
          onClick={onBack}
          disabled={isSubmitting}
          type="button"
        >
          Retour
        </Button>

        <Button
          variant="primary"
          className="font-bold mt-4 px-8"
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Calcul en cours…" : "Continuer"}
        </Button>
      </div>
    </form>
  );
}