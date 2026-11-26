import { useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { FoodConsumptionRead } from "../../api/generated/foodConsumptionRead";
import type { RecipeRead } from "../../api/generated/recipeRead";
import { MealType } from "../../api/generated/mealType";
import { NutritionFactsCard } from "../../components/food/NutritionFactsCard";
import { RecipeIngredientsDetails } from "../../components/recipes/RecipeIngredientsDetails";
import Button from "../../components/ui/Button";
import { QuantityField } from "../../components/ui/QuantityField";
import Select from "../../components/ui/Select";
import { useRecipe } from "../../hooks/useRecipe";
import { consumedAtForDay, formatDayLabel, toDateKey, todayKey } from "../../lib/date";
import {
  formatNutrient,
  getDefaultMealType,
  hasAtMostTwoDecimals,
  MEAL_TYPE_LABELS,
  toNumber,
  type FoodNutrients,
} from "../../lib/food";
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
import { PageHeader } from "../../components/navigation/PageHeader";

// Quantité maximale acceptée par l'API pour une consommation.
const MAX_QUANTITY_G = 5000;

// Écart (kcal) au-delà duquel l'instantané d'une entrée ne correspond plus à la recette.
const SNAPSHOT_TOLERANCE_KCAL = 1;

type QuantityUnit = "servings" | "grams";

const UNIT_OPTIONS = [
  { value: "servings", label: "portions" },
  { value: "grams", label: "g" },
] as const;

// L'API accepte au plus deux décimales.
function roundCents(value: number): number {
  return Math.round(value * 100) / 100;
}

/*
 * Ajout d'une recette au journal (/journal/recipe/:recipeId).
 */
export function RecipeAddPage() {
  const { recipeId } = useParams<{ recipeId: string }>();
  const { recipe, isLoading, error } = useRecipe(recipeId);

  if (recipe) {
    return <RecipeEntryForm key={recipe.id} recipe={recipe} />;
  }
  return <LoadingOrError isLoading={isLoading} error={error ?? "Recette introuvable."} backTo="/journal/add" />;
}

/*
 * Modification d'une entrée du journal provenant d'une recette
 * (/journal/recipe-entry/:entryId).
 */
export function RecipeEntryEditPage() {
  const { entryId } = useParams<{ entryId: string }>();
  const location = useLocation();
  const stateEntry = (location.state as { entry?: FoodConsumptionRead } | null)?.entry;

  const entryQuery = useQuery({
    queryKey: queryKeys.journal.entry(entryId ?? ""),
    queryFn: () => journalService.getEntry(entryId!),
    enabled: Boolean(entryId),
    // L'entrée transmise par le journal s'affiche sans attendre.
    initialData: stateEntry && stateEntry.id === entryId ? stateEntry : undefined,
  });
  const entry = entryQuery.data;
  const { recipe, isLoading: isRecipeLoading, error: recipeError } = useRecipe(
    entry?.recipe_id ?? undefined,
  );

  if (entry && recipe) {
    return <RecipeEntryForm key={entry.id} recipe={recipe} entry={entry} />;
  }

  const error =
    entryQuery.error?.message ??
    (entry && !entry.recipe_id ? "Cette entrée ne provient pas d’une recette." : null) ??
    recipeError;
  return (
    <LoadingOrError
      isLoading={!error && (entryQuery.isPending || isRecipeLoading)}
      error={error ?? "Entrée introuvable."}
      backTo="/journal"
    />
  );
}

function LoadingOrError({ isLoading, error, backTo }: { isLoading: boolean; error: string; backTo: string }) {
  const navigate = useNavigate();
  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      {isLoading ? (
        <p>Chargement…</p>
      ) : (
        <>
          <p className="text-danger" role="alert">
            {error}
          </p>
          <Button variant="ghost" className="mt-4" onClick={() => navigate(backTo)}>
            {backTo === "/journal" ? "Retour au journal" : "Retour à la recherche"}
          </Button>
        </>
      )}
    </main>
  );
}

// Nutriments enregistrés dans une entrée du journal.
function entryNutrients(entry: FoodConsumptionRead): FoodNutrients {
  return {
    calories_kcal: toNumber(entry.calories_kcal),
    protein_g: toNumber(entry.protein_g),
    carbohydrates_g: toNumber(entry.carbohydrates_g),
    fat_g: toNumber(entry.fat_g),
  };
}

// Quantité initiale d'une entrée : en portions si elle tombe sur un quart de portion, sinon en grammes.
function initialQuantity(entry: FoodConsumptionRead, portionG: number): { unit: QuantityUnit; input: string } {
  const quantityG = toNumber(entry.quantity_g);
  if (portionG > 0) {
    const quarters = Math.round((quantityG / portionG) * 4);
    if (quarters > 0 && roundCents((quarters / 4) * portionG) === quantityG) {
      return { unit: "servings", input: formatQuantityInput(quarters / 4) };
    }
  }
  return { unit: "grams", input: formatQuantityInput(quantityG) };
}

/*
 * Quantité en portions ou en grammes, fiche nutritionnelle et repas.
 * L'API reçoit toujours des grammes et calcule l'instantané nutritionnel.
 * Avec `entry`, la page modifie cette entrée au lieu d'en ajouter une.
 */
