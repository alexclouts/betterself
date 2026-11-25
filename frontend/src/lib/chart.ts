import { parseDateKey } from "./date";

/*
 * Utilitaires partagés par les graphiques de poids (accueil et profil).
 */

export const DAY_MS = 86_400_000;
// Pas « ronds » possibles pour l'axe des kilogrammes.
const NICE_STEPS = [0.5, 1, 2, 5, 10, 20, 50];

// Clé "YYYY-MM-DD" → nombre de jours, pour un axe du temps proportionnel ; null si invalide.
export function dayNumber(key: string): number | null {
  const date = parseDateKey(key);
  return date ? date.getTime() / DAY_MS : null;
}

export function formatKg(value: number): string {
  return value.toLocaleString("fr-CA", { maximumFractionDigits: 1 });
}

// Domaine et graduations de l'axe des poids, avec une marge pour que la courbe respire.
export function weightAxis(weights: number[]) {
  const min = Math.min(...weights);
  const max = Math.max(...weights);
  const pad = Math.max(0.5, (max - min) * 0.1);
  const range = max - min + pad * 2;
  const step = NICE_STEPS.find((s) => range / s <= 4) ?? 100;

  const lo = Math.floor((min - pad) / step) * step;
  const hi = Math.ceil((max + pad) / step) * step;
  const ticks: number[] = [];
  for (let value = lo; value <= hi + step / 2; value += step) ticks.push(value);
  return { lo, hi, ticks };
}

// Indice de la position (en pixels) la plus proche du pointeur.
export function nearestIndex(positions: number[], px: number): number {
  let nearest = 0;
  positions.forEach((position, i) => {
    if (Math.abs(position - px) < Math.abs(positions[nearest] - px)) nearest = i;
  });
  return nearest;
}
