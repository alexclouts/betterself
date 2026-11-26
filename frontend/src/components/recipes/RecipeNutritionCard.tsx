import { useState } from "react";
import Card from "../ui/Card";
import { SegmentedControl } from "../ui/SegmentedControl";
import { formatNutrient, type FoodNutrients } from "../../lib/food";
import { formatCount, perServing } from "../../lib/recipe";

type Scope = "serving" | "recipe";

const SCOPE_OPTIONS = [
  { value: "serving", label: "Par portion" },
  { value: "recipe", label: "Recette entière" },
] as const;

type RecipeNutritionCardProps = {
  totals: FoodNutrients;
  servings: number;
  // Somme des quantités des ingrédients.
  totalWeightG: number;
};

/*
 * Valeurs nutritionnelles d'une recette, pour une portion ou pour la recette
 * entière : un bouton à bascule choisit ce qui est affiché (une portion par défaut).
 */
export function RecipeNutritionCard({ totals, servings, totalWeightG }: RecipeNutritionCardProps) {
  const [scope, setScope] = useState<Scope>("serving");
  const validServings = Number.isInteger(servings) && servings > 0 ? servings : 1;

  const nutrients = scope === "serving" ? perServing(totals, validServings) : totals;
  const weightLabel =
    scope === "serving"
      ? `1 portion · ${formatNutrient(totalWeightG / validServings, 0)} g`
      : `${formatCount(validServings, "portion", "portions")} · ${formatNutrient(totalWeightG)} g`;

  return (
    <Card className="w-full bg-surface">
      <SegmentedControl
        label="Valeurs affichées"
        options={SCOPE_OPTIONS}
        value={scope}
        onChange={setScope}
        color="secondary"
      />

      {/* Annoncé aux lecteurs d'écran quand on change de vue. */}
      <div aria-live="polite">
        <p className="mt-3 text-sm text-muted">{weightLabel}</p>
        <p className="mt-1 text-foreground">
          <span className="text-4xl font-bold">{formatNutrient(nutrients.calories_kcal, 0)}</span>{" "}
          <span>kcal</span>
        </p>

        <dl className="mt-4 grid grid-cols-3 gap-3">
          <div>
            <dt className="text-sm text-muted">Protéines</dt>
            <dd className="font-semibold text-foreground">{formatNutrient(nutrients.protein_g)} g</dd>
          </div>
          <div>
            <dt className="text-sm text-muted">Glucides</dt>
            <dd className="font-semibold text-foreground">{formatNutrient(nutrients.carbohydrates_g)} g</dd>
          </div>
          <div>
            <dt className="text-sm text-muted">Lipides</dt>
            <dd className="font-semibold text-foreground">{formatNutrient(nutrients.fat_g)} g</dd>
          </div>
        </dl>
      </div>
    </Card>
  );
}
