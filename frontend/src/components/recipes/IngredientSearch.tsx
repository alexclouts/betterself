import { useState } from "react";
import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { FoodSearchResult } from "../../api/generated/foodSearchResult";
import { FoodResultItem } from "../journal/FoodResultItem";
import Button from "../ui/Button";
import Input from "../ui/Input";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import { queryKeys } from "../../lib/queryClient";
import type { PickedFood } from "../../lib/recipe";
import { foodService } from "../../services/foodService";

// Mêmes réglages que la recherche du journal.
const MIN_SEARCH_LENGTH = 2;
const SEARCH_DELAY_MS = 300;
const VISIBLE_RESULTS = 10;
const HISTORY_RESULTS = 3;

type IngredientSearchProps = {
  // Aliments déjà dans la recette : l'API refuse les doublons.
  excludedFoodIds: Set<string>;
  onPick: (food: PickedFood) => void;
  onBack: () => void;
};

/*
 * Recherche d'un ingrédient, sur le modèle de « Ajouter un aliment » du journal :
 * historique sans recherche, puis aliments créés et catalogue.
 */
export function IngredientSearch({ excludedFoodIds, onPick, onBack }: IngredientSearchProps) {
  const queryClient = useQueryClient();
  const [query, setQuery] = useState("");
  const [isExpanded, setIsExpanded] = useState(false);

  const searchTerm = useDebouncedValue(query.trim(), SEARCH_DELAY_MS);
  const isSearching = searchTerm.length >= MIN_SEARCH_LENGTH;
  const apiTerm = isSearching ? searchTerm : "";

  const searchQuery = useQuery({
    queryKey: queryKeys.foods.search(apiTerm),
    queryFn: ({ signal }) => foodService.searchFoods(apiTerm, signal),
    placeholderData: keepPreviousData,
    staleTime: 5 * 60_000,
  });

  // Un produit du catalogue est copié dans les aliments seulement lorsqu'il est choisi.
  const importMutation = useMutation({
    mutationFn: (code: string) => foodService.importCatalogProduct(code),
    onSuccess: (food) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.foods.all });
      onPick(food);
    },
  });

  const results = (searchQuery.data?.results ?? []).filter(
    (food) => !food.food_id || !excludedFoodIds.has(food.food_id),
  );
  const visibleResults = !isSearching
    ? results.slice(0, HISTORY_RESULTS)
    : isExpanded
      ? results
      : results.slice(0, VISIBLE_RESULTS);
  const hiddenCount = isSearching ? results.length - visibleResults.length : 0;
  const hasNoResults =
    isSearching && searchQuery.isSuccess && !searchQuery.isPlaceholderData && results.length === 0;
  const error = searchQuery.error?.message ?? importMutation.error?.message ?? null;

  function handleSelect(food: FoodSearchResult) {
    if (food.food_id) {
      onPick({ ...food, id: food.food_id });
    } else if (food.catalog_code) {
      importMutation.mutate(food.catalog_code);
    }
  }

  return (
    <>
      <Button type="button" variant="secondary" onClick={onBack} className="text-sm">
        ← Retour à la recette
      </Button>

      <h1>Ajouter un ingrédient</h1>

      <Input
        type="search"
        value={query}
        onChange={(event) => {
          setQuery(event.target.value);
          setIsExpanded(false);
        }}
        placeholder="Rechercher un aliment"
        className="mt-4 w-full border px-4 py-3"
        autoFocus
      />

      {isSearching && searchQuery.isFetching && <p className="mt-4">Recherche…</p>}

      {error && (
        <p className="mt-4 text-danger" role="alert">
          {error}
        </p>
      )}

      {!isSearching && visibleResults.length > 0 && (
        <h2 id="ingredient-history-heading" className="mt-6 mb-2 text-left text-xl">
          Historique
        </h2>
      )}

      {visibleResults.length > 0 && (
        <ul
          {...(isSearching
            ? { "aria-label": "Résultats de la recherche" }
            : { "aria-labelledby": "ingredient-history-heading" })}
          className={`${isSearching ? "mt-6" : ""} divide-y divide-border overflow-hidden bg-surface`}
        >
          {visibleResults.map((food) => (
            <FoodResultItem
              key={food.food_id ?? food.catalog_code}
              food={food}
              onSelect={() => handleSelect(food)}
              disabled={importMutation.isPending}
              isPending={importMutation.isPending && importMutation.variables === food.catalog_code}
            />
          ))}
        </ul>
      )}

      {hiddenCount > 0 && (
        <Button
          type="button"
          variant="ghost"
          onClick={() => setIsExpanded(true)}
          className="mt-2 w-full text-sm"
        >
          Afficher {hiddenCount} résultat{hiddenCount > 1 ? "s" : ""} de plus
        </Button>
      )}

      {hasNoResults && <p className="mt-4">Aucun aliment trouvé pour « {searchTerm} ».</p>}

      {visibleResults.some((food) => food.source === "open_food_facts") && (
        <p className="mt-12 text-xs">
          Contient des données d’
          <a href="https://world.openfoodfacts.org" target="_blank" rel="noreferrer" className="underline">
            Open Food Facts
          </a>
          , offertes sous la licence{" "}
          <a href="https://opendatacommons.org/licenses/odbl/1-0/" target="_blank" rel="noreferrer" className="underline">
            Open Database License (ODbL)
          </a>
          .
        </p>
      )}
    </>
  );
}
