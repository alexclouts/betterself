import type { NutritionGoalRead } from "../api/generated/nutritionGoalRead";

/*
 * Sens d'une variation de poids par rapport à l'objectif de l'utilisateur :
 * - toward  : le poids se rapproche de l'objectif (affiché en vert) ;
 * - away    : le poids s'en éloigne (affiché en rouge) ;
 * - neutral : aucune variation, ou l'objectif ne permet pas de juger.
 */
export type WeightTrend = "toward" | "away" | "neutral";

// Poids visé : le poids cible s'il est défini ; pour un maintien, le poids de départ.
function referenceWeight(goal: NutritionGoalRead): number | null {
  if (goal.goal_type === "maintain_weight") return Number(goal.start_weight_kg);
  if (goal.target_weight_kg !== null) return Number(goal.target_weight_kg);
  return null;
}

export function weightTrend(
  previousKg: number,
  currentKg: number,
  goal: NutritionGoalRead | null,
): WeightTrend {
  // Même arrondi que l'affichage : une variation affichée vide reste neutre.
  const delta = Math.round((currentKg - previousKg) * 10) / 10;
  if (!goal || delta === 0) return "neutral";

  // Avec un poids visé : on compare la distance avant et après la mesure.
  // Cela couvre aussi le dépassement de l'objectif (ex. perdre sous le poids cible).
  const reference = referenceWeight(goal);
  if (reference !== null && Number.isFinite(reference)) {
    const before = Math.abs(previousKg - reference);
    const after = Math.abs(currentKg - reference);
    if (after < before) return "toward";
    if (after > before) return "away";
    return "neutral";
  }

  // Sans poids visé : seul le sens de l'objectif compte.
  switch (goal.goal_type) {
    case "lose_weight":
      return delta < 0 ? "toward" : "away";
    case "gain_muscle":
      return delta > 0 ? "toward" : "away";
    default:
      // Recomposition corporelle : le poids seul ne dit pas si l'on progresse.
      return "neutral";
  }
}
