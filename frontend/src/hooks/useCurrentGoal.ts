import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "../lib/queryClient";
import { goalService } from "../services/goalService";

// Objectif nutritionnel actif de l'utilisateur (null s'il n'en a pas).
export function useCurrentGoal() {
  const query = useQuery({
    queryKey: queryKeys.currentGoal,
    queryFn: () => goalService.getCurrentGoal(),
  });

  return {
    goal: query.data ?? null,
    isLoading: query.isPending,
    error: query.error?.message ?? null,
  };
}
