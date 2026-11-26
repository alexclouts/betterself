import { useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { RecipeRead } from "../../api/generated/recipeRead";
import type { RecipeUpdate } from "../../api/generated/recipeUpdate";
import { IngredientEntry } from "../../components/recipes/IngredientEntry";
import { IngredientSearch } from "../../components/recipes/IngredientSearch";
import { RecipeComposition } from "../../components/recipes/RecipeComposition";
import { RecipeDetailsFields } from "../../components/recipes/RecipeDetailsFields";
import { RecipeNutritionCard } from "../../components/recipes/RecipeNutritionCard";
import Button from "../../components/ui/Button";
import { useIngredientFlow } from "../../hooks/useIngredientFlow";
import { useRecipe } from "../../hooks/useRecipe";
import { getDefaultQuantityG, toNumber } from "../../lib/food";
import { readJournalNavState } from "../../lib/journal";
import { queryKeys } from "../../lib/queryClient";
import {
  areDetailsValid,
  parseDecimal,
  recipeTotals,
  type RecipeDetailsValues,
} from "../../lib/recipe";
import { recipeService } from "../../services/recipeService";
import { useToastStore } from "../../stores/toastStore";

/*
 * Page d'une recette : valeurs nutritionnelles, ingrédients et détails.
 * Chaque changement d'ingrédient est enregistré aussitôt et le poids total
 * recalculé par l'API.
 */
export function RecipeEditPage() {
  const navigate = useNavigate();
  const { recipeId } = useParams<{ recipeId: string }>();
  const { recipe, isLoading, error: loadError } = useRecipe(recipeId);

  if (recipe) {
    // Formulaire réinitialisé si l'on passe à une autre recette.
    return <RecipeEditor key={recipe.id} recipe={recipe} />;
  }

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      <Button type="button" variant="secondary" onClick={() => navigate("/recipes")} className="text-sm">
        ← Mes recettes
      </Button>
      {isLoading ? (
        <p className="mt-6">Chargement de la recette…</p>
      ) : (
        <p className="mt-6 text-danger" role="alert">
          {loadError ?? "Recette introuvable."}
        </p>
      )}
    </main>
  );
}

