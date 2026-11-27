import Card from "../ui/Card";
import { formatNutrient, type FoodNutrients } from "../../lib/food";
import { CalorieWarning } from "./CalorieWarning";
import { MacroBreakdown } from "./MacroBreakdown";
import { WeightEstimateWarning } from "./WeightEstimateWarning";

type NutritionFactsCardProps = {
  // Valeurs pour la quantité saisie; null affiche des tirets (quantité invalide).
  nutrients: FoodNutrients | null;
  // Affiche, en bas de la carte, l'avertissement « Calories à vérifier ».
  showCalorieWarning?: boolean;
  // Affiche l'avertissement « Poids estimé » (portion sans poids sur l'étiquette).
  showWeightWarning?: boolean;
  className?: string;
};

// Calories en grand, puis la répartition des protéines, glucides et lipides, chacun dans sa couleur.
export function NutritionFactsCard({
  nutrients,
  showCalorieWarning = false,
  showWeightWarning = false,
  className = "",
}: NutritionFactsCardProps) {
  return (
    <Card className={`w-full p-6 bg-surface ${className}`}>
      <dl>
        <dt>Calories</dt>
        <dd className="text-2xl font-semibold">
          {nutrients ? formatNutrient(nutrients.calories_kcal, 0) : "–"} kcal
        </dd>
      </dl>
      <MacroBreakdown nutrients={nutrients} className="mt-4" />
      {showWeightWarning && <WeightEstimateWarning className="mt-5" />}
      {showCalorieWarning && <CalorieWarning className={showWeightWarning ? "mt-2" : "mt-5"} />}
    </Card>
  );
}
