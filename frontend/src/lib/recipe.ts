import type { RecipeRead } from "../api/generated/recipeRead";
import type { FoodRead } from "../api/generated/foodRead";
import { hasAtMostTwoDecimals, toNumber, type FoodNutrients, type NutritionReference } from "./food";

// Aliment choisi comme ingrédient, avec ce qu'il faut pour calculer sa nutrition.
export type PickedFood = NutritionReference &
  Pick<FoodRead, "id" | "name" | "brand" | "serving_g">;

// Bornes acceptées par l'API.
export const MAX_WEIGHT_G = 100000;
export const MAX_SERVINGS = 1000;

// Accepte la virgule comme séparateur décimal; NaN si vide ou invalide.
export function parseDecimal(value: string): number {
  if (value.trim() === "") return NaN;
  return Number(value.replace(",", "."));
}

// Valide une quantité en grammes; retourne un message d'erreur ou null.
export function validateWeight(value: string): string | null {
  const parsed = parseDecimal(value);
  if (!Number.isFinite(parsed)) return "Valeur invalide.";
  if (parsed <= 0) return "Doit être supérieur à 0.";
  if (parsed > MAX_WEIGHT_G) return `Maximum ${MAX_WEIGHT_G.toLocaleString("fr-CA")} g.`;
  if (!hasAtMostTwoDecimals(parsed)) return "Deux décimales au plus.";
  return null;
}

// Valide un nombre de portions (entier); retourne un message d'erreur ou null.
export function validateServings(value: string): string | null {
  const parsed = parseDecimal(value);
  if (!Number.isInteger(parsed)) return "Nombre entier requis.";
  if (parsed <= 0) return "Doit être supérieur à 0.";
  if (parsed > MAX_SERVINGS) return `Maximum ${MAX_SERVINGS}.`;
  return null;
}

// Quantité affichée dans un champ : « 350,5 », sans séparateur de milliers.
export function formatQuantityInput(value: string | number): string {
  return toNumber(value).toLocaleString("fr-CA", {
    maximumFractionDigits: 2,
    useGrouping: false,
  });
}

// Champs saisis pour les détails d'une recette.
export type RecipeDetailsValues = {
  name: string;
  description: string;
  servings: string;
};

// Les détails sont valides : nom présent et nombre de portions entier.
export function areDetailsValid(values: RecipeDetailsValues): boolean {
  return values.name.trim() !== "" && validateServings(values.servings) === null;
}

// « 1 portion », « 4 portions »
export function formatCount(count: number, singular: string, plural: string): string {
  return `${count.toLocaleString("fr-CA")} ${count > 1 ? plural : singular}`;
}

// Additionne des valeurs nutritionnelles.
export function sumNutrients(items: FoodNutrients[]): FoodNutrients {
  return items.reduce<FoodNutrients>(
    (total, item) => ({
      calories_kcal: total.calories_kcal + item.calories_kcal,
      protein_g: total.protein_g + item.protein_g,
      carbohydrates_g: total.carbohydrates_g + item.carbohydrates_g,
      fat_g: total.fat_g + item.fat_g,
    }),
    { calories_kcal: 0, protein_g: 0, carbohydrates_g: 0, fat_g: 0 },
  );
}

// Divise des valeurs nutritionnelles par un nombre de portions (1 si invalide).
export function perServing(totals: FoodNutrients, servings: number): FoodNutrients {
  const divisor = Number.isFinite(servings) && servings > 0 ? servings : 1;
  return {
    calories_kcal: totals.calories_kcal / divisor,
    protein_g: totals.protein_g / divisor,
    carbohydrates_g: totals.carbohydrates_g / divisor,
    fat_g: totals.fat_g / divisor,
  };
}

// Valeurs nutritionnelles totales d'une recette enregistrée.
export function recipeTotals(recipe: RecipeRead): FoodNutrients {
  return {
    calories_kcal: toNumber(recipe.nutrition.calories_kcal),
    protein_g: toNumber(recipe.nutrition.protein_g),
    carbohydrates_g: toNumber(recipe.nutrition.carbohydrates_g),
    fat_g: toNumber(recipe.nutrition.fat_g),
  };
}

// Poids d'une portion d'une recette enregistrée.
export function servingWeightG(recipe: RecipeRead): number {
  return recipe.servings > 0 ? toNumber(recipe.total_weight_g) / recipe.servings : 0;
}

// Valeurs nutritionnelles d'une quantité (g) d'une recette, au prorata de son poids total.
export function recipeNutrientsForQuantity(recipe: RecipeRead, quantityG: number): FoodNutrients {
  const totalWeight = toNumber(recipe.total_weight_g);
  const ratio = totalWeight > 0 ? quantityG / totalWeight : 0;
  const totals = recipeTotals(recipe);
  return {
    calories_kcal: totals.calories_kcal * ratio,
    protein_g: totals.protein_g * ratio,
    carbohydrates_g: totals.carbohydrates_g * ratio,
    fat_g: totals.fat_g * ratio,
  };
}

// Compare des noms sans tenir compte des majuscules ni des accents.
export function normalizeSearchText(value: string): string {
  return value.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
}
