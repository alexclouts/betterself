import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import type { PickedFood } from "../lib/recipe";

/*
 * Écran affiché sur une page de recette : la recette elle-même, la recherche
 * d'un ingrédient, ou la fiche d'un ingrédient (nouveau, ou existant via `key`).
 *
 * Les écrans restent dans la même page pour ne pas perdre le brouillon d'une
 * nouvelle recette, mais chacun est une entrée de l'historique (location.state) :
 * le bouton retour du téléphone remonte d'un écran, comme dans le journal.
 */
export type IngredientView =
  | { kind: "recipe" }
  | { kind: "search" }
  | { kind: "entry"; food: PickedFood; quantityG: number; key?: string };

// Écran enregistré dans l'historique, avec sa profondeur depuis l'écran de la recette.
type StackedView = Exclude<IngredientView, { kind: "recipe" }>;
type StoredView = StackedView & { depth: number };

const STATE_KEY = "ingredientView";

function readStoredView(state: unknown): StoredView | null {
  if (!state || typeof state !== "object") return null;
  const stored = (state as Record<string, unknown>)[STATE_KEY];
  if (!stored || typeof stored !== "object") return null;
  const { kind, depth } = stored as Partial<StoredView>;
  if ((kind !== "search" && kind !== "entry") || typeof depth !== "number" || depth < 1) return null;
  return stored as StoredView;
}

export function useIngredientFlow() {
  const navigate = useNavigate();
  const location = useLocation();
  const stored = readStoredView(location.state);
  const view: IngredientView = stored ?? { kind: "recipe" };
  const depth = stored?.depth ?? 0;

  // Chaque écran commence en haut de la page, comme une navigation.
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [view.kind]);

  // Ouvre un écran par-dessus l'écran actuel, en conservant le reste de l'état
  // de navigation (repas et journée du journal).
  function push(next: StackedView) {
    const base = (location.state && typeof location.state === "object" ? location.state : {}) as object;
    navigate(location.pathname + location.search, {
      state: { ...base, [STATE_KEY]: { ...next, depth: depth + 1 } },
    });
  }

  return {
    view,
    // Revient à l'écran de la recette en remontant l'historique.
    showRecipe: () => {
      if (depth > 0) navigate(-depth);
    },
    // Depuis la fiche d'un nouvel ingrédient, la recherche est l'écran précédent.
    showSearch: () => {
      if (view.kind === "entry" && depth >= 2) navigate(-1);
      else push({ kind: "search" });
    },
    showEntry: (food: PickedFood, quantityG: number, key?: string) =>
      push({ kind: "entry", food, quantityG, key }),
  };
}
