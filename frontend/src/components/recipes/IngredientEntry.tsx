import { useState } from "react";
import { NutritionFactsCard } from "../food/NutritionFactsCard";
import Button from "../ui/Button";
import { computeNutrientsForQuantity, hasInconsistentCalories } from "../../lib/food";
import {
  formatQuantityInput,
  parseDecimal,
  validateGrams,
  type PickedFood,
} from "../../lib/recipe";
import { PageHeader } from "../navigation/PageHeader";
import { QuantityField } from "../ui/QuantityField";
import {
  convertAmount,
  foodUnitOptions,
  getFoodUnit,
  hasValidPrecision,
  initialQuantity,
  toGrams,
  unitWeightHint,
  type QuantityUnit,
} from "../../lib/units";
import { FoodSubtitle } from "../food/FoodSubtitle";

type IngredientEntryProps = {
  food: PickedFood;
  initialQuantityG: number;
  // Ingrédient déjà dans la recette : on modifie sa quantité.
  isEditing?: boolean;
  // Une promesse rejetée affiche son message.
  onSubmit: (quantityG: number) => void | Promise<unknown>;
  onBack: () => void;
};

/*
 * Fiche d'un ingrédient, sur le modèle de l'ajout d'un aliment au journal :
 * valeurs nutritionnelles pour la quantité saisie, sans choix de repas.
 */
export function IngredientEntry({
  food,
  initialQuantityG,
  isEditing = false,
  onSubmit,
  onBack,
}: IngredientEntryProps) {
  const foodUnit = getFoodUnit(food);
  const unitG = foodUnit?.grams ?? 0;
  // Dans l'unité de l'aliment si la quantité y tombe (« 2 tranches »), sinon en grammes.
  const [initial] = useState(() => initialQuantity(initialQuantityG, foodUnit?.grams ?? null));
  const [unit, setUnit] = useState<QuantityUnit>(initial.unit);
  const [quantityInput, setQuantityInput] = useState(() => formatQuantityInput(initial.amount));
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // La quantité saisie, toujours ramenée en grammes.
  const amount = parseDecimal(quantityInput);
  const quantityG = toGrams(amount, unit, unitG);
  const quantityError = !Number.isFinite(amount)
    ? "Valeur invalide."
    : hasValidPrecision(amount, unit)
      ? validateGrams(quantityG)
      : "Deux décimales au plus.";

  // Changer d'unité convertit la valeur saisie pour garder la même quantité.
  function changeUnit(next: QuantityUnit) {
    if (next === unit) return;
    if (Number.isFinite(amount) && amount > 0) {
      setQuantityInput(formatQuantityInput(convertAmount(amount, unit, next, unitG)));
    }
    setUnit(next);
  }
  const nutrients = quantityError === null ? computeNutrientsForQuantity(food, quantityG) : null;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (quantityError !== null) return;

    setIsSubmitting(true);
    setError(null);
    try {
      await onSubmit(quantityG);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Impossible d’enregistrer cet ingrédient.");
      setIsSubmitting(false);
    }
  }

  return (
    <>
      {/* Un nouvel ingrédient revient à la recherche, un ingrédient existant à la recette. */}
      <PageHeader
        onBack={onBack}
        backLabel={isEditing ? "Retour à la recette" : "Retour à la recherche"}
      />

      <h1>{food.name}</h1>
      <FoodSubtitle
        brand={food.brand}
        serving_g={food.serving_g}
        reference_weight_g={food.reference_weight_g}
        unit_name={food.unit_name}
        unit_name_plural={food.unit_name_plural}
        unit_g={food.unit_g}
      />

      <NutritionFactsCard
        nutrients={nutrients}
        showCalorieWarning={hasInconsistentCalories(food)}
        showWeightWarning={food.weight_is_estimated}
        className="mt-6"
      />

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <QuantityField
          value={quantityInput}
          onChange={setQuantityInput}
          unit={unit}
          units={foodUnitOptions(foodUnit, amount)}
          onUnitChange={changeUnit}
          error={quantityError && quantityInput.trim() !== "" ? quantityError : null}
          hint={
            unit === "unit" && foodUnit && quantityError === null
              ? unitWeightHint(foodUnit, amount, food.weight_is_estimated)
              : null
          }
          autoFocus
        />

        {error && (
          <p className="text-danger" role="alert">
            {error}
          </p>
        )}

        <Button
          type="submit"
          className="w-full mt-2 font-bold"
          disabled={quantityError !== null || isSubmitting}
        >
          {isEditing
            ? isSubmitting ? "Modification…" : "Modifier l’ingrédient"
            : isSubmitting ? "Ajout…" : "Ajouter à la recette"}
        </Button>
      </form>
    </>
  );
}
