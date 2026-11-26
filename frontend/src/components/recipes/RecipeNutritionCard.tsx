import Card from "../ui/Card";
import { formatNutrient, type FoodNutrients } from "../../lib/food";
import { formatCount, perServing } from "../../lib/recipe";

// « 420 kcal · P 30 g · G 45 g · L 12 g »
function NutrientsLine({ nutrients }: { nutrients: FoodNutrients }) {
  return (
    <>
      <strong className="text-foreground">{formatNutrient(nutrients.calories_kcal, 0)} kcal</strong>
      {" "}· P {formatNutrient(nutrients.protein_g)} g · G {formatNutrient(nutrients.carbohydrates_g)} g
      {" "}· L {formatNutrient(nutrients.fat_g)} g
    </>
  );
}

type RecipeNutritionCardProps = {
  totals: FoodNutrients;
  servings: number;
  // Somme des quantités des ingrédients.
  totalWeightG: number;
};

// Valeurs nutritionnelles d'une portion et de la recette entière, avec le poids total calculé.
export function RecipeNutritionCard({ totals, servings, totalWeightG }: RecipeNutritionCardProps) {
  const validServings = Number.isInteger(servings) && servings > 0 ? servings : 1;

  return (
    <Card className="w-full bg-surface text-left">
      <p className="text-sm text-muted">
        Par portion ({formatCount(validServings, "portion", "portions")},{" "}
        {formatNutrient(totalWeightG / validServings, 0)} g chacune)
      </p>
      <p className="mt-1">
        <NutrientsLine nutrients={perServing(totals, validServings)} />
      </p>
      <p className="mt-3 text-sm text-muted">
        Recette entière ({formatNutrient(totalWeightG)} g)
      </p>
      <p className="mt-1 text-sm">
        <NutrientsLine nutrients={totals} />
      </p>
    </Card>
  );
}
