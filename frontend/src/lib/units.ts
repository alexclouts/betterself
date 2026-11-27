import type { FoodRead } from "../api/generated/foodRead";
import { formatNutrient, toNumber } from "./food";

// Unités de saisie des quantités (components/ui/QuantityField).
export type UnitOption<T extends string> = { value: T; label: string };

// Grammes seulement : aliment sans unité propre.
export const GRAM_UNIT_OPTIONS = [{ value: "grams", label: "g" }] as const;

/*
 * Une quantité se saisit en grammes ou dans une unité qui a un poids :
 * l'unité d'un aliment (tranche, tasse…) ou la portion d'une recette.
 * L'API reçoit toujours des grammes.
 */
export type QuantityUnit = "grams" | "unit";

// Unité propre à un aliment, telle que l'API la retourne.
export type FoodUnitFields = Pick<FoodRead, "unit_name" | "unit_name_plural" | "unit_g">;

export type FoodUnit = { singular: string; plural: string; grams: number };

// L'unité de l'aliment, ou null s'il se saisit seulement en grammes.
export function getFoodUnit(food: FoodUnitFields): FoodUnit | null {
  const grams = food.unit_g === null ? 0 : toNumber(food.unit_g);
  if (!food.unit_name || !food.unit_name_plural || grams <= 0) return null;
  return { singular: food.unit_name, plural: food.unit_name_plural, grams };
}

// L'API accepte au plus deux décimales.
export function roundCents(value: number): number {
  return Math.round(value * 100) / 100;
}

// « tranche » ou « tranches », selon la quantité (même règle que formatCount).
export function unitLabel(unit: FoodUnit, amount: number): string {
  return Number.isFinite(amount) && amount > 1 ? unit.plural : unit.singular;
}

// Options du menu : l'unité de l'aliment d'abord, puis les grammes.
export function foodUnitOptions(unit: FoodUnit | null, amount: number): UnitOption<QuantityUnit>[] {
  if (!unit) return [...GRAM_UNIT_OPTIONS];
  return [
    { value: "unit", label: unitLabel(unit, amount) },
    { value: "grams", label: "g" },
  ];
}

// Quantité saisie ramenée en grammes, arrondie au centième.
export function toGrams(amount: number, unit: QuantityUnit, unitG: number): number {
  return roundCents(unit === "unit" ? amount * unitG : amount);
}

// En grammes, la valeur est envoyée telle quelle : deux décimales au plus.
// Dans une unité, la conversion en grammes est arrondie au centième.
export function hasValidPrecision(amount: number, unit: QuantityUnit): boolean {
  return unit === "unit" || roundCents(amount) === amount;
}

// Valeur saisie convertie d'une unité à l'autre, pour garder la même quantité.
export function convertAmount(amount: number, from: QuantityUnit, to: QuantityUnit, unitG: number): number {
  if (from === to || !(unitG > 0)) return amount;
  return roundCents(to === "grams" ? amount * unitG : amount / unitG);
}

/*
 * Quantité en unités si les grammes tombent sur un quart d'unité (« 2 tranches »,
 * « 1,5 tasse »), sinon null : la quantité s'affiche alors en grammes.
 */
export function gramsToUnitCount(quantityG: number, unitG: number): number | null {
  if (!(unitG > 0) || !(quantityG > 0)) return null;
  const quarters = Math.round((quantityG / unitG) * 4);
  return quarters > 0 && roundCents((quarters / 4) * unitG) === roundCents(quantityG) ? quarters / 4 : null;
}

// Quantité initiale d'un champ : dans l'unité si possible, sinon en grammes.
export function initialQuantity(quantityG: number, unitG: number | null): { unit: QuantityUnit; amount: number } {
  const count = unitG ? gramsToUnitCount(quantityG, unitG) : null;
  return count === null ? { unit: "grams", amount: quantityG } : { unit: "unit", amount: count };
}

// Poids d'une unité sous le champ : « 1 tranche = 25 g », « 2 tranches = 50 g ».
export function unitWeightHint(unit: FoodUnit, amount: number, isEstimated: boolean): string {
  const count = Number.isFinite(amount) && amount > 0 ? amount : 1;
  const sign = isEstimated ? "≈" : "=";
  return `${formatNutrient(count, 2)} ${unitLabel(unit, count)} ${sign} ${formatNutrient(count * unit.grams)} g`;
}
