import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import type { FoodConsumptionRead } from "../../api/generated/foodConsumptionRead";
import type { FoodRead } from "../../api/generated/foodRead";
import { MealType } from "../../api/generated/mealType";
import Button from "../../components/ui/Button";
import Select from "../../components/ui/Select";
import {
  computeNutrientsForQuantity,
  formatNutrient,
  getDefaultMealType,
  getDefaultQuantityG,
  hasInconsistentCalories,
  MEAL_TYPE_LABELS,
  toNumber,
} from "../../lib/food"
// Services et utilitaires pour la gestion des aliments et du journal.
import { foodService } from "../../services/foodService";
import { journalService } from "../../services/journalService";
import { queryKeys } from "../../lib/queryClient";
import { consumedAtForDay, toDateKey, todayKey } from "../../lib/date";
import { journalUrl, readJournalNavState } from "../../lib/journal";
import { NutritionFactsCard } from "../../components/food/NutritionFactsCard";
import { PageHeader } from "../../components/navigation/PageHeader";
import { QuantityField } from "../../components/ui/QuantityField";
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
import { formatQuantityInput, parseDecimal } from "../../lib/recipe";
import { FoodSubtitle } from "../../components/food/FoodSubtitle";
import { JournalDayBadge } from "../../components/journal/JournalDayBadge";

const MAX_QUANTITY_G = 5000;

type QuantityState = { unit: QuantityUnit; input: string };

/*
 * Quantité proposée à l'ajout : la portion du fabricant, dans l'unité de l'aliment
 * si elle y tombe (« 2 tranches »). Sans portion, une unité de l'aliment.
 */
function defaultQuantity(food: FoodRead): QuantityState {
  const unit = getFoodUnit(food);
  if (unit && food.serving_g === null) return { unit: "unit", input: "1" };
  return quantityState(getDefaultQuantityG(food), food);
}

// Quantité en grammes affichée dans l'unité de l'aliment si possible.
function quantityState(quantityG: number, food: FoodRead): QuantityState {
  const { unit, amount } = initialQuantity(quantityG, getFoodUnit(food)?.grams ?? null);
  return { unit, input: formatQuantityInput(amount) };
}