function RecipeEditor({ recipe }: { recipe: RecipeRead }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const location = useLocation();
  // Repas et journée choisis dans le journal, si l'on arrive de « Créer une recette ».
  const journalNavState = readJournalNavState(location.state);
  const { view, showRecipe, showSearch, showEntry } = useIngredientFlow();
  const [details, setDetails] = useState<RecipeDetailsValues>({
    name: recipe.name,
    description: recipe.description ?? "",
    servings: String(recipe.servings),
  });

  function refresh() {
    return queryClient.invalidateQueries({ queryKey: queryKeys.recipes.all });
  }

  const updateMutation = useMutation({
    mutationFn: (payload: RecipeUpdate) => recipeService.updateRecipe(recipe.id, payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(queryKeys.recipes.detail(updated.id), updated);
      void refresh();
      useToastStore.getState().showToast("La recette a été enregistrée.");
    },
  });

  const removeMutation = useMutation({
    mutationFn: (ingredientId: string) => recipeService.removeIngredient(recipe.id, ingredientId),
    onSuccess: refresh,
  });

  const ingredients = useMemo(() => recipe.ingredients ?? [], [recipe]);
  const excludedFoodIds = useMemo(
    () => new Set(ingredients.map((ingredient) => ingredient.food.id)),
    [ingredients],
  );

  const isDirty =
    details.name.trim() !== recipe.name ||
    (details.description.trim() || null) !== recipe.description ||
    parseDecimal(details.servings) !== recipe.servings;
  const canSave = areDetailsValid(details) && isDirty && !updateMutation.isPending;

  function handleSave(event: React.FormEvent) {
    event.preventDefault();
    if (!canSave) return;
    updateMutation.mutate({
      name: details.name.trim(),
      description: details.description.trim() || null,
      servings: parseDecimal(details.servings),
    });
  }

  function openIngredient(ingredientId: string) {
    const ingredient = ingredients.find((item) => item.id === ingredientId);
    // Un ingrédient enregistré ne connaît pas la portion du fabricant.
    if (ingredient) {
      showEntry({ ...ingredient.food, serving_g: null }, toNumber(ingredient.quantity_g), ingredient.id);
    }
  }

  function removeIngredient(ingredientId: string) {
    const ingredient = ingredients.find((item) => item.id === ingredientId);
    if (!ingredient || !window.confirm(`Retirer ${ingredient.food.name} de la recette ?`)) return;
    removeMutation.mutate(ingredientId);
  }

  // Ajoute un nouvel ingrédient ou modifie la quantité d'un ingrédient existant.
  async function saveIngredient(foodId: string, quantityG: number, ingredientId?: string) {
    if (ingredientId) {
      await recipeService.updateIngredient(recipe.id, ingredientId, quantityG);
    } else {
      await recipeService.addIngredient(recipe.id, foodId, quantityG);
    }
    await refresh();
    showRecipe();
  }

  if (view.kind === "search") {
    return (
      <main className="mx-auto w-full max-w-md px-4 py-6">
        <IngredientSearch
          excludedFoodIds={excludedFoodIds}
          onPick={(food) => showEntry(food, getDefaultQuantityG(food))}
          onBack={showRecipe}
        />
      </main>
    );
  }

  if (view.kind === "entry") {
    return (
      <main className="mx-auto w-full max-w-md px-4 py-6">
        <IngredientEntry
          food={view.food}
          initialQuantityG={view.quantityG}
          isEditing={view.key !== undefined}
          onSubmit={(quantityG) => saveIngredient(view.food.id, quantityG, view.key)}
          // Nouvel ingrédient : retour à la recherche, comme dans le journal.
          onBack={view.key !== undefined ? showRecipe : showSearch}
        />
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      <Button type="button" variant="secondary" onClick={() => navigate("/recipes")} className="text-sm">
        ← Mes recettes
      </Button>

      <h1 className="break-words">{recipe.name}</h1>
      {recipe.is_archived && <p className="text-sm text-muted">Recette archivée</p>}

      <RecipeNutritionCard
        totals={recipeTotals(recipe)}
        servings={recipe.servings}
        totalWeightG={toNumber(recipe.total_weight_g)}
      />

      {/* Une recette archivée n'est plus proposée pour le journal. */}
      {!recipe.is_archived && (
        <Button
          type="button"
          onClick={() => navigate(`/journal/recipe/${recipe.id}`, { state: journalNavState })}
          className="mt-4 w-full font-bold"
        >
          Ajouter au journal
        </Button>
      )}

      <div className="mt-8">
        <RecipeComposition
          items={ingredients.map((ingredient) => ({
            key: ingredient.id,
            name: ingredient.food.name,
            quantityG: toNumber(ingredient.quantity_g),
            caloriesKcal: toNumber(ingredient.nutrition.calories_kcal),
          }))}
          onOpen={openIngredient}
          onRemove={removeIngredient}
          onAdd={showSearch}
          canRemove={ingredients.length > 1}
          removingKey={removeMutation.isPending ? removeMutation.variables : null}
        />
        {removeMutation.error && (
          <p className="mt-2 text-danger" role="alert">
            {removeMutation.error.message}
          </p>
        )}
      </div>

      <section className="mt-10" aria-labelledby="details-heading">
        <h2 id="details-heading" className="mt-0 mb-2 text-left text-xl">
          Détails
        </h2>
        <form onSubmit={handleSave}>
          <RecipeDetailsFields values={details} onChange={setDetails} />

          {updateMutation.error && (
            <p className="mt-4 text-danger" role="alert">
              {updateMutation.error.message}
            </p>
          )}

          <Button type="submit" className="mt-4 w-full font-bold" disabled={!canSave}>
            {updateMutation.isPending ? "Enregistrement…" : "Enregistrer"}
          </Button>
        </form>
      </section>
    </main>
  );
}
