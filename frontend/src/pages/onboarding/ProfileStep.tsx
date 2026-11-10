import { useOnboarding } from "../../context/OnboardingContext";

export function ProfileStep() {
    // Récupération des données d'onboarding et de la fonction de mise à jour.
    const { data, updateData } = useOnboarding();

    return (
        <section className="space-y-4">
        <h1 className="text-2xl font-bold">Vos informations</h1>

        {/* Nom */}
        <div>
            <label htmlFor="name" className="mb-1 block">
            Nom
            </label>

            <input
            id="name"
            value={data.firstName}
            onChange={(event) =>
                updateData({ firstName: event.target.value })
            }
            className="w-full rounded-xl border border-gray-300 p-3"
            />
        </div>

        {/* Année de naissance */}
        <div>
            <label htmlFor="birthYear" className="mb-1 block">
            Année de naissance
            </label>

            <input
            id="birthYear"
            type="number"
            min="1900"
            max={new Date().getFullYear()}
            value={data.birthYear}
            onChange={(event) =>
                updateData({ birthYear: event.target.value })
            }
            className="w-full rounded-xl border border-gray-300 p-3"
            />
        </div>

        {/* Sexe */}
        <div>
            <label htmlFor="sex" className="mb-1 block">
            Sexe
            </label>

            <select
            id="sex"
            value={data.sex}
            onChange={(event) =>
                updateData({
                sex: event.target.value as typeof data.sex,
                })
            }
            className="w-full rounded-xl border border-gray-300 p-3"
            >
            <option value="" disabled>
                Sélectionne une option
            </option>

            <option value="male">Homme</option>
            <option value="female">Femme</option>
            <option value="other">Autre</option>
            </select>
        </div>

        {/* Taille et Poids */}
        <div className="grid grid-cols-2 gap-4">
            <div>
            <label htmlFor="heightCm" className="mb-1 block">
                Taille (cm)
            </label>

            <input
                id="heightCm"
                type="number"
                min="100"
                max="250"
                value={data.heightCm}
                onChange={(event) =>
                updateData({ heightCm: event.target.value })
                }
                className="w-full rounded-xl border border-gray-300 p-3"
            />
            </div>

            <div>
            <label htmlFor="weightKg" className="mb-1 block">
                Poids (kg)
            </label>

            <input
                id="weightKg"
                type="number"
                min="30"
                max="300"
                step="0.1"
                value={data.weightKg}
                onChange={(event) =>
                updateData({ weightKg: event.target.value })
                }
                className="w-full rounded-xl border border-gray-300 p-3"
            />
            </div>
        </div>
        </section>
    );
}