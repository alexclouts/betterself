import { useQuery } from "@tanstack/react-query";
import { queryKeys } from "../lib/queryClient";
import { recipeService } from "../services/recipeService";

/*
 * Une recette avec ses ingrédients et ses valeurs nutritionnelles.
 * Rechargée après chaque modification grâce à l'invalidation de queryKeys.recipes.all.
 */
export function useRecipe(recipeId: string | undefined) {
  const query = useQuery({
    queryKey: queryKeys.recipes.detail(recipeId ?? ""),
    queryFn: () => recipeService.getRecipe(recipeId!),
    enabled: Boolean(recipeId),
  });

  return {
    recipe: query.data ?? null,
    isLoading: query.isPending,
    error: query.error?.message ?? null,
  };
}
