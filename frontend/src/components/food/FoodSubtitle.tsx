import { formatNutrient, toNumber } from "../../lib/food";
import { getFoodUnit, gramsToUnitCount, unitLabel, type FoodUnitFields } from "../../lib/units";
import type { FoodRead } from "../../api/generated/foodRead";

type FoodSubtitleProps = Pick<FoodRead, "brand" | "serving_g" | "reference_weight_g"> & FoodUnitFields;

/*
 * Sous le nom d'un aliment : la marque, puis la portion, avec la quantité en évidence.
 * Une portion qui tombe sur l'unité de l'aliment est exprimée dans cette unité :
 * « 2 tranches (50 g) ».
 */
export function FoodSubtitle({ brand, serving_g, reference_weight_g, ...unitFields }: FoodSubtitleProps) {
  const quantityG = toNumber(serving_g ?? reference_weight_g);
  const unit = getFoodUnit(unitFields);
  const count = serving_g && unit ? gramsToUnitCount(quantityG, unit.grams) : null;

  return (
    <div className="-mt-2 space-y-0.5 lg:-mt-4">
      {brand && <p className="font-semibold text-foreground">{brand}</p>}
      <p className="text-sm">
        {serving_g ? "Portion suggérée" : "Portion de référence"} :{" "}
        <strong className="font-semibold text-foreground">
          {unit && count !== null
            ? `${formatNutrient(count, 2)} ${unitLabel(unit, count)} (${formatNutrient(quantityG)} g)`
            : `${formatNutrient(quantityG)} g`}
        </strong>
      </p>
    </div>
  );
}
