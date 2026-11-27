import type { FoodSearchResult } from "../../api/generated/foodSearchResult";
import {
  computeNutrientsForQuantity,
  formatNutrient,
  getDefaultQuantityG,
  hasInconsistentCalories,
} from "../../lib/food";
import { MacroInline } from "../food/MacroBreakdown";

// Petite horloge discrète : l'aliment fait partie de l'historique de l'utilisateur.
function HistoryIcon() {
  return (
    <span title="Dans votre historique" className="ml-1.5 inline-block align-[-2px] text-muted">
      <svg
        viewBox="0 0 16 16"
        className="h-3.5 w-3.5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <circle cx="8" cy="8" r="6.25" />
        <path d="M8 4.5V8l2.25 1.5" />
      </svg>
      <span className="sr-only">Dans votre historique</span>
    </span>
  );
}

type FoodResultItemProps = {
  food: FoodSearchResult;
  onSelect: () => void;
  disabled?: boolean;
  isPending?: boolean;
};

// Résultat de recherche : nom, marque, calories et macros pour la quantité par défaut.
export function FoodResultItem({
  food,
  onSelect,
  disabled = false,
  isPending = false,
}: FoodResultItemProps) {
  const quantityG = getDefaultQuantityG(food);
  const nutrients = computeNutrientsForQuantity(food, quantityG);

  return (
    <li>
      <button
        type="button"
        onClick={onSelect}
        disabled={disabled}
        aria-busy={isPending}
        className="flex w-full items-start justify-between gap-4 px-4 py-3 text-left transition hover:bg-surface-raised focus-visible:bg-surface-raised disabled:opacity-60"
      >
        <span className="min-w-0 flex-1">
          <span className="line-clamp-2 font-medium text-foreground">
            {food.name}
            {food.in_history && <HistoryIcon />}
          </span>
          {food.brand && <span className="block truncate text-sm text-muted">{food.brand}</span>}
          <MacroInline nutrients={nutrients} className="mt-1" />
          {hasInconsistentCalories(food) && (
            <span className="block text-sm text-warning">Calories à vérifier sur l’emballage</span>
          )}
        </span>

        <span className="shrink-0 text-right">
          <span className="block font-semibold text-foreground">
            {isPending ? "Ajout…" : `${formatNutrient(nutrients.calories_kcal, 0)} kcal`}
          </span>
          <span className="block text-sm text-muted">
            {food.serving_g ? "portion de " : ""}
            {formatNutrient(quantityG)} g
          </span>
        </span>
      </button>
    </li>
  );
}