function RecipeEntryForm({ recipe, entry }: { recipe: RecipeRead; entry?: FoodConsumptionRead }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const location = useLocation();
  const journalState = readJournalNavState(location.state);
  // En modification, la journée est celle de l'entrée.
  const dayKey = entry ? toDateKey(new Date(entry.consumed_at)) : journalState.date ?? todayKey();

  const portionG = servingWeightG(recipe);
  const [initial] = useState(() =>
    entry ? initialQuantity(entry, portionG) : { unit: "servings" as const, input: "1" },
  );
  const [unit, setUnit] = useState<QuantityUnit>(initial.unit);
  const [quantityInput, setQuantityInput] = useState(initial.input);
  const [mealType, setMealType] = useState<MealType>(
    () => entry?.meal_type ?? journalState.mealType ?? getDefaultMealType(),
  );

  // La quantité saisie, toujours ramenée en grammes.
  const amount = parseDecimal(quantityInput);
  const quantityG = roundCents(unit === "servings" ? amount * portionG : amount);
  // En grammes, la valeur saisie est envoyée telle quelle : deux décimales au plus.
  // En portions, la conversion en grammes est arrondie au centième.
  const isPrecisionValid = unit === "servings" || hasAtMostTwoDecimals(amount);
  const isQuantityValid =
    Number.isFinite(quantityG) && quantityG > 0 && quantityG <= MAX_QUANTITY_G && isPrecisionValid;
  const isQuantityChanged = !entry || quantityG !== toNumber(entry.quantity_g);

  // Quantité inchangée : on montre ce qui est enregistré, même si la recette a changé depuis.
  const nutrients = !isQuantityValid
    ? null
    : isQuantityChanged
      ? recipeNutrientsForQuantity(recipe, quantityG)
      : entryNutrients(entry!);

  // La recette a été modifiée depuis l'ajout : changer la quantité recalculera l'entrée.
  const isSnapshotOutdated =
    entry !== undefined &&
    Math.abs(
      recipeNutrientsForQuantity(recipe, toNumber(entry.quantity_g)).calories_kcal -
        toNumber(entry.calories_kcal),
    ) > SNAPSHOT_TOLERANCE_KCAL;

  // Changer d'unité convertit la valeur saisie pour garder la même quantité.
  function changeUnit(next: QuantityUnit) {
    if (next === unit) return;
    if (Number.isFinite(amount) && amount > 0 && portionG > 0) {
      const converted = next === "grams" ? amount * portionG : amount / portionG;
      setQuantityInput(formatQuantityInput(roundCents(converted)));
    }
    setUnit(next);
  }

  const saveMutation = useMutation({
    mutationFn: () =>
      entry
        ? journalService.updateEntry(entry.id, {
            // Quantité envoyée seulement si elle change : l'instantané est conservé sinon.
            ...(isQuantityChanged ? { quantity_g: quantityG } : {}),
            meal_type: mealType,
          })
        : journalService.addEntry({
            recipe_id: recipe.id,
            quantity_g: quantityG,
            meal_type: mealType,
            consumed_at: consumedAtForDay(dayKey),
          }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.journal.all });
      navigate(journalUrl(dayKey), { replace: true });
    },
  });

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!isQuantityValid || saveMutation.isPending) return;
    saveMutation.mutate();
  }

  const maxInUnit =
    unit === "servings" && portionG > 0
      ? `${formatNutrient(MAX_QUANTITY_G / portionG)} portions`
      : `${formatNutrient(MAX_QUANTITY_G)} g`;

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      <PageHeader onBack={() => navigate(-1)} />

      <h1 className="break-words">{recipe.name}</h1>
      <p className="mt-1">
        Recette · {formatCount(recipe.servings, "portion", "portions")} de{" "}
        {formatNutrient(portionG, 0)} g
      </p>

      <NutritionFactsCard nutrients={nutrients} className="mt-6" />
      <RecipeIngredientsDetails
        recipe={recipe}
        quantityG={isQuantityValid ? quantityG : null}
        className="mt-3"
      />
      {dayKey !== todayKey() && (
        <p className="mt-1">
          {entry ? "Entrée du journal de" : "Ajout au journal de"} :{" "}
          {formatDayLabel(dayKey).toLowerCase()}
        </p>
      )}
      {isSnapshotOutdated && (
        <p className="mt-2 text-sm text-muted" role="note">
          La recette a été modifiée depuis cet ajout. Changer la quantité recalculera les valeurs
          avec la recette actuelle.
        </p>
      )}

      <form onSubmit={handleSubmit} className="mt-6 space-y-4 text-left">
        <QuantityField
          value={quantityInput}
          onChange={setQuantityInput}
          unit={unit}
          units={UNIT_OPTIONS}
          onUnitChange={changeUnit}
          error={
            !isQuantityValid && quantityInput.trim() !== ""
              ? isPrecisionValid
                ? `Entrez une quantité supérieure à 0 et d’au plus ${maxInUnit}.`
                : "Entrez une quantité avec deux décimales au plus."
              : null
          }
        />

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

        {saveMutation.error && (
          <p className="text-danger" role="alert">
            {saveMutation.error.message}
          </p>
        )}

        <Button
          type="submit"
          className="mt-2 w-full font-bold"
          disabled={!isQuantityValid || saveMutation.isPending}
        >
          {entry
            ? saveMutation.isPending ? "Modification…" : "Modifier l’entrée"
            : saveMutation.isPending ? "Ajout…" : "Ajouter au journal"}
        </Button>
      </form>
    </main>
  );
}
