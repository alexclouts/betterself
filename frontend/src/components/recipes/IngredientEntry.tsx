import { useState } from "react";
import { NutritionFactsCard } from "../food/NutritionFactsCard";
import Button from "../ui/Button";
import Input from "../ui/Input";
import { computeNutrientsForQuantity, formatNutrient } from "../../lib/food";
import {
  formatQuantityInput,
  parseDecimal,
  validateWeight,
  type PickedFood,
} from "../../lib/recipe";

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
  const [quantityInput, setQuantityInput] = useState(() => formatQuantityInput(initialQuantityG));
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const quantityError = validateWeight(quantityInput);
  const quantityG = parseDecimal(quantityInput);
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
      <Button type="button" variant="secondary" onClick={onBack} className="text-sm">
        ← Retour
      </Button>

      <h1>{food.name}</h1>
      {food.brand && <p>{food.brand}</p>}

      <p className="mt-1">
        {food.serving_g
          ? `Portion suggérée : ${formatNutrient(food.serving_g)} g`
          : `Portion de référence : ${formatNutrient(food.reference_weight_g)} g`}
      </p>

      <NutritionFactsCard nutrients={nutrients} className="mt-6" />

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <label className="block">
          <span className="text-sm font-medium">Quantité (g)</span>
          <Input
            type="text"
            inputMode="decimal"
            value={quantityInput}
            onChange={(event) => setQuantityInput(event.target.value)}
            className="mt-1"
            aria-invalid={quantityError !== null}
            autoFocus
          />
          {quantityError && quantityInput.trim() !== "" && (
            <span className="mt-1 block text-sm text-danger">
              {quantityError}
            </span>
          )}
        </label>

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
