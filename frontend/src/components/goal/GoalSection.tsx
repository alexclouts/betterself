import type { NutritionGoalRead } from "../../api/generated/nutritionGoalRead";
import { useCurrentGoal } from "../../hooks/useCurrentGoal";
import { useMeasurements } from "../../hooks/useMeasurements";
import { dayNumber, formatKg } from "../../lib/chart";
import { formatLongDate, todayKey } from "../../lib/date";
import { GOAL_PACE_LABELS, GOAL_TYPE_LABELS, goalPlan } from "../../lib/goal";
import Card from "../ui/Card";
import DetailList, { type DetailRow } from "../ui/DetailList";
import { GoalChart } from "./GoalChart";

/*
 * Section « Mon objectif » du profil. Chaque information est une ligne de la
 * liste `rows`, et le graphique suit : d'autres informations sur l'objectif
 * (modification, historique des cibles…) pourront s'y ajouter sans changer la page.
 */

// Temps restant avant la date estimée : « dans 3 semaines », « dans 4 jours », « date dépassée ».
function formatRemaining(targetKey: string): string {
  const target = dayNumber(targetKey);
  const today = dayNumber(todayKey());
  if (target === null || today === null) return "";
  // Arrondi : un changement d'heure décale les minuits d'une heure.
  const days = Math.round(target - today);
  if (days < 0) return "date dépassée";
  if (days === 0) return "aujourd’hui";
  if (days < 14) return `dans ${days} jour${days > 1 ? "s" : ""}`;
  return `dans ${Math.round(days / 7)} semaines`;
}

// Progression vers le poids visé : « 4,2 kg sur 10 kg (42 %) ». null sans poids visé.
function formatProgress(goal: NutritionGoalRead, currentKg: number | null): string | null {
  if (goal.target_weight_kg === null || currentKg === null) return null;
  const start = Number(goal.start_weight_kg);
  const target = Number(goal.target_weight_kg);
  const total = target - start;
  if (total === 0) return null;
  // Positif dans le sens de l'objectif ; négatif si l'on s'en est éloigné.
  const done = currentKg - start;
  const percent = Math.round(Math.min(1, Math.max(0, done / total)) * 100);
  const doneLabel = Math.sign(done) === Math.sign(total) ? formatKg(Math.abs(done)) : "0";
  return `${doneLabel} kg sur ${formatKg(Math.abs(total))} kg (${percent} %)`;
}

export function GoalSection() {
  const { goal, isLoading, error } = useCurrentGoal();
  const { measurements, latest } = useMeasurements();

  const plan = goal ? goalPlan(goal) : null;
  const progress = goal ? formatProgress(goal, latest?.weight_kg ?? null) : null;

  const rows = goal
    ? [
        { label: "Objectif", value: GOAL_TYPE_LABELS[goal.goal_type] },
        goal.goal_pace && { label: "Rythme", value: GOAL_PACE_LABELS[goal.goal_pace] },
        {
          label: "Poids de départ",
          value: `${formatKg(Number(goal.start_weight_kg))} kg le ${formatLongDate(goal.start_date)}`,
        },
        goal.target_weight_kg !== null && {
          label: "Poids visé",
          value: `${formatKg(Number(goal.target_weight_kg))} kg`,
        },
        goal.target_date !== null && {
          label: "Date estimée",
          value: `${formatLongDate(goal.target_date)} (${formatRemaining(goal.target_date)})`,
        },
        progress && { label: "Progression", value: progress },
      ].filter((row): row is DetailRow => Boolean(row))
    : [];

  return (
    <section className="mt-8" aria-labelledby="goal-heading">
      <Card className="w-full bg-surface">
        <h2 id="goal-heading" className="mt-0 mb-3 text-left text-xl">Mon objectif</h2>

        {isLoading ? (
          <p>Chargement de votre objectif…</p>
        ) : error ? (
          <p className="text-danger" role="alert">{error}</p>
        ) : !goal ? (
          <p>Aucun objectif actif.</p>
        ) : (
          <>
            <DetailList rows={rows} />

            {plan ? (
              <div className="mt-6">
                <GoalChart plan={plan} measurements={measurements} />
              </div>
            ) : (
              <p className="mt-6 text-sm text-muted">
                Cet objectif n’a pas de trajectoire de poids à afficher.
              </p>
            )}
          </>
        )}
      </Card>
    </section>
  );
}
