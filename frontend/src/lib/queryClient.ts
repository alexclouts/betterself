// src/lib/queryClient.ts
import { QueryClient } from "@tanstack/react-query";

/*
 * Client TanStack Query partagé par toute l'application.
 * Exporté comme module (et non créé dans un composant) pour pouvoir
 * vider le cache hors de React, par exemple à la déconnexion.
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Les données restent « fraîches » 30 s : pas de rechargement en naviguant entre pages.
      staleTime: 30_000,
      // Une seule nouvelle tentative : les erreurs de l'API (400, 404…) ne se corrigent pas en réessayant.
      retry: 1,
    },
  },
});

/*
 * Clés du cache, centralisées pour éviter les fautes de frappe
 * et pour invalider des groupes de requêtes d'un coup.
 */
export const queryKeys = {
  journal: {
    // Préfixe commun : invalider cette clé rafraîchit toutes les journées.
    all: ["journal"] as const,
    day: (dayKey: string) => ["journal", "day", dayKey] as const,
  },
  foods: {
    // Préfixe commun : invalider cette clé rafraîchit toutes les recherches.
    all: ["foods"] as const,
    search: (term: string) => ["foods", "search", term] as const,
  },
  recipes: {
    // Préfixe commun : invalider cette clé rafraîchit les listes et les détails.
    all: ["recipes"] as const,
    list: (includeArchived: boolean) => ["recipes", "list", { includeArchived }] as const,
    detail: (recipeId: string) => ["recipes", "detail", recipeId] as const,
  },
  currentTarget: ["nutrition-goal", "current-target"] as const,
  currentGoal: ["nutrition-goal", "current"] as const,
  profile: ["users", "me", "profile"] as const,
  currentUser: ["users", "me"] as const,
  measurements: {
    // Préfixe commun : invalider cette clé rafraîchit toutes les listes de mesures.
    all: ["measurements"] as const,
    list: ["measurements", "list"] as const,
  },
};
