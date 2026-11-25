import { formatKg } from "../../lib/chart";

type WeightGridProps = {
  ticks: number[];
  // Graduation du bas, tracée en trait plein (les autres sont en pointillé).
  baseline: number;
  y: (weight: number) => number;
  left: number;
  right: number;
};

// Grille horizontale et graduations de l'axe des poids : discrètes, derrière les courbes.
export function WeightGrid({ ticks, baseline, y, left, right }: WeightGridProps) {
  return (
    <>
      {ticks.map((tick) => (
        <g key={tick}>
          <line
            x1={left}
            x2={right}
            y1={y(tick)}
            y2={y(tick)}
            stroke="var(--border)"
            strokeOpacity={0.5}
            strokeDasharray={tick === baseline ? undefined : "2 4"}
          />
          <text x={left - 8} y={y(tick)} dy="0.32em" textAnchor="end" fontSize={12} fill="var(--muted)">
            {formatKg(tick)}
          </text>
        </g>
      ))}
    </>
  );
}
