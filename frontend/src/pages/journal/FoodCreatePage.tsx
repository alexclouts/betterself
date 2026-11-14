import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { FoodCategory } from "../../api/generated/foodCategory";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import { formatNutrient } from "../../lib/food";
import { foodService } from "../../services/foodService";
import Card from "../../components/ui/Card";

const CATEGORY_LABELS: Record<FoodCategory, string> = {
  vegetables_and_fruits: "Fruits et légumes",
  cereals: "Céréales",
  meat: "Viandes",
  nuts_and_seeds: "Noix et graines",
  dairy: "Produits laitiers",
  fats_and_oils: "Matières grasses et huiles",
  beverages: "Boissons",
  sweets: "Sucreries",
  prepared_meals: "Plats préparés",
  supplements: "Suppléments",
  other: "Autre",
};

type NumericField =
  | "reference_weight_g"
  | "calories_kcal"
  | "protein_g"
  | "carbohydrates_g"
  | "fat_g";

const NUMERIC_FIELDS: { key: NumericField; label: string; unit: string; max?: number }[] = [
  { key: "reference_weight_g", label: "Portion de référence", unit: "g", max: 100000 },
  { key: "calories_kcal", label: "Calories", unit: "kcal" },
  { key: "protein_g", label: "Protéines", unit: "g", max: 100000 },
  { key: "carbohydrates_g", label: "Glucides", unit: "g", max: 100000 },
  { key: "fat_g", label: "Lipides", unit: "g", max: 100000 },
];

// Accepte la virgule comme séparateur décimal ; NaN si vide ou invalide.
function parseDecimal(value: string): number {
  if (value.trim() === "") 
    return NaN;
    
  return Number(value.replace(",", "."));
}

// Même règle que le backend : calories ≈ 4P + 4G + 9L (tolérance max(10, 10 %)).
function caloriesMatchMacros(calories: number, protein: number, carbs: number, fat: number) {
  const calculated = protein * 4 + carbs * 4 + fat * 9;
  const tolerance = Math.max(10, calculated * 0.1);
  return { 
    calculated, 
    matches: Math.abs(calories - calculated) <= tolerance 
  };
}

export function FoodCreatePage() {
  const navigate = useNavigate();
  const location = useLocation();

  // Préremplit le nom avec la recherche effectuée, si disponible.
  const initialName = (location.state as { name?: string } | null)?.name ?? "";

  const [name, setName] = useState(initialName);
  const [brand, setBrand] = useState("");
  const [category, setCategory] = useState<FoodCategory | "">("");
  const [values, setValues] = useState<Record<NumericField, string>>({
    reference_weight_g: "100",
    calories_kcal: "",
    protein_g: "",
    carbohydrates_g: "",
    fat_g: "",
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Analyse des valeurs numériques saisies.
  const parsed = Object.fromEntries(
    NUMERIC_FIELDS.map(({ key }) => [key, parseDecimal(values[key])]),
  ) as Record<NumericField, number>;


  const fieldErrors = Object.fromEntries(
    // Vérifie chaque champ numérique pour les erreurs.
    NUMERIC_FIELDS.map(({ key, max }) => {
      const value = parsed[key];

      // Si le champ est vide, pas d'erreur.
      if (values[key].trim() === "") 
        return [key, null];

      // Si la valeur n'est pas un nombre fini, erreur.
      if (!Number.isFinite(value)) 
        return [key, "Valeur invalide."];

      // Vérifie que la valeur n'est pas négative (ou strictement positive pour le poids de référence).
      if (key === "reference_weight_g" ? value <= 0 : value < 0)
        return [key, key === "reference_weight_g" ? "Doit être supérieur à 0." : "Ne peut pas être négatif."];
      
      // Vérifie que la valeur ne dépasse pas le maximum autorisé.
      if (max !== undefined && value > max) return [key, `Maximum ${max}.`];
        return [key, null];
    }),
  ) as Record<NumericField, string | null>;

  // Vérifie si tous les champs numériques sont valides.
  const allNumbersValid = NUMERIC_FIELDS.every(({ key }) => 
    values[key].trim() !== "" && fieldErrors[key] === null
  );

  // Vérifie si les macros correspondent aux calories.
  const macroCheck = allNumbersValid ? caloriesMatchMacros(
    parsed.calories_kcal, 
    parsed.protein_g, 
    parsed.carbohydrates_g, 
    parsed.fat_g
  ): null;

  // Vérifie si le formulaire peut être soumis.
  const canSubmit = name.trim() !== "" && allNumbersValid && macroCheck?.matches === true && !isSubmitting;

  function setValue(key: NumericField, value: string) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!canSubmit) 
      return;

    setIsSubmitting(true);
    setError(null);

    try {
      const food = await foodService.createFood({
        name: name.trim(),
        brand: brand.trim() || null,
        category: category || null,
        ...parsed,
      });
      // Enchaîne directement sur l'ajout au journal avec l'aliment créé.
      navigate(`/journal/food/${food.id}`, { replace: true, state: { food } });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Impossible de créer cet aliment.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      <Button type="button" variant="secondary" onClick={() => navigate(-1)} className="text-sm text-gray-500">
        ← Retour
      </Button>

      <h1 className="mt-2 text-xl font-semibold">Créer un aliment</h1>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <label className="block">
          <span className="text-sm font-medium">Nom *</span>
          <Input
            value={name}
            onChange={(event) => setName(event.target.value)}
            maxLength={255}
            className="mt-1"
            required
          />
        </label>

        <label className="block">
          <span className="text-sm font-medium">Marque</span>
          <Input
            value={brand}
            onChange={(event) => setBrand(event.target.value)}
            maxLength={255}
            className="mt-1"
          />
        </label>

        <label className="block">
          <span className="text-sm font-medium">Catégorie</span>
          <Select
            value={category}
            onChange={(event) => setCategory(event.target.value as FoodCategory | "")}
            className="mt-1"
          >
            <option value="">—</option>
            {Object.values(FoodCategory).map((value) => (
              <option key={value} value={value}>
                {CATEGORY_LABELS[value]}
              </option>
            ))}
          </Select>
        </label>

        <Card className="w-full mt-10 bg-surface">
          <fieldset className="space-y-3 p-4">
            <legend className="px-1 text-sm font-bold">
              Valeurs nutritives pour la portion de référence
            </legend>

            {NUMERIC_FIELDS.map(({ key, label, unit }) => (
              <label key={key} className="block">
                <span className="text-sm">
                  {label} ({unit}) *
                </span>
                <Input
                  type="text"
                  inputMode="decimal"
                  value={values[key]}
                  onChange={(event) => setValue(key, event.target.value)}
                  className="mt-1"
                  aria-invalid={fieldErrors[key] !== null}
                />
                {fieldErrors[key] && (
                  <span className="mt-1 block text-sm text-red-600">{fieldErrors[key]}</span>
                )}
              </label>
            ))}

            {macroCheck && !macroCheck.matches && (
              <p className="text-sm text-red-600">
                Les calories ne correspondent pas aux macronutriments (environ{" "}
                {formatNutrient(macroCheck.calculated, 0)} kcal attendues).
              </p>
            )}
        </fieldset>
        </Card>


        {error && <p className="text-sm text-red-600">{error}</p>}

        <Button type="submit" className="w-full mt-2" disabled={!canSubmit}>
          {isSubmitting ? "Création…" : "Créer et ajouter au journal"}
        </Button>
      </form>
    </main>
  );
}
