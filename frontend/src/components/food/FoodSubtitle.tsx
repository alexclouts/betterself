import { formatNutrient } from "../../lib/food";
import type { FoodRead } from "../../api/generated/foodRead";

type FoodSubtitleProps = Pick<FoodRead, "brand" | "serving_g" | "reference_weight_g">;

/*
 * Sous le nom d'un aliment : la marque, puis la portion, avec la quantité en évidence.
 */
export function FoodSubtitle({ brand, serving_g, reference_weight_g }: FoodSubtitleProps) {
  return (
    <div className="-mt-2 space-y-0.5 lg:-mt-4">
      {brand && <p className="font-semibold text-foreground">{brand}</p>}
      <p className="text-sm">
        {serving_g ? "Portion suggérée" : "Portion de référence"} :{" "}
        <strong className="font-semibold text-foreground">
          {formatNutrient(serving_g ?? reference_weight_g)} g
        </strong>
      </p>
    </div>
  );
}
