// src/lib/journal.ts
import type { MealType } from "../api/generated/mealType";
import { parseDateKey, todayKey } from "./date";
import { isMealType } from "./food";

/*
 * Gestion de l'état de navigation transmis entre les pages du parcours d'ajout
 * (journal → recherche → [création] → ajout), via location.state (pas un contexte React).
 * 
 * Un state de navigation conserve les données à travers les différentes pages du parcours d'ajout.
 */

export type JournalNavState = {
  mealType?: MealType;
  date?: string; // "YYYY-MM-DD"
};

// Lit l'état de navigation du journal depuis location.state, en ignorant les valeurs invalides.
export function readJournalNavState(state: unknown): JournalNavState {
  if (!state || typeof state !== "object") return {};
  const { mealType, date } = state as Record<string, unknown>;

  return {
    mealType: isMealType(mealType) ? mealType : undefined,
    date: typeof date === "string" && parseDateKey(date) ? date : undefined,
  };
}

// URL du journal pour une journée (sans paramètre pour aujourd'hui).
export function journalUrl(date?: string): string {
  return !date || date === todayKey() ? "/journal" : `/journal?date=${date}`;
}
