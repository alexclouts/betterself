import { useEffect, useMemo, useState } from "react";
import type { FoodConsumptionRead } from "../api/generated/foodConsumptionRead";
import type { GoalTargetRead } from "../api/generated/goalTargetRead";
import { sumNutrients } from "../lib/food";
import { journalService } from "../services/journalService";

/*
 * Charge les entrées du journal d'une journée locale ("YYYY-MM-DD")
 * ainsi que la cible nutritionnelle active, et calcule les totaux.
 */
export function useJournalDay(dayKey: string) {
  const [entries, setEntries] = useState<FoodConsumptionRead[]>([]);
  const [target, setTarget] = useState<GoalTargetRead | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Entrées de la journée : rechargées à chaque changement de journée.
  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    journalService
      .getEntriesForDay(dayKey)
      .then((result) => {
        if (!cancelled) setEntries(result);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Impossible de charger le journal.");
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [dayKey]);

  // La cible ne dépend pas de la journée : chargée une seule fois.
  useEffect(() => {
    let cancelled = false;
    journalService
      .getCurrentTarget()
      .then((result) => {
        if (!cancelled) setTarget(result);
      })
      .catch(() => {
        // Sans cible, le résumé affiche seulement les totaux consommés.
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const totals = useMemo(() => sumNutrients(entries), [entries]);

  return { entries, setEntries, totals, target, isLoading, error, setError };
}
