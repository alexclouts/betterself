import { useOnboarding } from "../../context/OnboardingContext";
import Button from "../../components/ui/Button";
import Select from "../../components/ui/Select";

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

export function GoalStep({
    onBack,
    onNext,
    isSubmitting = false,
}: GoalStepProps) {
    const { data, updateData } = useOnboarding();

    const isGoalSelected = data.goal !== "";

    function handleSubmit(event: React.SubmitEvent<HTMLFormElement>) {
        event.preventDefault();

        if (!isGoalSelected || isSubmitting) {
            return;
        }
        onNext();
    }

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
            value={data.goal}
            onChange={(event) =>
                updateData({
                    goal: event.target.value as typeof data.goal,
                })
            }
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

        <div className="flex gap-3 justify-center">
            <Button
            variant="secondary"
            className="font-bold mt-4 px-8"
            onClick={onBack}
            disabled={isSubmitting}
            >
            Retour
            </Button>

            <Button
            variant="primary"
            className="font-bold mt-4 px-8"
            type="submit"
            disabled={!isGoalSelected || isSubmitting}
            >
            {isSubmitting ? "Enregistrement…" : "Continuer"}
            </Button>
        </div>
        </form>
  );
}