import type { GoalPace } from "../api/generated/goalPace";
import type { GoalType } from "../api/generated/goalType";
import type { NutritionGoalRead } from "../api/generated/nutritionGoalRead";
import { dayNumber } from "./chart";

export const GOAL_TYPE_LABELS: Record<GoalType, string> = {
  lose_weight: "Perdre du poids",
  maintain_weight: "Maintenir mon poids",
  gain_muscle: "Prendre du muscle",
  body_recomposition: "Recomposition corporelle",
};

// Mêmes rythmes que l'onboarding (WEEKLY_WEIGHT_CHANGE_KG côté backend).
export const GOAL_PACE_LABELS: Record<GoalPace, string> = {
  slow: "Lent · 0,5 lb par semaine",
  moderate: "Modéré · 1 lb par semaine",
  aggressive: "Rapide · 1,5 lb par semaine",
};

/*
 * Trajectoire fixée au départ de l'objectif : une droite du poids de départ
 * (à la date de début) au poids visé (à la date estimée de réussite).
 * Pour un maintien, `end` est null : le poids prévu reste le poids de départ.
 */
export type GoalPlan = {
  start: { key: string; day: number; weight: number };
  end: { key: string; day: number; weight: number } | null;
};

export function goalPlan(goal: NutritionGoalRead): GoalPlan | null {
  const startDay = dayNumber(goal.start_date);
  const startWeight = Number(goal.start_weight_kg);
  if (startDay === null || !Number.isFinite(startWeight)) return null;
  const start = { key: goal.start_date, day: startDay, weight: startWeight };

  if (goal.goal_type === "maintain_weight") return { start, end: null };

  if (goal.target_date !== null && goal.target_weight_kg !== null) {
    const endDay = dayNumber(goal.target_date);
    const endWeight = Number(goal.target_weight_kg);
    if (endDay === null || !Number.isFinite(endWeight) || endDay <= startDay) return null;
    return { start, end: { key: goal.target_date, day: endDay, weight: endWeight } };
  }

  return null;
}

// Poids prévu par la trajectoire à un jour donné (le poids visé une fois la date passée).
export function plannedWeightAt(plan: GoalPlan, day: number): number {
  const { start, end } = plan;
  if (!end || day <= start.day) return start.weight;
  if (day >= end.day) return end.weight;
  return start.weight + ((day - start.day) / (end.day - start.day)) * (end.weight - start.weight);
}
