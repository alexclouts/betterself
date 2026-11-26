import { useMemo, useState } from "react";
import type { MeasurementRead } from "../../api/generated/measurementRead";
import { useElementWidth } from "../../hooks/useElementWidth";
import { WeightGrid } from "../charts/WeightGrid";
import { dayNumber, formatKg, nearestIndex, weightAxis } from "../../lib/chart";
import { formatLongDate, formatShortDate, todayKey } from "../../lib/date";
import { plannedWeightAt, type GoalPlan } from "../../lib/goal";

/*
 * Trajectoire de l'objectif, en SVG (aucune dépendance) :
 * - en pointillé, la trajectoire fixée au départ : du poids de départ au poids
 *   visé, entre la date de début et la date estimée de réussite ;
 * - en trait plein, le poids réellement mesuré depuis le début de l'objectif.
 * L'axe du temps va du début de l'objectif à la date estimée (ou à aujourd'hui
 * si elle est dépassée) : on voit où l'on en est sur le chemin prévu.
 * Survol (ou flèches du clavier) : poids mesuré et poids prévu à cette date.
 */

const HEIGHT = 220;
const MARGIN = { top: 28, right: 20, bottom: 28, left: 40 };
const MAX_MARKERS = 40;
const ACTUAL_COLOR = "var(--chart-actual)";
const PLAN_COLOR = "var(--chart-plan)";

type Point = { key: string; day: number; weight: number; planned: number };

function formatSignedKg(value: number): string {
  const rounded = Math.round(value * 10) / 10;
  if (rounded === 0) return "pile sur la trajectoire";
  const sign = rounded > 0 ? "+" : "−";
  return `${sign}${formatKg(Math.abs(rounded))} kg par rapport au prévu`;
}

type GoalChartProps = {
  plan: GoalPlan;
  // Mesures quotidiennes (une par jour), triées par date croissante.
  measurements: MeasurementRead[];
};

