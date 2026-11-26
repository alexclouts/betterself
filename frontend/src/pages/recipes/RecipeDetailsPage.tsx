import { useRef, useState } from "react";
import { useBeforeUnload, useBlocker, useLocation, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { RecipeRead } from "../../api/generated/recipeRead";
import type { RecipeUpdate } from "../../api/generated/recipeUpdate";
import { RecipeDetailsFields } from "../../components/recipes/RecipeDetailsFields";
import Button from "../../components/ui/Button";
import { ConfirmDialog } from "../../components/ui/ConfirmDialog";
import { useRecipe } from "../../hooks/useRecipe";
import { queryKeys } from "../../lib/queryClient";
import { areDetailsValid, parseDecimal, type RecipeDetailsValues } from "../../lib/recipe";
import { recipeService } from "../../services/recipeService";
import { useToastStore } from "../../stores/toastStore";
import { PageHeader } from "../../components/navigation/PageHeader";

/*
 * Modification du nom, du nombre de portions et de la description d'une recette
 * (/recipes/:recipeId/edit). Les ingrédients se modifient sur la page de la recette.
 */
export function RecipeDetailsPage() {
  const navigate = useNavigate();
  const { recipeId } = useParams<{ recipeId: string }>();
  const { recipe, isLoading, error } = useRecipe(recipeId);

  if (recipe) {
    return <RecipeDetailsForm key={recipe.id} recipe={recipe} />;
  }

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      {isLoading ? (
        <p>Chargement de la recette…</p>
      ) : (
        <>
          <p className="text-danger" role="alert">
            {error ?? "Recette introuvable."}
          </p>
          <Button variant="ghost" className="mt-4" onClick={() => navigate("/recipes")}>
            Retour à mes recettes
          </Button>
        </>
      )}
    </main>
  );
}

function RecipeDetailsForm({ recipe }: { recipe: RecipeRead }) {
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();
  const [details, setDetails] = useState<RecipeDetailsValues>({
    name: recipe.name,
    description: recipe.description ?? "",
    servings: String(recipe.servings),
  });

  const isDirty =
    details.name.trim() !== recipe.name ||
    (details.description.trim() || null) !== recipe.description ||
    parseDecimal(details.servings) !== recipe.servings;

  // Retour à la page de la recette. Ouverte directement (sans historique dans
  // l'app), la page est remplacée par celle de la recette.
  function goBack() {
    if (location.key !== "default") navigate(-1);
    else navigate(`/recipes/${recipe.id}`, { replace: true });
  }

  // Une fois enregistré, le retour ne doit pas demander de confirmation.
  const isSavedRef = useRef(false);
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      isDirty && !isSavedRef.current && currentLocation.pathname !== nextLocation.pathname,
  );

  // Recharger la page, fermer l'onglet ou quitter le site : avertissement du navigateur.
  useBeforeUnload((event) => {
    if (isDirty && !isSavedRef.current) event.preventDefault();
  });

  const updateMutation = useMutation({
    mutationFn: (payload: RecipeUpdate) => recipeService.updateRecipe(recipe.id, payload),
    onSuccess: (updated) => {
      isSavedRef.current = true;
      queryClient.setQueryData(queryKeys.recipes.detail(updated.id), updated);
      void queryClient.invalidateQueries({ queryKey: queryKeys.recipes.all });
      useToastStore.getState().showToast("La recette a été enregistrée.");
      goBack();
    },
  });

  const canSave = areDetailsValid(details) && isDirty && !updateMutation.isPending;

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!canSave) return;
    updateMutation.mutate({
      name: details.name.trim(),
      description: details.description.trim() || null,
      servings: parseDecimal(details.servings),
    });
  }

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      <PageHeader onBack={goBack} backLabel="Retour à la recette" />

      <h1 className="break-words">Modifier la recette</h1>

      <form onSubmit={handleSubmit}>
        <fieldset disabled={updateMutation.isPending} className="min-w-0">
          <RecipeDetailsFields values={details} onChange={setDetails} />
        </fieldset>

        {updateMutation.error && (
          <p className="mt-4 text-danger" role="alert">
            {updateMutation.error.message}
          </p>
        )}

        <Button type="submit" className="mt-6 w-full font-bold" disabled={!canSave}>
          {updateMutation.isPending ? "Enregistrement…" : "Enregistrer"}
        </Button>
      </form>

      <ConfirmDialog
        open={blocker.state === "blocked"}
        title="Quitter sans enregistrer ?"
        message="Vos modifications de la recette seront perdues."
        confirmLabel="Quitter"
        cancelLabel="Continuer"
        onConfirm={() => blocker.proceed?.()}
        onCancel={() => blocker.reset?.()}
      />
    </main>
  );
}
