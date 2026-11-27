import type { FoodNutrients } from "./food";

export type MacroKey = "protein_g" | "carbohydrates_g" | "fat_g";

/*
 * Macronutriments et leur couleur, partout dans l'application :
 * protéines en secondaire (orange), glucides en tertiaire (violet), lipides en quaternaire (bleu).
 * Le vert (primaire) est réservé aux calories.
 */
export const MACROS: readonly {
  key: MacroKey;
  label: string;
  kcalPerGram: number;
  // Classe de fond Tailwind (pastille, barre).
  bgClass: string;
}[] = [
  { key: "protein_g", label: "Protéines", kcalPerGram: 4, bgClass: "bg-secondary" },
  { key: "carbohydrates_g", label: "Glucides", kcalPerGram: 4, bgClass: "bg-tertiary" },
  { key: "fat_g", label: "Lipides", kcalPerGram: 9, bgClass: "bg-quaternary" },
];

/*
 * Part de chaque macronutriment dans les calories qu'ils apportent (4/4/9 kcal par gramme),
 * en pourcentage. Tous à 0 si l'aliment n'a aucun macronutriment.
 */
export function macroCalorieShares(nutrients: FoodNutrients): Record<MacroKey, number> {
  const kcal = MACROS.map((macro) => Math.max(nutrients[macro.key], 0) * macro.kcalPerGram);
  const total = kcal.reduce((sum, value) => sum + value, 0);
  const [protein_g, carbohydrates_g, fat_g] = kcal.map((value) => (total > 0 ? (value / total) * 100 : 0));
  return { protein_g, carbohydrates_g, fat_g };
}
