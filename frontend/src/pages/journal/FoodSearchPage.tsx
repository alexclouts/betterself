import { useEffect, useState } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { FoodSearchResult } from "../../api/generated/foodSearchResult";
import { foodService } from "../../services/foodService";
import { readJournalNavState } from "../../lib/journal";
import { queryKeys } from "../../lib/queryClient";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import { FoodResultItem } from "../../components/journal/FoodResultItem";
import { RecipeResultItem } from "../../components/journal/RecipeResultItem";
import { useRecipes } from "../../hooks/useRecipes";
import { normalizeSearchText } from "../../lib/recipe";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";

// Nombre minimal de caractères avant de lancer une recherche.
const MIN_SEARCH_LENGTH = 2;

// Délai sans frappe avant de lancer la recherche.
const SEARCH_DELAY_MS = 300;

// Nombre de résultats affichés avant « Afficher plus ».
const VISIBLE_RESULTS = 3;

// Nombre d'aliments de l'historique proposés tant que rien n'est recherché.
const HISTORY_RESULTS = 3;

// Nombre de recettes proposées, avec ou sans recherche.
const RECIPE_RESULTS = 3;

export function FoodSearchPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const location = useLocation();
  // Repas et journée choisis depuis le journal, relayés jusqu'à la page d'ajout.
  const journalNavState = readJournalNavState(location.state);

  // Le terme recherché est conservé dans l'URL (?q=...) : au retour depuis
  // la page d'un aliment, la recherche et ses résultats sont retrouvés.
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(() => searchParams.get("q") ?? "");
  const searchTerm = useDebouncedValue(query.trim(), SEARCH_DELAY_MS);
  const isSearching = searchTerm.length >= MIN_SEARCH_LENGTH;
  // Tant que rien n'est recherché, l'API propose l'historique.
  const apiTerm = isSearching ? searchTerm : "";

  // Synchronise l'URL avec le terme recherché, sans ajouter d'entrée à l'historique.
  // L'état de navigation (repas, journée) est conservé.
  useEffect(() => {
    if ((searchParams.get("q") ?? "") === searchTerm) return;
    setSearchParams(searchTerm ? { q: searchTerm } : {}, {
      replace: true,
      state: location.state,
    });
  }, [searchTerm, searchParams, setSearchParams, location.state]);

  // Une entrée de cache par terme : les résultats affichés correspondent
  // toujours au terme en cours, même si une ancienne réponse arrive en retard.
  const searchQuery = useQuery({
    queryKey: queryKeys.foods.search(apiTerm),
    queryFn: ({ signal }) => foodService.searchFoods(apiTerm, signal),
    // Garde les résultats précédents affichés pendant le chargement des nouveaux.
    placeholderData: keepPreviousData,
    staleTime: 5 * 60_000,
  });

  // Un produit du catalogue est copié dans les aliments seulement lorsqu'il est choisi.
  const importMutation = useMutation({
    mutationFn: (code: string) => foodService.importCatalogProduct(code),
    onSuccess: (food) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.foods.all });
      navigate(`/journal/food/${food.id}`, { state: { ...journalNavState, food } });
    },
  });

  // Terme pour lequel tous les produits sont affichés : une nouvelle recherche replie la liste.
  const [expandedTerm, setExpandedTerm] = useState<string | null>(null);

  const results = searchQuery.data?.results ?? [];
  // Sans recherche, seuls les derniers aliments de l'historique sont proposés, sans « Afficher plus ».
  const visibleResults = !isSearching
    ? results.slice(0, HISTORY_RESULTS)
    : expandedTerm === apiTerm
      ? results
      : results.slice(0, VISIBLE_RESULTS);
  const hiddenCount = isSearching ? results.length - visibleResults.length : 0;
  const isLoading = isSearching && searchQuery.isFetching;
  const error = searchQuery.error?.message ?? null;
  const hasCurrentResults = searchQuery.isSuccess && !searchQuery.isPlaceholderData;

  // « Aucun résultat » seulement quand la réponse du terme en cours est arrivée.
  const hasNoResults = isSearching && hasCurrentResults && results.length === 0;
  const isCatalogUnavailable = hasCurrentResults && !searchQuery.data.catalog_available;

  // Recettes actives : les plus récentes sans recherche, sinon celles dont le nom correspond.
  const { recipes } = useRecipes();
  const normalizedTerm = normalizeSearchText(searchTerm);
  const visibleRecipes = (
    isSearching
      ? recipes.filter((recipe) => normalizeSearchText(recipe.name).includes(normalizedTerm))
      : recipes
  ).slice(0, RECIPE_RESULTS);

  const recipeSection = visibleRecipes.length > 0 && (
    <>
      <h2 id="recipes-heading" className="mt-6 mb-2 text-left text-xl">
        Mes recettes
      </h2>
      <ul aria-labelledby="recipes-heading" className="divide-y divide-border overflow-hidden bg-surface">
        {visibleRecipes.map((recipe) => (
          <RecipeResultItem
            key={recipe.id}
            recipe={recipe}
            onSelect={() => navigate(`/journal/recipe/${recipe.id}`, { state: journalNavState })}
          />
        ))}
      </ul>
    </>
  );

  // L'attribution est exigée dès qu'une donnée d'Open Food Facts est affichée.
  const needsAttribution = visibleResults.some((food) => food.source === "open_food_facts");

  function handleSelect(food: FoodSearchResult) {
    if (food.food_id) {
      navigate(`/journal/food/${food.food_id}`, { state: journalNavState });
    } else if (food.catalog_code) {
      importMutation.mutate(food.catalog_code);
    }
  }

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      <Button
        type="button"
        variant="secondary"
        onClick={() => navigate(-1)}
        className="text-sm text-gray-500"
      >
        ← Retour
      </Button>

      <h1>
        Ajouter un aliment
      </h1>

      <Input
        type="search"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Rechercher un aliment"
        className="mt-4 w-full border px-4 py-3"
      />

      <Button
        type="button"
        variant="ghost"
        onClick={() => navigate("/journal/scan", { state: journalNavState })}
        className="mt-2 w-full text-sm font-semibold"
      >
        Scanner un code-barres
      </Button>

      {isLoading && (
        <p className="mt-4">
          Recherche…
        </p>
      )}

      {error && (
        <p className="mt-4 text-danger">
          {error}
        </p>
      )}

      {importMutation.error && (
        <p className="mt-4 text-danger" role="alert">
          {importMutation.error.message}
        </p>
      )}

      {isSearching && recipeSection}

      {!isSearching && results.length > 0 && (
        <h2 id="history-heading" className="mt-6 mb-2 text-left text-xl">
          Historique
        </h2>
      )}

      {/* Les aliments suivent les recettes : un titre les sépare. */}
      {isSearching && visibleRecipes.length > 0 && results.length > 0 && (
        <h2 className="mt-6 mb-2 text-left text-xl">Aliments</h2>
      )}

      {results.length > 0 && (
        <ul
          {...(isSearching
            ? { "aria-label": "Résultats de la recherche" }
            : { "aria-labelledby": "history-heading" })}
          className={`${isSearching && visibleRecipes.length === 0 ? "mt-6" : ""} divide-y divide-border overflow-hidden bg-surface`}
        >
          {visibleResults.map((food) => (
            <FoodResultItem
              key={food.food_id ?? food.catalog_code}
              food={food}
              onSelect={() => handleSelect(food)}
              disabled={importMutation.isPending}
              isPending={
                importMutation.isPending && importMutation.variables === food.catalog_code
              }
            />
          ))}
        </ul>
      )}

      {!isSearching && recipeSection}

      {hiddenCount > 0 && (
        <Button
          type="button"
          variant="ghost"
          onClick={() => setExpandedTerm(apiTerm)}
          className="mt-2 w-full text-sm"
        >
          Afficher {hiddenCount} résultat{hiddenCount > 1 ? "s" : ""} de plus
        </Button>
      )}

      {isCatalogUnavailable && (
        <p className="mt-4 text-sm" role="status">
          Certains aliments sont indisponibles pour le moment.
        </p>
      )}

      {hasNoResults && (
        <p className="mt-4">
          Aucun aliment trouvé pour « {searchTerm} ».
        </p>
      )}

      {/* Deux boutons de même largeur sur une rangée. */}
      <div className="mt-6 grid grid-cols-2 gap-2">
        <Button
          type="button"
          onClick={() =>
            navigate("/journal/food/new", { state: { ...journalNavState, name: query.trim() } })
          }
          className="w-full py-3 text-primary font-bold"
        >
          + Créer un aliment
        </Button>
        <Button
          type="button"
          variant="secondary"
          onClick={() => navigate("/recipes/new", { state: journalNavState })}
          className="w-full py-3 font-bold"
        >
          + Créer une recette
        </Button>
      </div>

      {/* Attribution exigée par la licence ODbL. */}
      {needsAttribution && (
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
    </main>
  );
}