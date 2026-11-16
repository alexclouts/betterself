import { useEffect, useState } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { foodService } from "../../services/foodService";
import { formatNutrient } from "../../lib/food";
import { readJournalNavState } from "../../lib/journal";
import { queryKeys } from "../../lib/queryClient";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";

// Nombre minimal de caractères avant de lancer une recherche.
const MIN_SEARCH_LENGTH = 2;

// Délai sans frappe avant de lancer la recherche.
const SEARCH_DELAY_MS = 300;

export function FoodSearchPage() {
  const navigate = useNavigate();
  const location = useLocation();
  // Repas et journée choisis depuis le journal, relayés jusqu'à la page d'ajout.
  const journalNavState = readJournalNavState(location.state);

  // Le terme recherché est conservé dans l'URL (?q=...) : au retour depuis
  // la page d'un aliment, la recherche et ses résultats sont retrouvés.
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(() => searchParams.get("q") ?? "");
  const searchTerm = useDebouncedValue(query.trim(), SEARCH_DELAY_MS);
  const isSearchEnabled = searchTerm.length >= MIN_SEARCH_LENGTH;

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
    queryKey: queryKeys.foods.search(searchTerm),
    queryFn: ({ signal }) => foodService.searchFoods(searchTerm, {}, signal),
    enabled: isSearchEnabled,
    // Garde les résultats précédents affichés pendant le chargement des nouveaux.
    placeholderData: keepPreviousData,
    // Le catalogue d'aliments change peu.
    staleTime: 5 * 60_000,
  });

  const foods = isSearchEnabled ? (searchQuery.data ?? []) : [];
  const isLoading = isSearchEnabled && searchQuery.isFetching;
  const error = isSearchEnabled ? (searchQuery.error?.message ?? null) : null;
  // « Aucun résultat » seulement quand la réponse du terme en cours est arrivée.
  const hasNoResults = isSearchEnabled && searchQuery.isSuccess && !searchQuery.isPlaceholderData && foods.length === 0;

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

      <ul className="mt-4 divide-y">
        {foods.map((food) => (
          <li key={food.id}>
            <button
              type="button"
              onClick={() =>
                // On transmet l'aliment pour éviter un nouvel appel ; la quantité
                // sera initialisée à la portion de référence et modifiable à l'ajout.
                navigate(`/journal/food/${food.id}`, { state: { ...journalNavState, food } })
              }
              className="flex w-full items-center justify-between py-3 text-left"
            >
              <span>{food.name}</span>

              <span className="text-sm text-gray-500">
                {formatNutrient(food.calories_kcal, 0)} kcal /{" "}
                {formatNutrient(food.reference_weight_g)} g
              </span>
            </button>
          </li>
        ))}
      </ul>

      {hasNoResults && (
        <p className="mt-4">
          Aucun aliment trouvé pour « {searchTerm} ».
        </p>
      )}

        <Button
          type="button"
          onClick={() =>
            navigate("/journal/food/new", { state: { ...journalNavState, name: query.trim() } })
          }
          className="mt-4 w-full rounded-lg py-3 text-sm text-primary font-bold"
        >
          + Créer un nouvel aliment
        </Button>
    </main>
  );
}