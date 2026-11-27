import type { FoodRead } from "../api/generated/foodRead";
import { formatNutrient, toNumber } from "./food";

// Unités de saisie des quantités (components/ui/QuantityField).
export type UnitOption<T extends string> = { value: T; label: string };

/*
 * Une quantité se saisit en grammes ou dans une unité qui a un poids : l'unité
 * d'un aliment (tranche, tasse…) ou la portion d'une recette. L'API reçoit
 * toujours des grammes. La valeur du menu est GRAMS ou la clé d'une unité.
 */
export const GRAMS = "grams";

export type QuantityUnit = string;

export type FoodUnit = { key: string; singular: string; plural: string; grams: number };

// Grammes seulement : aliment sans unité propre.
export const GRAM_UNIT_OPTIONS = [{ value: GRAMS, label: "g" }] as const;

// Unité propre à un aliment, telle que l'API la retourne.
export type FoodUnitFields = Pick<FoodRead, "unit_name" | "unit_name_plural" | "unit_g">;

// Mesures de cuisine canadiennes, en ml : une unité de ce type les propose toutes.
const MEASURES = [
  { singular: "tasse", plural: "tasses", ml: 250 },
  { singular: "c. à soupe", plural: "c. à soupe", ml: 15 },
  { singular: "c. à thé", plural: "c. à thé", ml: 5 },
];

function unit(singular: string, plural: string, grams: number): FoodUnit {
  return { key: singular, singular, plural, grams };
}

// L'unité de l'aliment, ou null s'il se saisit seulement en grammes.
export function getFoodUnit(food: FoodUnitFields): FoodUnit | null {
  const grams = food.unit_g === null ? 0 : toNumber(food.unit_g);
  if (!food.unit_name || !food.unit_name_plural || grams <= 0) return null;
  return unit(food.unit_name, food.unit_name_plural, grams);
}

/*
 * Unités proposées pour l'aliment. Une mesure de cuisine (tasse, c. à soupe,
 * c. à thé) donne les trois, au prorata de leur volume : si 1 tasse = 250 g,
 * 1 c. à soupe = 15 g.
 */
export function getFoodUnits(food: FoodUnitFields): FoodUnit[] {
  const main = getFoodUnit(food);
  if (!main) return [];

  const measure = MEASURES.find((item) => item.singular === main.singular);
  if (!measure) return [main];

  const gramsPerMl = main.grams / measure.ml;
  return MEASURES.map((item) =>
    item === measure ? main : unit(item.singular, item.plural, roundCents(item.ml * gramsPerMl)),
  );
}

// L'unité choisie dans le menu, ou null pour les grammes.
export function findUnit(units: FoodUnit[], key: QuantityUnit): FoodUnit | null {
  return units.find((item) => item.key === key) ?? null;
}

// L'API accepte au plus deux décimales.
export function roundCents(value: number): number {
  return Math.round(value * 100) / 100;
}

// « tranche » ou « tranches », selon la quantité (même règle que formatCount).
export function unitLabel(unit: FoodUnit, amount: number): string {
  return Number.isFinite(amount) && amount > 1 ? unit.plural : unit.singular;
}

// Options du menu : les unités de l'aliment, puis les grammes.
export function unitOptions(units: FoodUnit[], amount: number): UnitOption<QuantityUnit>[] {
  return [
    ...units.map((item) => ({ value: item.key, label: unitLabel(item, amount) })),
    { value: GRAMS, label: "g" },
  ];
}

// Quantité saisie ramenée en grammes, arrondie au centième.
export function toGrams(amount: number, unit: FoodUnit | null): number {
  return roundCents(unit ? amount * unit.grams : amount);
}

// En grammes, la valeur est envoyée telle quelle : deux décimales au plus.
// Dans une unité, la conversion en grammes est arrondie au centième.
export function hasValidPrecision(amount: number, unit: FoodUnit | null): boolean {
  return unit !== null || roundCents(amount) === amount;
}

// Valeur saisie convertie d'une unité à l'autre (null : grammes), pour garder la même quantité.
export function convertAmount(amount: number, from: FoodUnit | null, to: FoodUnit | null): number {
  const grams = amount * (from?.grams ?? 1);
  return roundCents(grams / (to?.grams ?? 1));
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

// Quantité initiale d'un champ : dans la première unité où elle tombe juste, sinon en grammes.
export function initialQuantity(quantityG: number, units: FoodUnit[]): { unit: QuantityUnit; amount: number } {
  for (const item of units) {
    const count = gramsToUnitCount(quantityG, item.grams);
    if (count !== null) return { unit: item.key, amount: count };
  }
  return { unit: GRAMS, amount: quantityG };
}

// Poids sous le champ : « 1 tranche = 25 g », « 2 tasses ≈ 500 g » (poids estimé).
export function unitWeightHint(unit: FoodUnit, amount: number, isEstimated: boolean): string {
  const count = Number.isFinite(amount) && amount > 0 ? amount : 1;
  const sign = isEstimated ? "≈" : "=";
  return `${formatNutrient(count, 2)} ${unitLabel(unit, count)} ${sign} ${formatNutrient(count * unit.grams)} g`;
}
