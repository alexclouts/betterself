import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "../lib/queryClient";
import { recipeService } from "../services/recipeService";

/*
 * Recettes de l'utilisateur, de la plus récente à la plus ancienne.
 * Rechargées après chaque modification grâce à l'invalidation de queryKeys.recipes.all.
 */
export function useRecipes(includeArchived = false) {
  const query = useQuery({
    queryKey: queryKeys.recipes.list(includeArchived),
    queryFn: () => recipeService.listRecipes(includeArchived),
  });

  return {
    recipes: query.data ?? [],
    isLoading: query.isPending,
    error: query.error?.message ?? null,
  };
}