export function GoalChart({ plan, measurements }: GoalChartProps) {
  const [containerRef, width] = useElementWidth<HTMLDivElement>();
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  // Seules les mesures prises depuis le début de l'objectif sont comparées à la trajectoire.
  const points = useMemo<Point[]>(
    () =>
      measurements.flatMap((m) => {
        const day = dayNumber(m.date);
        if (day === null || day < plan.start.day) return [];
        return [{ key: m.date, day, weight: m.weight_kg, planned: plannedWeightAt(plan, day) }];
      }),
    [measurements, plan],
  );

  const today = dayNumber(todayKey()) ?? plan.start.day;
  const last = points.at(-1) ?? null;
  const dayLo = plan.start.day;
  // Un maintien n'a pas de date de fin : l'axe va jusqu'à aujourd'hui (au moins une semaine).
  const dayHi = Math.max(plan.end?.day ?? dayLo + 7, today, last?.day ?? dayLo);
  const planEndWeight = plan.end?.weight ?? plan.start.weight;

  const innerWidth = Math.max(0, width - MARGIN.left - MARGIN.right);
  const innerHeight = HEIGHT - MARGIN.top - MARGIN.bottom;
  const { lo, hi, ticks } = weightAxis([plan.start.weight, planEndWeight, ...points.map((p) => p.weight)]);

  const x = (day: number) => MARGIN.left + ((day - dayLo) / (dayHi - dayLo)) * innerWidth;
  const y = (weight: number) => MARGIN.top + (1 - (weight - lo) / (hi - lo)) * innerHeight;

  // La trajectoire prévue se prolonge à plat après la date estimée, jusqu'au bout de l'axe.
  const planEndDay = plan.end?.day ?? dayHi;
  const planPath =
    `M${x(dayLo)},${y(plan.start.weight)} L${x(planEndDay)},${y(planEndWeight)}` +
    (planEndDay < dayHi ? ` L${x(dayHi)},${y(planEndWeight)}` : "");
  const actualPath = points.map((p, i) => `${i === 0 ? "M" : "L"}${x(p.day)},${y(p.weight)}`).join(" ");

  const endKey = plan.end?.key ?? todayKey();
  const spansYears = plan.start.key.slice(0, 4) !== endKey.slice(0, 4);
  const showToday = today > dayLo && today < dayHi;
  const active = activeIndex !== null ? points[activeIndex] : null;
  const tooltipOnLeft = active ? x(active.day) > width / 2 : false;

  const summary = [
    plan.end
      ? `Trajectoire prévue : de ${formatKg(plan.start.weight)} kg le ${formatLongDate(plan.start.key)} à ${formatKg(plan.end.weight)} kg le ${formatLongDate(plan.end.key)}.`
      : `Poids à maintenir : ${formatKg(plan.start.weight)} kg depuis le ${formatLongDate(plan.start.key)}.`,
    last ? `Dernière mesure : ${formatKg(last.weight)} kg le ${formatLongDate(last.key)}, ${formatSignedKg(last.weight - last.planned)}.` : "",
  ].join(" ");

  function handlePointerMove(event: React.PointerEvent<SVGSVGElement>) {
    if (points.length === 0) return;
    const rect = event.currentTarget.getBoundingClientRect();
    setActiveIndex(nearestIndex(points.map((p) => x(p.day)), event.clientX - rect.left));
  }

  function handleKeyDown(event: React.KeyboardEvent<SVGSVGElement>) {
    if (points.length === 0 || (event.key !== "ArrowLeft" && event.key !== "ArrowRight")) return;
    event.preventDefault();
    const step = event.key === "ArrowLeft" ? -1 : 1;
    setActiveIndex((index) =>
      index === null ? points.length - 1 : Math.min(points.length - 1, Math.max(0, index + step)),
    );
  }

  return (
    <div className="text-left">
      {/* Légende : deux séries, distinguées aussi par le motif du trait (plein / pointillé). */}
      <ul className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted" aria-hidden="true">
        <li className="flex items-center gap-2">
          <svg width="20" height="8"><line x1="0" x2="20" y1="4" y2="4" stroke={ACTUAL_COLOR} strokeWidth={2} /></svg>
          Mon poids
        </li>
        <li className="flex items-center gap-2">
          <svg width="20" height="8"><line x1="0" x2="20" y1="4" y2="4" stroke={PLAN_COLOR} strokeWidth={2} strokeDasharray="4 3" /></svg>
          {plan.end ? "Trajectoire prévue" : "Poids à maintenir"}
        </li>
      </ul>

      <div ref={containerRef} className="relative mt-2 w-full">
        {width > 0 && (
          <svg
            width={width}
            height={HEIGHT}
            role="img"
            aria-label={summary}
            tabIndex={0}
            className="block touch-none rounded outline-none focus-visible:ring-2 focus-visible:ring-primary/30"
            onPointerMove={handlePointerMove}
            onPointerLeave={() => setActiveIndex(null)}
            onKeyDown={handleKeyDown}
            onBlur={() => setActiveIndex(null)}
          >
            {/* Grille et axe des poids : discrets, derrière les courbes. */}
            <WeightGrid ticks={ticks} baseline={lo} y={y} left={MARGIN.left} right={width - MARGIN.right} />

            {/* Axe du temps : début de l'objectif et date estimée de réussite. */}
            <text x={x(dayLo)} y={HEIGHT - 8} textAnchor="start" fontSize={12} fill="var(--muted)">
              {formatShortDate(plan.start.key, spansYears)}
            </text>
            <text x={x(dayHi)} y={HEIGHT - 8} textAnchor="end" fontSize={12} fill="var(--muted)">
              {formatShortDate(plan.end && plan.end.day >= dayHi ? plan.end.key : todayKey(), spansYears)}
            </text>

            {/* Repère d'aujourd'hui. */}
            {showToday && (
              <g>
                <line
                  x1={x(today)}
                  x2={x(today)}
                  y1={MARGIN.top}
                  y2={HEIGHT - MARGIN.bottom}
                  stroke="var(--muted)"
                  strokeOpacity={0.5}
                  strokeDasharray="2 3"
                />
                <text x={x(today)} y={MARGIN.top - 10} textAnchor="middle" fontSize={11} fill="var(--muted)">
                  Aujourd’hui
                </text>
              </g>
            )}

            <path d={planPath} fill="none" stroke={PLAN_COLOR} strokeWidth={2} strokeDasharray="6 4" strokeLinecap="round" />

            {/* Poids visé à la date estimée, étiqueté directement. */}
            {plan.end && (
              <g>
                <circle cx={x(plan.end.day)} cy={y(plan.end.weight)} r={5} fill={PLAN_COLOR} stroke="var(--surface)" strokeWidth={2} />
                <text
                  x={x(plan.end.day)}
                  y={y(plan.end.weight) + (plan.end.weight < plan.start.weight ? 18 : -10)}
                  textAnchor="end"
                  fontSize={12}
                  fontWeight={600}
                  fill="var(--foreground)"
                >
                  Objectif {formatKg(plan.end.weight)} kg
                </text>
              </g>
            )}

            {points.length > 0 && (
              <path d={actualPath} fill="none" stroke={ACTUAL_COLOR} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
            )}
            {points.length <= MAX_MARKERS &&
              points.map((p) => (
                <circle key={p.key} cx={x(p.day)} cy={y(p.weight)} r={4} fill={ACTUAL_COLOR} stroke="var(--surface)" strokeWidth={2} />
              ))}

            {/* Étiquette directe de la dernière mesure (masquée pendant le survol). */}
            {last && !active && (
              <text
                x={x(last.day)}
                y={y(last.weight) + (last.weight >= last.planned ? -10 : 18)}
                textAnchor={x(last.day) > width / 2 ? "end" : "start"}
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
                <circle cx={x(active.day)} cy={y(active.planned)} r={5} fill={PLAN_COLOR} stroke="var(--surface)" strokeWidth={2} />
                <circle cx={x(active.day)} cy={y(active.weight)} r={6} fill={ACTUAL_COLOR} stroke="var(--surface)" strokeWidth={2} />
              </g>
            )}
          </svg>
        )}

        {active && (
          <div
            role="status"
            className="pointer-events-none absolute top-0 z-10 whitespace-nowrap rounded-lg border border-border bg-surface-overlay px-3 py-2 text-sm shadow-md"
            style={tooltipOnLeft ? { right: width - x(active.day) + 12 } : { left: x(active.day) + 12 }}
          >
            <div className="text-muted">{formatLongDate(active.key)}</div>
            <div className="font-semibold text-foreground">Mon poids : {formatKg(active.weight)} kg</div>
            <div className="text-foreground">Prévu : {formatKg(active.planned)} kg</div>
            <div className="text-muted">{formatSignedKg(active.weight - active.planned)}</div>
          </div>
        )}
      </div>

      <details className="mt-3 text-sm">
        <summary className="cursor-pointer font-bold text-foreground">Voir les données</summary>
        <table className="mt-2 w-full">
          <thead>
            <tr className="text-muted">
              <th className="py-1 text-left font-normal">Date</th>
              <th className="py-1 text-right font-normal">Poids</th>
              <th className="py-1 text-right font-normal">Prévu</th>
            </tr>
          </thead>
          <tbody>
            {[...points].reverse().map((p) => (
              <tr key={p.key} className="border-t border-border/50">
                <td className="py-1">{formatLongDate(p.key)}</td>
                <td className="py-1 text-right tabular-nums">{formatKg(p.weight)} kg</td>
                <td className="py-1 text-right tabular-nums">{formatKg(p.planned)} kg</td>
              </tr>
            ))}
            {plan.end && (
              <tr className="border-t border-border/50 text-muted">
                <td className="py-1">{formatLongDate(plan.end.key)} (date estimée)</td>
                <td className="py-1 text-right">—</td>
                <td className="py-1 text-right tabular-nums">{formatKg(plan.end.weight)} kg</td>
              </tr>
            )}
          </tbody>
        </table>
      </details>
    </div>
  );
}
