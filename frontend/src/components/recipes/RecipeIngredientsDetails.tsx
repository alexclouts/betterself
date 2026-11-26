import type { RecipeRead } from "../../api/generated/recipeRead";
import { formatNutrient, toNumber } from "../../lib/food";

type RecipeIngredientsDetailsProps = {
  recipe: RecipeRead;
  // Quantité de la recette consommée; null si la saisie est invalide.
  quantityG: number | null;
  className?: string;
};

/*
 * Volet repliable « Voir les ingrédients », du même style que « Voir les données »
 * des graphiques : la part de chaque ingrédient dans la quantité saisie.
 */
export function RecipeIngredientsDetails({ recipe, quantityG, className = "" }: RecipeIngredientsDetailsProps) {
  const ingredients = recipe.ingredients ?? [];
  const totalWeight = toNumber(recipe.total_weight_g);
  const ratio = quantityG !== null && totalWeight > 0 ? quantityG / totalWeight : null;

  if (ingredients.length === 0) return null;

  return (
    <details className={`text-left text-sm ${className}`}>
      <summary className="cursor-pointer font-bold text-foreground">Voir les ingrédients</summary>
      <table className="mt-2 w-full">
        <caption className="sr-only">Ingrédients pour la quantité saisie</caption>
        <thead>
          <tr className="text-muted">
            <th className="py-1 text-left font-normal">Ingrédient</th>
            <th className="py-1 text-right font-normal">Quantité</th>
            <th className="py-1 pl-4 text-right font-normal">Calories</th>
          </tr>
        </thead>
        <tbody>
          {ingredients.map((ingredient) => (
            <tr key={ingredient.id} className="border-t border-border/50">
              <td className="py-1 pr-2 break-words">{ingredient.food.name}</td>
              <td className="py-1 text-right whitespace-nowrap tabular-nums">
                {ratio === null ? "–" : formatNutrient(toNumber(ingredient.quantity_g) * ratio)} g
              </td>
              <td className="py-1 pl-4 text-right font-bold whitespace-nowrap text-foreground tabular-nums">
                {ratio === null
                  ? "–"
                  : formatNutrient(toNumber(ingredient.nutrition.calories_kcal) * ratio, 0)}{" "}
                kcal
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </details>
  );
}
