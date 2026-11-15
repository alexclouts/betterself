import type { FoodConsumptionRead } from "../api/generated/foodConsumptionRead";
import type { FoodRead } from "../api/generated/foodRead";
import { MealType } from "../api/generated/mealType";

// Ordre d'affichage des repas dans la journée.
export const MEAL_TYPE_ORDER: MealType[] = [
  MealType.breakfast,
  MealType.lunch,
  MealType.dinner,
  MealType.snack,
];

// Libellés des types de repas (usage québécois).
export const MEAL_TYPE_LABELS: Record<MealType, string> = {
  breakfast: "Déjeuner",
  lunch: "Dîner",
  dinner: "Souper",
  snack: "Collation",
};

// Vérifie qu'une valeur reçue (URL, état de navigation) est un type de repas.
export function isMealType(value: unknown): value is MealType {
  return typeof value === "string" && (MEAL_TYPE_ORDER as string[]).includes(value);
}

export interface FoodNutrients {
  calories_kcal: number;
  protein_g: number;
  carbohydrates_g: number;
  fat_g: number;
}

// Les valeurs décimales arrivent de l'API sous forme de chaînes ("250.00").
export function toNumber(value: string | number): number {
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

// Additionne les valeurs nutritionnelles d'une liste de consommations.
export function sumNutrients(entries: FoodConsumptionRead[]): FoodNutrients {
  return entries.reduce<FoodNutrients>(
    (total, entry) => ({
      calories_kcal: total.calories_kcal + toNumber(entry.calories_kcal),
      protein_g: total.protein_g + toNumber(entry.protein_g),
      carbohydrates_g: total.carbohydrates_g + toNumber(entry.carbohydrates_g),
      fat_g: total.fat_g + toNumber(entry.fat_g),
    }),
    { calories_kcal: 0, protein_g: 0, carbohydrates_g: 0, fat_g: 0 },
  );
}
