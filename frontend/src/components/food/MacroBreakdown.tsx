import { formatNutrient, type FoodNutrients } from "../../lib/food";
import { MACROS, macroCalorieShares } from "../../lib/macros";

// Pastille de couleur d'un macronutriment, à placer devant son nom.
export function MacroDot({ bgClass }: { bgClass: string }) {
  return <span aria-hidden="true" className={`inline-block h-2.5 w-2.5 shrink-0 rounded-full ${bgClass}`} />;
}

type MacroBreakdownProps = {
  // Valeurs à représenter; null affiche des tirets (quantité invalide).
  nutrients: FoodNutrients | null;
  className?: string;
};

/*
 * Protéines, glucides et lipides : une barre empilée montre la part de chacun
 * dans les calories, puis chaque valeur en grammes avec sa couleur et son pourcentage.
 */
export function MacroBreakdown({ nutrients, className = "" }: MacroBreakdownProps) {
  const shares = nutrients ? macroCalorieShares(nutrients) : null;
  const hasShares = shares !== null && MACROS.some((macro) => shares[macro.key] > 0);
  const description = hasShares
    ? `Répartition des calories : ${MACROS.map((macro) => `${macro.label.toLowerCase()} ${Math.round(shares[macro.key])} %`).join(", ")}`
    : "Répartition des calories indisponible";

  return (
    <div className={className}>
      <div
        role="img"
        aria-label={description}
        className="flex h-3 w-full gap-0.5 overflow-hidden rounded-full bg-surface-raised"
      >
        {hasShares &&
          MACROS.map((macro) =>
            shares[macro.key] > 0 ? (
              <div
                key={macro.key}
                className={`h-full ${macro.bgClass} transition-[width] duration-300`}
                style={{ width: `${shares[macro.key]}%` }}
              />
            ) : null,
          )}
      </div>

      <dl className="mt-4 grid grid-cols-3 gap-3 text-center">
        {MACROS.map((macro) => (
          <div key={macro.key}>
            <dt className="flex items-center justify-center gap-1.5 text-sm text-muted">
              <MacroDot bgClass={macro.bgClass} />
              {macro.label}
            </dt>
            <dd className="mt-1 text-xl font-semibold text-foreground">
              {nutrients ? formatNutrient(nutrients[macro.key]) : "–"} g
            </dd>
            <dd className="text-sm text-muted">{hasShares ? `${Math.round(shares[macro.key])} %` : "–"}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
