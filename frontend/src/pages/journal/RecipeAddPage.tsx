import { useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { FoodConsumptionCreate } from "../../api/generated/foodConsumptionCreate";
import type { RecipeRead } from "../../api/generated/recipeRead";
import { MealType } from "../../api/generated/mealType";
import { NutritionFactsCard } from "../../components/food/NutritionFactsCard";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import { useRecipe } from "../../hooks/useRecipe";
import { consumedAtForDay, formatDayLabel, todayKey } from "../../lib/date";
import { formatNutrient, getDefaultMealType, MEAL_TYPE_LABELS } from "../../lib/food";
import { journalUrl, readJournalNavState } from "../../lib/journal";
import { queryKeys } from "../../lib/queryClient";
import {
  formatCount,
  formatQuantityInput,
  parseDecimal,
  recipeNutrientsForQuantity,
  servingWeightG,
} from "../../lib/recipe";
import { journalService } from "../../services/journalService";

// Quantité maximale acceptée par l'API pour une consommation.
const MAX_QUANTITY_G = 5000;

type QuantityUnit = "servings" | "grams";

/*
 * Ajout d'une recette au journal. La quantité se saisit en portions ou en
 * grammes; l'API reçoit toujours des grammes et calcule l'instantané nutritionnel.
 */
export function RecipeAddPage() {
  const navigate = useNavigate();
  const { recipeId } = useParams<{ recipeId: string }>();
  const { recipe, isLoading, error } = useRecipe(recipeId);

  if (recipe) {
    return <RecipeAddForm key={recipe.id} recipe={recipe} />;
  }

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      {isLoading ? (
        <p>Chargement de la recette…</p>
      ) : (
        <>
          <p className="text-danger" role="alert">
            {error ?? "Recette introuvable."}
          </p>
          <Button variant="ghost" className="mt-4" onClick={() => navigate("/journal/add")}>
            Retour à la recherche
          </Button>
        </>
      )}
    </main>
  );
}

function RecipeAddForm({ recipe }: { recipe: RecipeRead }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const location = useLocation();
  const journalState = readJournalNavState(location.state);
  const dayKey = journalState.date ?? todayKey();

  const portionG = servingWeightG(recipe);
  const [unit, setUnit] = useState<QuantityUnit>("servings");
  const [quantityInput, setQuantityInput] = useState("1");
  const [mealType, setMealType] = useState<MealType>(
    () => journalState.mealType ?? getDefaultMealType(),
  );

  // La quantité saisie, toujours ramenée en grammes.
  const amount = parseDecimal(quantityInput);
  const quantityG = unit === "servings" ? amount * portionG : amount;
  const isQuantityValid = Number.isFinite(quantityG) && quantityG > 0 && quantityG <= MAX_QUANTITY_G;
  const nutrients = isQuantityValid ? recipeNutrientsForQuantity(recipe, quantityG) : null;

  // Changer d'unité convertit la valeur saisie pour garder la même quantité.
  function changeUnit(next: QuantityUnit) {
    if (next === unit) return;
    if (Number.isFinite(amount) && amount > 0 && portionG > 0) {
      const converted = next === "grams" ? amount * portionG : amount / portionG;
      setQuantityInput(formatQuantityInput(Math.round(converted * 100) / 100));
    }
    setUnit(next);
  }

  const addMutation = useMutation({
    mutationFn: (payload: FoodConsumptionCreate) => journalService.addEntry(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.journal.all });
      navigate(journalUrl(dayKey), { replace: true });
    },
  });

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!isQuantityValid || addMutation.isPending) return;
    addMutation.mutate({
      recipe_id: recipe.id,
      // L'API accepte au plus deux décimales.
      quantity_g: Math.round(quantityG * 100) / 100,
      meal_type: mealType,
      consumed_at: consumedAtForDay(dayKey),
    });
  }

  const maxInUnit =
    unit === "servings" && portionG > 0
      ? `${formatNutrient(MAX_QUANTITY_G / portionG)} portions`
      : `${formatNutrient(MAX_QUANTITY_G)} g`;

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      <Button
        type="button"
        variant="secondary"
        onClick={() => navigate(-1)}
        className="text-sm text-gray-500"
      >
        ← Retour
      </Button>

      <h1 className="break-words">{recipe.name}</h1>
      <p className="mt-1">
        Recette · {formatCount(recipe.servings, "portion", "portions")} de{" "}
        {formatNutrient(portionG, 0)} g
      </p>

      <NutritionFactsCard nutrients={nutrients} className="mt-6" />
      {dayKey !== todayKey() && (
        <p className="mt-1">Ajout au journal de : {formatDayLabel(dayKey).toLowerCase()}</p>
      )}

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <div>
          <div className="flex items-baseline justify-between gap-3">
            <label htmlFor="recipe-quantity" className="text-sm font-medium">
              Quantité ({unit === "servings" ? "portions" : "g"})
            </label>
            {/* Choix de l'unité de saisie. */}
            <div role="group" aria-label="Unité" className="flex rounded-full border border-border p-0.5 text-sm">
              {(["servings", "grams"] as const).map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => changeUnit(option)}
                  aria-pressed={unit === option}
                  className={`rounded-full px-3 py-0.5 ${
                    unit === option ? "bg-primary text-white" : "text-muted hover:text-foreground"
                  }`}
                >
                  {option === "servings" ? "Portions" : "Grammes"}
                </button>
              ))}
            </div>
          </div>
          <Input
            id="recipe-quantity"
            type="text"
            inputMode="decimal"
            value={quantityInput}
            onChange={(event) => setQuantityInput(event.target.value)}
            className="mt-1"
            aria-invalid={!isQuantityValid}
          />
          {isQuantityValid && unit === "servings" && (
            <span className="mt-1 block text-sm text-muted">{formatNutrient(quantityG, 0)} g</span>
          )}
          {!isQuantityValid && quantityInput.trim() !== "" && (
            <span className="mt-1 block text-sm text-red-600">
              Entrez une quantité supérieure à 0 et d’au plus {maxInUnit}.
            </span>
          )}
        </div>

        <label className="block">
          <span className="text-sm font-medium">Repas</span>
          <Select
            value={mealType}
            onChange={(event) => setMealType(event.target.value as MealType)}
            className="mt-1"
          >
            {Object.values(MealType).map((type) => (
              <option key={type} value={type}>
                {MEAL_TYPE_LABELS[type]}
              </option>
            ))}
          </Select>
        </label>

        {addMutation.error && (
          <p className="text-danger" role="alert">
            {addMutation.error.message}
          </p>
        )}

        <Button
          type="submit"
          className="mt-2 w-full font-bold"
          disabled={!isQuantityValid || addMutation.isPending}
        >
          {addMutation.isPending ? "Ajout…" : "Ajouter au journal"}
        </Button>
      </form>
    </main>
  );
}
