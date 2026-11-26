import Card from "../ui/Card";
import { formatNutrient, type FoodNutrients } from "../../lib/food";

type NutritionFactsCardProps = {
  // Valeurs pour la quantité saisie; null affiche des tirets (quantité invalide).
  nutrients: FoodNutrients | null;
  className?: string;
};

// Calories en grand, puis protéines, glucides et lipides sur une rangée.
export function NutritionFactsCard({ nutrients, className = "" }: NutritionFactsCardProps) {
  return (
    <Card className={`w-full p-6 bg-surface ${className}`}>
      <dl className="grid grid-cols-3 gap-3">
        <div className="col-span-3">
          <dt>Calories</dt>
          <dd className="text-2xl font-semibold mb-4">
            {nutrients ? formatNutrient(nutrients.calories_kcal, 0) : "–"} kcal
          </dd>
        </div>
        <div>
          <dt>Protéines</dt>
          <dd>{nutrients ? formatNutrient(nutrients.protein_g) : "–"} g</dd>
        </div>
        <div>
          <dt>Glucides</dt>
          <dd>{nutrients ? formatNutrient(nutrients.carbohydrates_g) : "–"} g</dd>
        </div>
        <div>
          <dt>Lipides</dt>
          <dd>{nutrients ? formatNutrient(nutrients.fat_g) : "–"} g</dd>
        </div>
      </dl>
    </Card>
  );
}
