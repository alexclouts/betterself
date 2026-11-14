import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import type { FoodRead } from "../../api/generated/foodRead";
import { MealType } from "../../api/generated/mealType";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import {
  computeNutrientsForQuantity,
  formatNutrient,
  getDefaultQuantityG,
} from "../../lib/food";
import { foodService } from "../../services/foodService";
import Card from "../../components/ui/Card";

const MAX_QUANTITY_G = 5000;

// Labels pour les types de repas.
const MEAL_TYPE_LABELS: Record<MealType, string> = {
  breakfast: "Déjeuner",
  lunch: "Dîner",
  dinner: "Souper",
  snack: "Collation",
};

// Propose un repas selon l'heure actuelle.
function getDefaultMealType(date = new Date()): MealType {
  const hour = date.getHours();
  
  if (hour < 10) 
    return MealType.breakfast;
  if (hour < 14) 
    return MealType.lunch;
  if (hour >= 17 && hour < 21) 
    return MealType.dinner;

  return MealType.snack;
}


export function FoodAddPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const location = useLocation();

  // L'aliment peut être transmis par la page de recherche pour éviter un appel.
  const foodFromState = (location.state as { food?: FoodRead } | null)?.food;
  // Si l'aliment n'a pas été transmis par l'état, il sera chargé depuis le service.
  const initialFood = foodFromState && foodFromState.id === id ? foodFromState : null;

  const [food, setFood] = useState<FoodRead | null>(initialFood);
  const [quantityInput, setQuantityInput] = useState(
    initialFood ? String(getDefaultQuantityG(initialFood)) : "",
  );
  const [mealType, setMealType] = useState<MealType>(getDefaultMealType);
  const [isLoading, setIsLoading] = useState(!initialFood);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (food || !id) return;

    let cancelled = false;
    setIsLoading(true);

    // Chargement de l'aliment depuis le service
    foodService.getFood(id).then((result) => {
      if (cancelled) 
        return;
        
      setFood(result);
      setQuantityInput(String(getDefaultQuantityG(result)));
      })
      .catch((err) => {
        if (cancelled) 
          return;

        setError(
          err instanceof Error ? err.message : "Impossible de charger cet aliment.",
        );
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [id, food]);


  // Accepte la virgule comme séparateur décimal.
  const quantityG = Number(quantityInput.replace(",", "."));


  // Détermine si la quantité saisie est valide.
  const isQuantityValid = quantityInput.trim() !== "" && Number.isFinite(quantityG) && quantityG > 0 && quantityG <= MAX_QUANTITY_G;

  // Calcule les nutriments pour la quantité saisie.
  const nutrients = useMemo(() =>
    food && isQuantityValid ? computeNutrientsForQuantity(food, quantityG) : null,
    [food, isQuantityValid, quantityG],
  );

  // Gestion de la soumission du formulaire.
  async function handleSubmit(event: React.SubmitEvent) {
    event.preventDefault();

    if (!food || !isQuantityValid) 
      return;

    setIsSubmitting(true);
    setError(null);

    try {
      // Ajout de l'aliment au journal avec la quantité et le type de repas spécifiés.
      await foodService.addFoodToJournal({
        food_id: food.id,
        quantity_g: quantityG,
        meal_type: mealType,
      });
      navigate("/", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Impossible d’ajouter cet aliment au journal.");
    } finally {
      setIsSubmitting(false);
    }
  }
  // Affichage du chargement si nécessaire.
  if (isLoading) {
    return (
      <main className="mx-auto w-full max-w-md px-4 py-6">
        <p className="text-sm text-gray-500">Chargement…</p>
      </main>
    );
  }

  // Affichage de l'erreur si l'aliment n'a pas pu être chargé.
  if (!food) {
    return (
      <main className="mx-auto w-full max-w-md px-4 py-6">
        <p className="text-sm text-red-600">{error ?? "Aliment introuvable."}</p>
        <Button variant="ghost" className="mt-4" onClick={() => navigate("/journal/add")}>
          Retour à la recherche
        </Button>
      </main>
    );
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

      <h1 className="mt-2 text-xl font-semibold">{food.name}</h1>
      {food.brand && <p className="text-sm text-gray-500">{food.brand}</p>}
      <p className="mt-1 text-sm text-gray-500">
        Portion de référence : {formatNutrient(food.reference_weight_g)} g
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <label className="block">
          <span className="text-sm font-medium">Quantité (g)</span>
          <Input
            type="text"
            inputMode="decimal"
            value={quantityInput}
            onChange={(event) => setQuantityInput(event.target.value)}
            className="mt-1"
            aria-invalid={!isQuantityValid}
          />
          {!isQuantityValid && quantityInput.trim() !== "" && (
            <span className="mt-1 block text-sm text-red-600">
              Entrez une quantité entre 0 et {MAX_QUANTITY_G} g.
            </span>
          )}
        </label>

        <label className="block">
          <span className="text-sm font-medium">Repas</span>
          <Select
            value={mealType}
            onChange={(event) => setMealType(event.target.value as MealType)}
            className="mt-1"
          >
            {Object.values(MealType).map((type) => (
              <option key={type} value={type}>
                {MEAL_TYPE_LABELS[type]}
              </option>
            ))}
          </Select>
        </label>

        <Card className="w-full p-6 mt-6 bg-surface">
          <dl className="grid grid-cols-3 gap-3">
            <div className="col-span-3">
              <dt>Calories</dt>
              <dd className="text-2xl font-semibold mb-4">
                {nutrients ? formatNutrient(nutrients.calories_kcal, 0) : "–"} kcal
              </dd>
            </div>
            <div>
              <dt>Protéines</dt>
              <dd>{nutrients ? formatNutrient(nutrients.protein_g) : "–"} g</dd>
            </div>
            <div>
              <dt>Glucides</dt>
              <dd>{nutrients ? formatNutrient(nutrients.carbohydrates_g) : "–"} g</dd>
            </div>
            <div>
              <dt>Lipides</dt>
              <dd>{nutrients ? formatNutrient(nutrients.fat_g) : "–"} g</dd>
            </div>
          </dl>
        </Card>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <Button
          type="submit"
          className="w-full mt-2"
          disabled={!isQuantityValid || isSubmitting}
        >
          {isSubmitting ? "Ajout…" : "Ajouter au journal"}
        </Button>
      </form>
    </main>
  );
}
