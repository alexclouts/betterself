// src/lib/date.ts

/*
 * Contient des utilitaires de dates « locales » (fuseau de l'appareil) pour le journal.
 * Une journée est identifiée par une clé "YYYY-MM-DD" dans le fuseau local.
 * 
 * Fournit des fonctions pour convertir, formater et manipuler les dates locales.
 * Inclut également des fonctions pour obtenir les bornes d'une journée et le moment d'une consommation.
 */

// Retourne la clé "YYYY-MM-DD" d'une date dans le fuseau local.
export function toDateKey(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

// Clé du jour actuel.
export function todayKey(): string {
  return toDateKey(new Date());
}

// Convertit une clé "YYYY-MM-DD" en date locale à minuit ; null si invalide.
export function parseDateKey(key: string | null | undefined): Date | null {
  if (!key || !/^\d{4}-\d{2}-\d{2}$/.test(key)) return null;
  const [year, month, day] = key.split("-").map(Number);
  const date = new Date(year, month - 1, day);
  return toDateKey(date) === key ? date : null;
}

// Ajoute (ou retire) des jours à une clé de date.
export function addDays(key: string, days: number): string {
  const date = parseDateKey(key) ?? new Date();
  date.setDate(date.getDate() + days);
  return toDateKey(date);
}

/*
 * Bornes de la journée locale, en ISO UTC, pour filtrer les consommations.
 * Le backend stocke consumed_at en UTC : envoyer des dates en UTC (suffixe Z)
 * garantit une comparaison cohérente.
 */
export function getDayBoundsIso(key: string): { start: string; end: string } {
  const start = parseDateKey(key) ?? new Date();
  const end = new Date(start);
  end.setDate(end.getDate() + 1);
  end.setMilliseconds(end.getMilliseconds() - 1);
  return { start: start.toISOString(), end: end.toISOString() };
}

// Moment à enregistrer pour une consommation ajoutée à une journée donnée :
// maintenant si c'est aujourd'hui, sinon midi (heure locale) ce jour-là.
export function consumedAtForDay(key: string): string | undefined {
  if (key === todayKey()) return undefined;
  const date = parseDateKey(key);
  if (!date) return undefined;
  date.setHours(12, 0, 0, 0);
  return date.toISOString();
}

// Libellé lisible d'une journée : « Aujourd'hui », « Hier », « Demain » ou la date complète.
export function formatDayLabel(key: string): string {
  if (key === todayKey()) return "Aujourd’hui";
  if (key === addDays(todayKey(), -1)) return "Hier";
  if (key === addDays(todayKey(), 1)) return "Demain";

  const date = parseDateKey(key);
  if (!date) return key;
  const label = date.toLocaleDateString("fr-CA", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });
  return label.charAt(0).toUpperCase() + label.slice(1);
}
