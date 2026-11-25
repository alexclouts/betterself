import { useEffect, useState } from "react";
import type { PickedFood } from "../lib/recipe";

/*
 * Écran affiché sur une page de recette : la recette elle-même, la recherche
 * d'un ingrédient, ou la fiche d'un ingrédient (nouveau, ou existant via `key`).
 * Les écrans restent dans la même page pour ne pas perdre le brouillon d'une
 * nouvelle recette.
 */
export type IngredientView =
  | { kind: "recipe" }
  | { kind: "search" }
  | { kind: "entry"; food: PickedFood; quantityG: number; key?: string };

export function useIngredientFlow() {
  const [view, setView] = useState<IngredientView>({ kind: "recipe" });

  // Chaque écran commence en haut de la page, comme une navigation.
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [view.kind]);

  return {
    view,
    showRecipe: () => setView({ kind: "recipe" }),
    showSearch: () => setView({ kind: "search" }),
    showEntry: (food: PickedFood, quantityG: number, key?: string) =>
      setView({ kind: "entry", food, quantityG, key }),
  };
}
