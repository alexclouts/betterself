import type { GoalTargetRead } from "../../api/generated/goalTargetRead";
import { formatNutrient, type FoodNutrients } from "../../lib/food";
import Card from "../ui/Card";

// Barre de progression d'une valeur consommée par rapport à sa cible.
// Les calories sont en couleur primaire, les macros en couleur secondaire;
// une cible dépassée passe en rouge.
function ProgressBar({
  value,
  target,
  color = "primary",
}: {
  value: number;
  target: number;
  color?: "primary" | "secondary";
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
        className={`h-full rounded-full ${isOver ? "bg-danger" : color === "secondary" ? "bg-secondary" : "bg-primary"}`}
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
  const caloriesRemaining =
    caloriesTarget !== null ? caloriesTarget - totals.calories_kcal : null;

  const macros = [
    { label: "Protéines", value: totals.protein_g, target: target?.protein_target_g },
    { label: "Glucides", value: totals.carbohydrates_g, target: target?.carbs_target_g },
    { label: "Lipides", value: totals.fat_g, target: target?.fat_target_g },
  ];

  return (
    <Card className={`w-full bg-surface ${className}`}>
      <dl className="grid grid-cols-3 gap-3">
        <div className="col-span-3">
          <dt>Calories</dt>
          <dd className="text-2xl font-semibold">
            {formatNutrient(totals.calories_kcal, 0)}
            {caloriesTarget !== null && (
              <span className="text-base font-normal"> / {caloriesTarget} kcal</span>
            )}
            {caloriesTarget === null && " kcal"}
          </dd>
          {caloriesTarget !== null && caloriesRemaining !== null && (
            <>
              <ProgressBar value={totals.calories_kcal} target={caloriesTarget} />
              <p className={`mt-1 ${caloriesRemaining < 0 ? "text-danger" : ""}`}>
                {caloriesRemaining >= 0
                  ? `${formatNutrient(caloriesRemaining, 0)} kcal restantes`
                  : `${formatNutrient(-caloriesRemaining, 0)} kcal au-dessus de la cible`}
              </p>
            </>
          )}
        </div>

        {macros.map((macro) => (
          <div key={macro.label} className="mt-2">
            <dt>{macro.label}</dt>
            <dd>
              {formatNutrient(macro.value, 0)}
              {macro.target !== undefined && (
                <span className="text-base font-normal"> / {macro.target} g</span>
              )}
              {macro.target === undefined && " g"}
            </dd>
            {macro.target !== undefined && (
              <ProgressBar value={macro.value} target={macro.target} color="secondary" />
            )}
          </div>
        ))}
      </dl>
    </Card>
  );
}
