import { useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { RecipeCreate } from "../../api/generated/recipeCreate";
import { IngredientEntry } from "../../components/recipes/IngredientEntry";
import { IngredientSearch } from "../../components/recipes/IngredientSearch";
import { RecipeComposition } from "../../components/recipes/RecipeComposition";
import { RecipeDetailsFields } from "../../components/recipes/RecipeDetailsFields";
import { RecipeNutritionCard } from "../../components/recipes/RecipeNutritionCard";
import Button from "../../components/ui/Button";
import { useIngredientFlow } from "../../hooks/useIngredientFlow";
import { computeNutrientsForQuantity, getDefaultQuantityG } from "../../lib/food";
import { readJournalNavState } from "../../lib/journal";
import { queryKeys } from "../../lib/queryClient";
import {
  areDetailsValid,
  parseDecimal,
  sumNutrients,
  type PickedFood,
  type RecipeDetailsValues,
} from "../../lib/recipe";
import { recipeService } from "../../services/recipeService";

// Ingrédient du brouillon, pas encore enregistré.
type DraftIngredient = {
  food: PickedFood;
  quantityG: number;
};

/*
 * Création d'une recette avec ses ingrédients. Rien n'est enregistré avant
 * « Créer la recette »; le poids total est la somme des ingrédients.
 */
export function RecipeNewPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const location = useLocation();
  // Repas et journée choisis depuis le journal, relayés pour l'ajout de la recette au journal.
  const journalNavState = readJournalNavState(location.state);
  const { view, showRecipe, showSearch, showEntry } = useIngredientFlow();

  const [details, setDetails] = useState<RecipeDetailsValues>({
    name: "",
    description: "",
    servings: "1",
  });
  const [ingredients, setIngredients] = useState<DraftIngredient[]>([]);

  const excludedFoodIds = useMemo(
    () => new Set(ingredients.map((ingredient) => ingredient.food.id)),
    [ingredients],
  );
  const ingredientNutrients = ingredients.map((ingredient) =>
    computeNutrientsForQuantity(ingredient.food, ingredient.quantityG),
  );
  const totalWeightG = ingredients.reduce((total, ingredient) => total + ingredient.quantityG, 0);

  const createMutation = useMutation({
    mutationFn: (payload: RecipeCreate) => recipeService.createRecipe(payload),
    onSuccess: (recipe) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.recipes.all });
      queryClient.setQueryData(queryKeys.recipes.detail(recipe.id), recipe);
      navigate(`/recipes/${recipe.id}`, { replace: true, state: journalNavState });
    },
  });

  const canSubmit = areDetailsValid(details) && ingredients.length > 0 && !createMutation.isPending;

  // Ajoute l'ingrédient, ou remplace la quantité s'il est déjà dans le brouillon.
  function saveIngredient(food: PickedFood, quantityG: number) {
    setIngredients((current) =>
      current.some((ingredient) => ingredient.food.id === food.id)
        ? current.map((ingredient) =>
            ingredient.food.id === food.id ? { ...ingredient, quantityG } : ingredient,
          )
        : [...current, { food, quantityG }],
    );
    showRecipe();
  }

  function openIngredient(foodId: string) {
    const ingredient = ingredients.find((item) => item.food.id === foodId);
    if (ingredient) showEntry(ingredient.food, ingredient.quantityG, foodId);
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!canSubmit) return;
    createMutation.mutate({
      name: details.name.trim(),
      description: details.description.trim() || null,
      servings: parseDecimal(details.servings),
      ingredients: ingredients.map((ingredient) => ({
        food_id: ingredient.food.id,
        quantity_g: ingredient.quantityG,
      })),
    });
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
          onSubmit={(quantityG) => saveIngredient(view.food, quantityG)}
          // Nouvel ingrédient : retour à la recherche, comme dans le journal.
          onBack={view.key !== undefined ? showRecipe : showSearch}
        />
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      <Button type="button" variant="secondary" onClick={() => navigate(-1)} className="text-sm">
        ← Retour
      </Button>

      <h1>Créer une recette</h1>

      <form onSubmit={handleSubmit}>
        <RecipeDetailsFields values={details} onChange={setDetails} />

        <div className="mt-8">
          <RecipeComposition
            items={ingredients.map((ingredient, index) => ({
              key: ingredient.food.id,
              name: ingredient.food.name,
              quantityG: ingredient.quantityG,
              caloriesKcal: ingredientNutrients[index].calories_kcal,
            }))}
            onOpen={openIngredient}
            onRemove={(foodId) =>
              setIngredients((current) => current.filter((item) => item.food.id !== foodId))
            }
            onAdd={showSearch}
          />
        </div>

        {ingredients.length > 0 && (
          <div className="mt-8">
            <RecipeNutritionCard
              totals={sumNutrients(ingredientNutrients)}
              servings={parseDecimal(details.servings)}
              totalWeightG={totalWeightG}
            />
          </div>
        )}

        {createMutation.error && (
          <p className="mt-4 text-danger" role="alert">
            {createMutation.error.message}
          </p>
        )}

        <Button type="submit" className="mt-6 w-full font-bold" disabled={!canSubmit}>
          {createMutation.isPending ? "Création…" : "Créer la recette"}
        </Button>
        {ingredients.length === 0 && (
          <p className="mt-2 text-center text-sm text-muted">Ajoutez au moins un ingrédient.</p>
        )}
      </form>
    </main>
  );
}
