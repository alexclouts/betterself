import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { foodService } from "../../services/foodService";
import type { FoodRead } from "../../api/generated/foodRead";
import { formatNutrient } from "../../lib/food";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";

export function FoodSearchPage() {
  const navigate = useNavigate();

  const [query, setQuery] = useState("");
  const [foods, setFoods] = useState<FoodRead[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (query.trim().length < 2) {
      setFoods([]);
      return;
    }

    const timeoutId = setTimeout(async () => {
      setIsLoading(true);
      setError(null);

      try {
        const results = await foodService.searchFoods(query);
        setFoods(results);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Impossible de rechercher les aliments."
        );
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query]);

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

      <h1 className="mt-2 text-xl font-semibold">
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
        <p className="mt-4 text-sm text-gray-500">
          Recherche…
        </p>
      )}

      {error && (
        <p className="mt-4 text-sm text-red-600">
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
                navigate(`/journal/food/${food.id}`, { state: { food } })
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

      {!isLoading && !error && query.trim().length >= 2 && foods.length === 0 && (
        <p className="mt-4 text-sm text-gray-500">
          Aucun aliment trouvé pour « {query.trim()} ».
        </p>
      )}

        <Button
          type="button"
          onClick={() =>
            navigate("/journal/food/new", { state: { name: query.trim() } })
          }
          className="mt-4 w-full rounded-lg py-3 text-sm text-primary font-bold"
        >
          + Créer un nouvel aliment
        </Button>
    </main>
  );
}