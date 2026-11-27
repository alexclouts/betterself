import type { GoalTargetRead } from "../../api/generated/goalTargetRead";
import { formatNutrient, type FoodNutrients } from "../../lib/food";
import Card from "../ui/Card";
import { MacroDot } from "../food/MacroBreakdown";
import { MACROS, type MacroKey } from "../../lib/macros";

// Barre de progression d'une valeur consommée par rapport à sa cible.
// Les calories sont en couleur primaire, chaque macro dans sa couleur (lib/macros);
// une cible dépassée passe en rouge.
function ProgressBar({
  value,
  target,
  colorClass = "bg-primary",
}: {
  value: number;
  target: number;
  colorClass?: string;
}) {
  const ratio = target > 0 ? value / target : 0;
  const isOver = ratio > 1;

  return (
    <div
      className="mt-1 h-2 w-full overflow-hidden rounded-full bg-surface-raised"
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={target}
      aria-valuenow={Math.round(value)}
    >
      <div
        className={`h-full rounded-full ${isOver ? "bg-danger" : colorClass}`}
        style={{ width: `${Math.min(ratio, 1) * 100}%` }}
      />
    </div>
  );
}

type DailySummaryCardProps = {
  totals: FoodNutrients;
  // Cible active ; sans cible, seuls les totaux consommés sont affichés.
  target: GoalTargetRead | null;
  className?: string;
};

// Résumé nutritionnel d'une journée : calories et macros consommées vs cible.
export function DailySummaryCard({ totals, target, className = "" }: DailySummaryCardProps) {
  const caloriesTarget = target?.calories_target_kcal ?? null;

  const targets: Record<MacroKey, number | undefined> = {
    protein_g: target?.protein_target_g,
    carbohydrates_g: target?.carbs_target_g,
    fat_g: target?.fat_target_g,
  };
  const macros = MACROS.map((macro) => ({
    ...macro,
    value: totals[macro.key],
    target: targets[macro.key],
  }));

  return (
    <Card className={`w-full bg-surface ${className}`}>
      <dl className="grid grid-cols-3 gap-3">
        <div className="col-span-3">
          <dt>Calories</dt>
          <dd className="text-foreground">
            <span className="text-3xl font-bold">{formatNutrient(totals.calories_kcal, 0)}</span>
            {caloriesTarget !== null && (
              <span className="text-base font-normal text-muted"> / {caloriesTarget} kcal</span>
            )}
            {caloriesTarget === null && " kcal"}
          </dd>
          {caloriesTarget !== null && (
            <ProgressBar value={totals.calories_kcal} target={caloriesTarget} />
          )}
        </div>

        {macros.map((macro) => (
          <div key={macro.label} className="mt-2">
            <dt className="flex items-center gap-1.5">
              <MacroDot bgClass={macro.bgClass} />
              {macro.label}
            </dt>
            <dd className="text-foreground">
              <span className="text-xl font-bold">{formatNutrient(macro.value, 0)}</span>
              {macro.target !== undefined && (
                <span className="text-sm font-normal text-muted"> / {macro.target} g</span>
              )}
              {macro.target === undefined && " g"}
            </dd>
            {macro.target !== undefined && (
              <ProgressBar value={macro.value} target={macro.target} colorClass={macro.bgClass} />
            )}
          </div>
        ))}
      </dl>
    </Card>
  );
}
