import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { sumNutrients } from "../lib/food";
import { queryKeys } from "../lib/queryClient";
import { journalService } from "../services/journalService";

/*
 * Un hook est une fonction React qui encapsule la logique de gestion de
 * l'état du journal pour une journée donnée.
 *
 * Fournit un résumé des totaux consommés et de la cible nutritionnelle.
 * Les données sont chargées et mises en cache par TanStack Query :
 * elles sont partagées entre les pages (accueil, journal) et rechargées
 * automatiquement quand une modification invalide le cache du journal.
 */
export function useJournalDay(dayKey: string) {
  // Entrées de la journée : une entrée de cache par journée.
  // TanStack Query ignore lui-même les réponses d'une journée qui n'est plus affichée.
  const entriesQuery = useQuery({
    queryKey: queryKeys.journal.day(dayKey),
    queryFn: () => journalService.getEntriesForDay(dayKey),
  });

  // Cible active : ne dépend pas de la journée, donc partagée par toutes les journées.
  // Sans cible (ou en cas d'erreur), le résumé affiche seulement les totaux consommés.
  const targetQuery = useQuery({
    queryKey: queryKeys.currentTarget,
    queryFn: () => journalService.getCurrentTarget(),
  });

  const entries = useMemo(() => entriesQuery.data ?? [], [entriesQuery.data]);
  const totals = useMemo(() => sumNutrients(entries), [entries]);

  return {
    entries,
    totals,
    target: targetQuery.data ?? null,
    isLoading: entriesQuery.isPending,
    error: entriesQuery.error?.message ?? null,
  };
}
