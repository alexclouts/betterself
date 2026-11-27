import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { RecipeRead } from "../../api/generated/recipeRead";
import { useRecipes } from "../../hooks/useRecipes";
import { formatNutrient } from "../../lib/food";
import { queryKeys } from "../../lib/queryClient";
import { formatCount, perServing, recipeTotals } from "../../lib/recipe";
import { recipeService } from "../../services/recipeService";
import Button from "../../components/ui/Button";

/*
 * Recettes de l'utilisateur. Une recette archivée disparaît des choix courants
 * sans toucher aux entrées du journal qui y font référence ; elle reste
 * visible ici en cochant « Afficher les recettes archivées ».
 */
export function RecipesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showArchived, setShowArchived] = useState(false);
  const { recipes, isLoading, error: loadError } = useRecipes(showArchived);

  const archiveMutation = useMutation({
    mutationFn: ({ id, isArchived }: { id: string; isArchived: boolean }) =>
      recipeService.setArchived(id, isArchived),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.recipes.all });
    },
  });

  const pendingId = archiveMutation.isPending ? archiveMutation.variables.id : null;
  const error = loadError ?? archiveMutation.error?.message ?? null;

  function toggleArchive(recipe: RecipeRead) {
    archiveMutation.mutate({ id: recipe.id, isArchived: !recipe.is_archived });
  }

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6 text-center">
      <h1>Mes recettes</h1>

      <label className="flex items-center justify-center gap-2 text-sm text-muted">
        <input
          type="checkbox"
          checked={showArchived}
          onChange={(event) => setShowArchived(event.target.checked)}
        />
        Afficher les recettes archivées
      </label>

      {error && (
        <p className="mt-4 text-danger" role="alert">
          {error}
        </p>
      )}

      {isLoading ? (
        <p className="mt-6">Chargement de vos recettes…</p>
      ) : recipes.length === 0 ? (
        <p className="mt-6">
          {showArchived
            ? "Aucune recette enregistrée pour l’instant."
            : "Aucune recette active. Créez-en une avec le bouton « Créer une recette »."}
        </p>
      ) : (
        <ul className="mt-6 divide-y divide-border text-left">
          {recipes.map((recipe) => {
            const { calories_kcal: calories } = perServing(recipeTotals(recipe), recipe.servings);

            return (
              <li key={recipe.id} className="flex items-center gap-3 py-3">
                {/* Un clic ouvre la recette pour la consulter ou la modifier. */}
                <button
                  type="button"
                  onClick={() => navigate(`/recipes/${recipe.id}`)}
                  aria-label={`Ouvrir la recette ${recipe.name}${recipe.is_archived ? " (archivée)" : ""}`}
                  className={`flex min-w-0 flex-1 items-center justify-between gap-3 rounded-lg px-2 py-1 text-left hover:bg-surface-raised ${
                    recipe.is_archived ? "opacity-60" : ""
                  }`}
                >
                  {/* L'essentiel seulement : nom et portions à gauche, calories d'une portion à droite. */}
                  <span className="min-w-0">
                    <span className="line-clamp-2 font-medium break-words text-foreground">{recipe.name}</span>
                    <span className="block text-sm text-muted">
                      {recipe.is_archived ? "Archivée" : formatCount(recipe.servings, "portion", "portions")}
                    </span>
                  </span>
                  <span className="shrink-0 text-right">
                    <strong className="block text-foreground">{formatNutrient(calories, 0)} kcal</strong>
                    <span className="block text-xs text-muted">par portion</span>
                  </span>
                </button>

                {/* Icône plutôt que texte, pour alléger la rangée :
                    archiver en couleur secondaire, réactiver en couleur primaire. */}
                <button
                  type="button"
                  onClick={() => toggleArchive(recipe)}
                  disabled={pendingId === recipe.id}
                  aria-label={`${recipe.is_archived ? "Réactiver" : "Archiver"} la recette ${recipe.name}`}
                  title={recipe.is_archived ? "Réactiver" : "Archiver"}
                  className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full hover:bg-surface-raised disabled:opacity-30 ${
                    recipe.is_archived ? "text-primary-ink" : "text-secondary-ink"
                  }`}
                >
                  <svg
                    viewBox="0 0 24 24"
                    className="h-5 w-5"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    {recipe.is_archived ? (
                      // Flèche circulaire : réactiver.
                      <path d="M3 12a9 9 0 1 0 3-6.7L3 8M3 3v5h5" />
                    ) : (
                      // Boîte d'archives.
                      <>
                        <rect x="3" y="4" width="18" height="4" rx="1" />
                        <path d="M5 8v11a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8M10 12h4" />
                      </>
                    )}
                  </svg>
                </button>
              </li>
            );
          })}
        </ul>
      )}

      {!isLoading && (
        <Button className="mt-6 w-full font-bold" onClick={() => navigate("/recipes/new")}>
          Créer une recette
        </Button>
      )}
    </main>
  );
}
