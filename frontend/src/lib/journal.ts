// src/lib/journal.ts
import type { MealType } from "../api/generated/mealType";
import { parseDateKey, todayKey } from "./date";
import { isMealType } from "./food";

/*
 * Contexte transmis entre les pages du parcours d'ajout
 * (journal → recherche → [création] → ajout), via l'état de navigation.
 */
export type JournalContext = {
  mealType?: MealType;
  date?: string; // "YYYY-MM-DD"
};

// Lit le contexte du journal depuis location.state, en ignorant les valeurs invalides.
export function readJournalContext(state: unknown): JournalContext {
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
