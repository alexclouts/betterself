import { useMemo, useState } from "react";
import type { MeasurementRead } from "../../api/generated/measurementRead";
import { useElementWidth } from "../../hooks/useElementWidth";
import { WeightGrid } from "../charts/WeightGrid";
import { dayNumber, formatKg, nearestIndex, weightAxis } from "../../lib/chart";
import { formatLongDate, formatShortDate } from "../../lib/date";

/*
 * Courbe du poids au fil du temps, en SVG (aucune dépendance).
 * - L'axe horizontal est proportionnel au temps : un écart de deux semaines
 *   entre deux mesures se voit comme tel.
 * - Survol (ou flèches du clavier) : ligne verticale + infobulle sur la mesure la plus proche.
 * - Les données restent lisibles sans le graphique via le tableau « Voir les données ».
 */

const HEIGHT = 200;
const MARGIN = { top: 24, right: 16, bottom: 28, left: 40 };
// Au-delà, les points se chevauchent : on ne garde que la ligne.
const MAX_MARKERS = 40;
// La ligne utilise --primary-dark : --primary n'atteint pas un contraste de 3:1 sur fond blanc.
const LINE_COLOR = "var(--primary-dark)";

type Point = { key: string; weight: number; day: number };

function formatDelta(value: number): string {
  const sign = value > 0 ? "+" : value < 0 ? "−" : "±";
  return `${sign}${formatKg(Math.abs(value))} kg`;
}

