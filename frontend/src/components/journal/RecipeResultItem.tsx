import type { RecipeRead } from "../../api/generated/recipeRead";
import { formatNutrient } from "../../lib/food";
import { formatCount, perServing, recipeTotals, servingWeightG } from "../../lib/recipe";

type RecipeResultItemProps = {
  recipe: RecipeRead;
  onSelect: () => void;
};

// Recette proposée dans la recherche : nom, macros et calories pour une portion.
export function RecipeResultItem({ recipe, onSelect }: RecipeResultItemProps) {
  const nutrients = perServing(recipeTotals(recipe), recipe.servings);

  return (
    <li>
      <button
        type="button"
        onClick={onSelect}
        className="flex w-full items-start justify-between gap-4 px-4 py-3 text-left transition hover:bg-surface-raised focus-visible:bg-surface-raised"
      >
        <span className="min-w-0 flex-1">
          <span className="line-clamp-2 font-medium text-foreground">{recipe.name}</span>
          <span className="block text-sm text-muted">
            {formatCount(recipe.servings, "portion", "portions")}
          </span>
          <span className="mt-1 block text-sm text-muted">
            P {formatNutrient(nutrients.protein_g)} g · G {formatNutrient(nutrients.carbohydrates_g)} g
            {" "}· L {formatNutrient(nutrients.fat_g)} g
          </span>
        </span>

        <span className="shrink-0 text-right">
          <span className="block font-semibold text-foreground">
            {formatNutrient(nutrients.calories_kcal, 0)} kcal
          </span>
          <span className="block text-sm text-muted">
            portion de {formatNutrient(servingWeightG(recipe), 0)} g
          </span>
        </span>
      </button>
    </li>
  );
}
