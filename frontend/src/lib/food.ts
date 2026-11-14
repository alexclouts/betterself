import type { FoodRead } from "../api/generated/foodRead";

export interface FoodNutrients {
  calories_kcal: number;
  protein_g: number;
  carbohydrates_g: number;
  fat_g: number;
}

// Les valeurs décimales arrivent de l'API sous forme de chaînes ("250.00").
function toNumber(value: string | number): number {
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

// Formate une valeur nutritionnelle sans zéros superflus (ex. "250.00" → "250").
export function formatNutrient(value: string | number, maxDecimals = 1): string {
  return toNumber(value).toLocaleString("fr-CA", {
    maximumFractionDigits: maxDecimals,
  });
}

// Quantité par défaut proposée lors de l'ajout : la portion de référence de l'aliment.
export function getDefaultQuantityG(food: FoodRead): number {
  return toNumber(food.reference_weight_g);
}

/*
 * Calcule les valeurs nutritionnelles pour une quantité donnée,
 * à partir des valeurs déclarées pour la portion de référence.
 */
export function computeNutrientsForQuantity(
  food: FoodRead,
  quantityG: number,
): FoodNutrients {
  const referenceWeight = toNumber(food.reference_weight_g);
  const ratio = referenceWeight > 0 ? quantityG / referenceWeight : 0;

  return {
    calories_kcal: toNumber(food.calories_kcal) * ratio,
    protein_g: toNumber(food.protein_g) * ratio,
    carbohydrates_g: toNumber(food.carbohydrates_g) * ratio,
    fat_g: toNumber(food.fat_g) * ratio,
  };
}