export function WeightChart({ measurements }: { measurements: MeasurementRead[] }) {
  const [containerRef, width] = useElementWidth<HTMLDivElement>();
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  const points = useMemo<Point[]>(
    () =>
      measurements.flatMap((m) => {
        const day = dayNumber(m.date);
        return day !== null ? [{ key: m.date, weight: m.weight_kg, day }] : [];
      }),
    [measurements],
  );

  if (points.length === 0) {
    return <p className="text-sm">Aucune mesure pour l’instant. Enregistrez votre poids pour voir votre courbe.</p>;
  }

  const first = points[0];
  const last = points[points.length - 1];
  const innerWidth = Math.max(0, width - MARGIN.left - MARGIN.right);
  const innerHeight = HEIGHT - MARGIN.top - MARGIN.bottom;

  // Une seule mesure : on centre le point sur une fenêtre de deux jours.
  const dayLo = points.length > 1 ? first.day : first.day - 1;
  const dayHi = points.length > 1 ? last.day : last.day + 1;
  const { lo, hi, ticks } = weightAxis(points.map((p) => p.weight));

  const x = (day: number) => MARGIN.left + ((day - dayLo) / (dayHi - dayLo)) * innerWidth;
  const y = (weight: number) => MARGIN.top + (1 - (weight - lo) / (hi - lo)) * innerHeight;

  const path = points.map((p, i) => `${i === 0 ? "M" : "L"}${x(p.day)},${y(p.weight)}`).join(" ");
  const spansYears = first.key.slice(0, 4) !== last.key.slice(0, 4);
  const xTicks = points.length > 1 ? [first, last] : [first];
  const showMarkers = points.length <= MAX_MARKERS;

  const active = activeIndex !== null ? points[activeIndex] : null;
  const previous = activeIndex !== null && activeIndex > 0 ? points[activeIndex - 1] : null;

  // Mesure dont la date est la plus proche du pointeur.
  function handlePointerMove(event: React.PointerEvent<SVGSVGElement>) {
    const rect = event.currentTarget.getBoundingClientRect();
    setActiveIndex(nearestIndex(points.map((p) => x(p.day)), event.clientX - rect.left));
  }

  function handleKeyDown(event: React.KeyboardEvent<SVGSVGElement>) {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    const delta = event.key === "ArrowLeft" ? -1 : 1;
    setActiveIndex((index) =>
      Math.min(points.length - 1, Math.max(0, (index ?? points.length - 1) + (index === null ? 0 : delta))),
    );
  }

  const summary = points.length > 1
      ? `Poids du ${formatLongDate(first.key)} au ${formatLongDate(last.key)} : de ${formatKg(first.weight)} kg à ${formatKg(last.weight)} kg.`
      : `Une mesure : ${formatKg(first.weight)} kg le ${formatLongDate(first.key)}.`;

  // L'infobulle bascule à gauche du point dans la moitié droite du graphique.
  const tooltipOnLeft = active ? x(active.day) > width / 2 : false;

  return (
    <div className="text-left">
      {points.length > 1 && (
        <p className="text-sm">
          <span className="font-semibold text-foreground">{formatDelta(last.weight - first.weight)}</span>{" "}
          depuis le {formatLongDate(first.key)}
        </p>
      )}

      <div ref={containerRef} className="relative mt-2 w-full">
        {width > 0 && (
          <svg
            width={width}
            height={HEIGHT}
            role="img"
            aria-label={summary}
            tabIndex={0}
            className="block touch-none outline-none focus-visible:ring-2 focus-visible:ring-primary/30 rounded"
            onPointerMove={handlePointerMove}
            onPointerLeave={() => setActiveIndex(null)}
            onKeyDown={handleKeyDown}
            onBlur={() => setActiveIndex(null)}
          >
            {/* Grille et axe des poids : discrets, derrière la courbe. */}
            <WeightGrid ticks={ticks} baseline={lo} y={y} left={MARGIN.left} right={width - MARGIN.right} />

            {/* Axe du temps : première et dernière date. */}
            {xTicks.map((p, i) => (
              <text
                key={p.key}
                x={x(p.day)}
                y={HEIGHT - 8}
                textAnchor={xTicks.length === 1 ? "middle" : i === 0 ? "start" : "end"}
                fontSize={12}
                fill="var(--muted)"
              >
                {formatShortDate(p.key, spansYears)}
              </text>
            ))}

            <path d={path} fill="none" stroke={LINE_COLOR} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />

            {showMarkers &&
              points.map((p) => (
                <circle
                  key={p.key}
                  cx={x(p.day)}
                  cy={y(p.weight)}
                  r={4}
                  fill={LINE_COLOR}
                  stroke="var(--surface)"
                  strokeWidth={2}
                />
              ))}

            {/* Étiquette directe de la dernière valeur (masquée pendant le survol). */}
            {!active && (
              <text
                x={x(last.day)}
                y={y(last.weight) - 10}
                textAnchor={points.length > 1 ? "end" : "middle"}
                fontSize={12}
                fontWeight={600}
                fill="var(--foreground)"
              >
                {formatKg(last.weight)} kg
              </text>
            )}

            {active && (
              <g pointerEvents="none">
                <line
                  x1={x(active.day)}
                  x2={x(active.day)}
                  y1={MARGIN.top}
                  y2={HEIGHT - MARGIN.bottom}
                  stroke="var(--muted)"
                  strokeOpacity={0.6}
                />
                <circle
                  cx={x(active.day)}
                  cy={y(active.weight)}
                  r={6}
                  fill={LINE_COLOR}
                  stroke="var(--surface)"
                  strokeWidth={2}
                />
              </g>
            )}
          </svg>
        )}

        {active && (
          <div
            role="status"
            className="pointer-events-none absolute top-0 z-10 rounded-lg border border-border bg-surface-overlay px-3 py-2 text-sm shadow-md whitespace-nowrap"
            style={
              tooltipOnLeft
                ? { right: width - x(active.day) + 12 }
                : { left: x(active.day) + 12 }
            }
          >
            <div className="text-muted">{formatLongDate(active.key)}</div>
            <div className="font-semibold text-foreground">{formatKg(active.weight)} kg</div>
            {previous && (
              <div className="text-muted">{formatDelta(active.weight - previous.weight)} vs mesure précédente</div>
            )}
          </div>
        )}
      </div>

      <details className="mt-3 text-sm">
        <summary className="cursor-pointer text-muted">Voir les données</summary>
        <table className="mt-2 w-full">
          <thead>
            <tr className="text-muted">
              <th className="py-1 text-left font-normal">Date</th>
              <th className="py-1 text-right font-normal">Poids</th>
            </tr>
          </thead>
          <tbody>
            {[...points].reverse().map((p) => (
              <tr key={p.key} className="border-t border-border/50">
                <td className="py-1">{formatLongDate(p.key)}</td>
                <td className="py-1 text-right tabular-nums">{formatKg(p.weight)} kg</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}
