import { formatNutrient } from "../../lib/food";

export type CompositionItem = {
  key: string;
  name: string;
  quantityG: number;
  caloriesKcal: number;
};

type RecipeCompositionProps = {
  items: CompositionItem[];
  onOpen: (key: string) => void;
  onRemove: (key: string) => void;
  onAdd: () => void;
  // Le dernier ingrédient d'une recette enregistrée ne peut pas être retiré.
  canRemove?: boolean;
  removingKey?: string | null;
};

/*
 * Ingrédients d'une recette, présentés comme un repas du journal : titre et
 * total des calories, une ligne par ingrédient, puis « + Ajouter un ingrédient ».
 */
export function RecipeComposition({
  items,
  onOpen,
  onRemove,
  onAdd,
  canRemove = true,
  removingKey = null,
}: RecipeCompositionProps) {
  const totalCalories = items.reduce((total, item) => total + item.caloriesKcal, 0);

  return (
    <section aria-labelledby="composition-heading" className="text-center">
      <div className="flex items-baseline justify-between border-b border-border pb-2">
        <h3 id="composition-heading" className="text-lg font-semibold text-foreground">
          Ingrédients
        </h3>
        <span className="text-sm font-bold text-foreground">{formatNutrient(totalCalories, 0)} kcal</span>
      </div>

      {items.length === 0 ? (
        <p className="py-3">Aucun ingrédient.</p>
      ) : (
        <ul className="divide-y divide-border">
          {items.map((item) => (
            <li key={item.key} className="flex items-center gap-3 py-3">
              {/* Un clic ouvre la fiche de l'ingrédient pour modifier sa quantité. */}
              <button
                type="button"
                onClick={() => onOpen(item.key)}
                className="flex min-w-0 flex-1 items-baseline justify-between gap-3 rounded-lg px-2 py-1 text-left hover:bg-surface-raised"
              >
                <span className="min-w-0">
                  <span className="block truncate text-foreground">{item.name}</span>
                  <span className="text-sm text-muted">{formatNutrient(item.quantityG)} g</span>
                </span>
                {/* Calories en évidence, comme dans le journal. */}
                <span className="shrink-0 text-sm font-bold text-foreground">
                  {formatNutrient(item.caloriesKcal, 0)} kcal
                </span>
              </button>

              <button
                type="button"
                onClick={() => onRemove(item.key)}
                disabled={!canRemove || removingKey === item.key}
                aria-label={`Retirer ${item.name}`}
                title={canRemove ? undefined : "Une recette doit contenir au moins un ingrédient."}
                className="rounded-full px-3 py-1 text-muted hover:bg-surface-raised hover:text-danger disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-muted"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      )}

      <button type="button" onClick={onAdd} className="mt-1 text-sm font-semibold text-primary-ink">
        + Ajouter un ingrédient
      </button>
    </section>
  );
}