export function FoodAddPage() {
  /*
   * Variables d'état et constantes pour la gestion de l'ajout ou 
   * de la modification d'une consommation alimentaire.
   */

  const navigate = useNavigate();
  // Accès au cache TanStack Query, pour signaler que le journal a changé.
  const queryClient = useQueryClient();
  // /journal/food/:id → ajout ; 
  // /journal/entry/:entryId → modification d'une entrée.
  const { id, entryId } = useParams<{ id: string; entryId: string }>();

  // Détermine si l'on est en mode modification.
  const isEditing = Boolean(entryId);

  // Lecture de l'état de navigation et récupération des données transmises.
  const location = useLocation();
  const state = location.state as { food?: FoodRead; entry?: FoodConsumptionRead } | null;

  const foodFromState = state?.food;
  const initialFood = !isEditing && foodFromState && foodFromState.id === id ? foodFromState : null;
  const entryFromState = state?.entry && state.entry.id === entryId ? state.entry : null;
  const journalState = readJournalNavState(location.state);


  // Déclaration des variables d'état pour l'aliment, l'entrée, la quantité et le type de repas.
  const [food, setFood] = useState<FoodRead | null>(initialFood);
  const [entry, setEntry] = useState<FoodConsumptionRead | null>(null);
  const [initialQuantityState] = useState<QuantityState>(() =>
    initialFood ? defaultQuantity(initialFood) : { unit: "grams", input: "" },
  );
  const [quantityInput, setQuantityInput] = useState(initialQuantityState.input);
  const [unit, setUnit] = useState<QuantityUnit>(initialQuantityState.unit);
  const [mealType, setMealType] = useState<MealType>(
    () => journalState.mealType ?? getDefaultMealType(),
  );

  // État pour le chargement et la soumission du formulaire, ainsi que pour les erreurs.
  const [isLoading, setIsLoading] = useState(!initialFood);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // En modification, la journée est celle de l'entrée.
  const dayKey = entry ? toDateKey(new Date(entry.consumed_at)): journalState.date ?? todayKey();

  /*
   * Effet déclenché lors de l'accès à la page pour 
   * charger l'aliment et l'entrée correspondants.
   */

  useEffect(() => {
    if (food) 
      return;

    let cancelled = false;
    setIsLoading(true);

    async function load() {
      if (entryId) {
        // Modification : charge l'entrée, puis l'aliment correspondant.
        const loadedEntry = entryFromState ?? (await journalService.getEntry(entryId));
        // Une entrée de recette a sa propre page.
        if (!loadedEntry.food_id) {
          if (!cancelled) {
            navigate(`/journal/recipe-entry/${loadedEntry.id}`, { replace: true, state: { entry: loadedEntry } });
          }
          return;
        }
        const loadedFood = await foodService.getFood(loadedEntry.food_id);

        if (cancelled) 
          return;

        // Mise à jour de l'état avec l'entrée et l'aliment chargés.
        const quantity = quantityState(toNumber(loadedEntry.quantity_g), loadedFood);
        setEntry(loadedEntry);
        setFood(loadedFood);
        setQuantityInput(quantity.input);
        setUnit(quantity.unit);
        setMealType(loadedEntry.meal_type);

      } else if (id) {
        // Ajout : chargement de l'aliment depuis le service.
        const loadedFood = await foodService.getFood(id);
        if (cancelled) 
          return;
        
        const quantity = defaultQuantity(loadedFood);
        setFood(loadedFood);
        setQuantityInput(quantity.input);
        setUnit(quantity.unit);
      }
    }
    // On veut charger l'aliment et l'entrée lorsque l'utilisateur accède à cette page
    load()
      .catch((err) => {
        if (cancelled) 
          return;

        setError(err instanceof Error ? err.message : "Impossible de charger cet aliment.");
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [id, entryId, food, navigate]);

  // Validation de la quantité saisie, toujours ramenée en grammes.
  const foodUnit = food ? getFoodUnit(food) : null;
  const unitG = foodUnit?.grams ?? 0;
  const amount = parseDecimal(quantityInput);
  const quantityG = toGrams(amount, unit, unitG);
  const isPrecisionValid = hasValidPrecision(amount, unit);
  const isQuantityValid =
    Number.isFinite(quantityG) && quantityG > 0 && quantityG <= MAX_QUANTITY_G && isPrecisionValid;

  // Changer d'unité convertit la valeur saisie pour garder la même quantité.
  function changeUnit(next: QuantityUnit) {
    if (next === unit) return;
    if (Number.isFinite(amount) && amount > 0) {
      setQuantityInput(formatQuantityInput(convertAmount(amount, unit, next, unitG)));
    }
    setUnit(next);
  }

  const maxInUnit =
    unit === "unit" && foodUnit
      ? `${formatNutrient(MAX_QUANTITY_G / unitG)} ${foodUnit.plural}`
      : `${formatNutrient(MAX_QUANTITY_G)} g`;

  // Calcule les nutriments pour la quantité saisie.
  const nutrients = food && isQuantityValid ? computeNutrientsForQuantity(food, quantityG) : null;

  // Gestion de la soumission du formulaire.
  async function handleSubmit(event: React.SubmitEvent) {
    event.preventDefault();

    if (!food || !isQuantityValid) 
      return;

    setIsSubmitting(true);
    setError(null);

    try {
      if (entry) {
        // Modification de l'entrée : l'API recalcule les nutriments.
        await journalService.updateEntry(entry.id, {
          quantity_g: quantityG,
          meal_type: mealType,
        });
      } else {
        // Ajout de l'aliment au journal avec la quantité et le type de repas spécifiés.
        await foodService.addFoodToJournal({
          food_id: food.id,
          quantity_g: quantityG,
          meal_type: mealType,
          consumed_at: consumedAtForDay(dayKey),
        });
      }
      // Le journal a changé : l'accueil et le journal rechargeront leurs données.
      await queryClient.invalidateQueries({ queryKey: queryKeys.journal.all });
      // L'historique proposé par la recherche aussi.
      await queryClient.invalidateQueries({ queryKey: queryKeys.foods.all });
      navigate(journalUrl(dayKey), { replace: true });
    } catch (err) {
      const fallback = entry ? "Impossible de modifier cette entrée.": "Impossible d’ajouter cet aliment au journal.";
      setError(err instanceof Error ? err.message : fallback);
    } finally {
      setIsSubmitting(false);
    }
  }
  // Affichage du chargement si nécessaire.
  if (isLoading) {
    return (
      <main className="mx-auto w-full max-w-md px-4 py-6">
        <p>Chargement…</p>
      </main>
    );
  }

  // Affichage de l'erreur si l'aliment n'a pas pu être chargé.
  if (!food) {
    return (
      <main className="mx-auto w-full max-w-md px-4 py-6">
        <p className="text-danger">{error ?? "Aliment introuvable."}</p>
        <Button
          variant="ghost"
          className="mt-4"
          onClick={() => navigate(isEditing ? "/journal" : "/journal/add")}
        >
          {isEditing ? "Retour au journal" : "Retour à la recherche"}
        </Button>
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      <PageHeader onBack={() => navigate(-1)} />

      <h1>{food.name}</h1>
      <FoodSubtitle
        brand={food.brand}
        serving_g={food.serving_g}
        reference_weight_g={food.reference_weight_g}
        unit_name={food.unit_name}
        unit_name_plural={food.unit_name_plural}
        unit_g={food.unit_g}
      />
      {dayKey !== todayKey() && <JournalDayBadge dayKey={dayKey} isEntry={entry !== null} className="mt-3" />}
      <NutritionFactsCard
        nutrients={nutrients}
        showCalorieWarning={hasInconsistentCalories(food)}
        showWeightWarning={food.weight_is_estimated}
        className="mt-6"
      />

      <form onSubmit={handleSubmit} className="mt-6 space-y-4 text-left">
        <QuantityField
          value={quantityInput}
          onChange={setQuantityInput}
          unit={unit}
          units={foodUnitOptions(foodUnit, amount)}
          onUnitChange={changeUnit}
          error={
            !isQuantityValid && quantityInput.trim() !== ""
              ? isPrecisionValid
                ? `Entrez une quantité supérieure à 0 et d’au plus ${maxInUnit}.`
                : "Entrez une quantité avec deux décimales au plus."
              : null
          }
          hint={
            unit === "unit" && foodUnit && isQuantityValid
              ? unitWeightHint(foodUnit, amount, food.weight_is_estimated)
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

        {error && <p className="text-danger">{error}</p>}

        <Button
          type="submit"
          className="w-full mt-2 font-bold"
          disabled={!isQuantityValid || isSubmitting}
        >
          {entry
            ? isSubmitting ? "Modification…" : "Modifier l’entrée"
            : isSubmitting ? "Ajout…" : "Ajouter au journal"}
        </Button>
      </form>
    </main>
  );
}
