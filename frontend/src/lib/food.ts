import type { FoodConsumptionRead } from "../api/generated/foodConsumptionRead";
import type { FoodRead } from "../api/generated/foodRead";
import { MealType } from "../api/generated/mealType";

/**
 * Contient toutes les fonctions utilitaires pour la gestion des aliments et de leurs valeurs nutritionnelles.
 * 
 * Fournit des fonctions pour convertir, formater et calculer les valeurs nutritionnelles des aliments.
 * Inclut également des fonctions pour additionner les valeurs nutritionnelles de plusieurs consommations.
 */


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
// Les quantités sont enregistrées au centième de gramme (NUMERIC(10, 2)) :
// l'API refuse une valeur plus précise.
export function hasAtMostTwoDecimals(value: number): boolean {
  return Number.isFinite(value) && Math.round(value * 100) / 100 === value;
}

// Propose un repas selon l'heure actuelle.
export function getDefaultMealType(date = new Date()): MealType {
  const hour = date.getHours();

  if (hour < 10) return MealType.breakfast;
  if (hour < 14) return MealType.lunch;
  if (hour >= 17 && hour < 21) return MealType.dinner;

  return MealType.snack;
}

export function isMealType(value: unknown): value is MealType {
  return typeof value === "string" && (MEAL_TYPE_ORDER as string[]).includes(value);
}

export interface FoodNutrients {
  calories_kcal: number;
  protein_g: number;
  carbohydrates_g: number;
  fat_g: number;
}

// Valeurs nutritives d'un aliment, ou d'un produit du catalogue, pour sa portion de référence.
export type NutritionReference = Pick<
  FoodRead,
  "reference_weight_g" | "calories_kcal" | "protein_g" | "carbohydrates_g" | "fat_g"
>;

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

/*
 * Signale des calories très éloignées de celles des macros (4P + 4G + 9L).
 * L'écart peut être normal (fibres, polyols, alcool) : on avertit sans bloquer.
 */
export function hasInconsistentCalories(food: NutritionReference): boolean {
  // Ramené à 100 g pour que la tolérance ne dépende pas de la portion de référence.
  const per100g = computeNutrientsForQuantity(food, 100);
  const expected = per100g.protein_g * 4 + per100g.carbohydrates_g * 4 + per100g.fat_g * 9;
  return Math.abs(per100g.calories_kcal - expected) > Math.max(20, per100g.calories_kcal * 0.2);
}

/*
 * Calcule les valeurs nutritionnelles pour une quantité donnée,
 * à partir des valeurs déclarées pour la portion de référence.
 */
export function computeNutrientsForQuantity(
  food: NutritionReference,
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
