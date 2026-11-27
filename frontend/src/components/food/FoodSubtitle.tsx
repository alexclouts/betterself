import { formatNutrient } from "../../lib/food";
import { formatSuggestedQuantity, suggestedQuantity, type SuggestionFields } from "../../lib/units";
import type { FoodRead } from "../../api/generated/foodRead";

type FoodSubtitleProps = Pick<FoodRead, "brand"> & SuggestionFields;

/*
 * Sous le nom d'un aliment : la marque, puis la portion proposée, dans l'unité qui
 * lui correspond le mieux (« 2 tranches (90 g) »), avec la quantité en évidence.
 */
export function FoodSubtitle({ brand, ...food }: FoodSubtitleProps) {
  const suggestion = suggestedQuantity(food);
  const isReference = suggestion.unit === null && food.serving_g === null;

  return (
    <div className="-mt-2 space-y-0.5 lg:-mt-4">
      {brand && <p className="font-semibold text-foreground">{brand}</p>}
      <p className="text-sm">
        {isReference ? "Portion de référence" : "Portion suggérée"} :{" "}
        <strong className="font-semibold text-foreground">
          {formatSuggestedQuantity(suggestion)}
          {suggestion.unit && ` (${formatNutrient(suggestion.grams)} g)`}
        </strong>
      </p>
    </div>
  );
}
