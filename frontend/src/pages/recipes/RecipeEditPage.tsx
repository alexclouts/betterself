import { useMemo } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { RecipeRead } from "../../api/generated/recipeRead";
import { IngredientEntry } from "../../components/recipes/IngredientEntry";
import { IngredientSearch } from "../../components/recipes/IngredientSearch";
import { RecipeComposition } from "../../components/recipes/RecipeComposition";
import { RecipeNutritionCard } from "../../components/recipes/RecipeNutritionCard";
import Button from "../../components/ui/Button";
import { useIngredientFlow } from "../../hooks/useIngredientFlow";
import { useRecipe } from "../../hooks/useRecipe";
import { toNumber } from "../../lib/food";
import { suggestedQuantity } from "../../lib/units";
import { readJournalNavState } from "../../lib/journal";
import { queryKeys } from "../../lib/queryClient";
import { recipeTotals } from "../../lib/recipe";
import { recipeService } from "../../services/recipeService";
import { PageHeader } from "../../components/navigation/PageHeader";

/*
 * Page d'une recette : valeurs nutritionnelles et ingrédients. Le nom, les
 * portions et la description se modifient dans RecipeDetailsPage (« Modifier »).
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
      <PageHeader onBack={() => navigate("/recipes")} backLabel="Retour à mes recettes" />
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

  function refresh() {
    return queryClient.invalidateQueries({ queryKey: queryKeys.recipes.all });
  }

  const removeMutation = useMutation({
    mutationFn: (ingredientId: string) => recipeService.removeIngredient(recipe.id, ingredientId),
    onSuccess: refresh,
  });

  const ingredients = useMemo(() => recipe.ingredients ?? [], [recipe]);
  const excludedFoodIds = useMemo(
    () => new Set(ingredients.map((ingredient) => ingredient.food.id)),
    [ingredients],
  );

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
          onPick={(food) => showEntry(food, suggestedQuantity(food).grams)}
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
      {/* Nom, portions et description se modifient dans une page à part. */}
      <PageHeader
        onBack={() => navigate("/recipes")}
        backLabel="Retour à mes recettes"
        action={
          <button
            type="button"
            onClick={() => navigate(`/recipes/${recipe.id}/edit`)}
            aria-label={`Modifier les informations de la recette ${recipe.name}`}
            className="rounded-full px-3 py-2 text-sm font-semibold text-primary-ink hover:bg-surface-raised"
          >
            Modifier
          </button>
        }
      />

      <h1 className="break-words">{recipe.name}</h1>
      {recipe.is_archived && <p className="text-sm text-muted">Recette archivée</p>}
      {recipe.description && (
        <p className="mb-4 whitespace-pre-line">{recipe.description}</p>
      )}

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
    </main>
  );
}
