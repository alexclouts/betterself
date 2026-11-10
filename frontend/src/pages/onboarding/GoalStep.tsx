import { useOnboarding } from "../../context/OnboardingContext";

// Liste des objectifs disponibles pour l'utilisateur.
const goals = [
    { value: "lose_weight", label: "Perdre du poids" },
    { value: "maintain_weight", label: "Maintenir mon poids" },
    { value: "gain_muscle", label: "Prendre du muscle" },
];

export function GoalStep() {
    // Récupération des données d'onboarding et de la fonction de mise à jour.
    const { data, updateData } = useOnboarding();

    return (
        <section>
        <h1 className="mb-4 text-2xl font-bold">
            Quel est ton objectif principal ?
        </h1>

        <label htmlFor="goal" className="mb-2 block">
            Choisis ton objectif
        </label>

        {/* Sélecteur d'objectif principal */}
        <select
            id="goal"
            name="goal"
            value={data.goal}
            onChange={(event) =>
            updateData({
                goal: event.target.value as typeof data.goal,
            })
            }
            className="w-full rounded-xl border border-gray-300 p-3"
        >
            <option value="" disabled>
            Sélectionne un objectif
            </option>

            {goals.map((goal) => (
            <option key={goal.value} value={goal.value}>
                {goal.label}
            </option>
            ))}
        </select>
        </section>
    );
}