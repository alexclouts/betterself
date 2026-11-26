import Input from "../ui/Input";
import { validateServings, type RecipeDetailsValues } from "../../lib/recipe";
import { RequiredMark } from "../ui/RequiredMark";

type RecipeDetailsFieldsProps = {
  values: RecipeDetailsValues;
  onChange: (values: RecipeDetailsValues) => void;
};

/*
 * Nom, nombre de portions et description d'une recette. Le poids total n'est
 * pas saisi : l'API le calcule à partir des ingrédients.
 */
export function RecipeDetailsFields({ values, onChange }: RecipeDetailsFieldsProps) {
  // Pas d'erreur affichée sur un champ encore vide.
  const servingsError = values.servings.trim() === "" ? null : validateServings(values.servings);

  function setValue(key: keyof RecipeDetailsValues, value: string) {
    onChange({ ...values, [key]: value });
  }

  return (
    <div className="space-y-4 text-left">
      <div className="grid grid-cols-[1fr_6rem] gap-3">
        <label className="block">
          <span className="text-sm font-medium">Nom <RequiredMark /></span>
          <Input
            value={values.name}
            onChange={(event) => setValue("name", event.target.value)}
            maxLength={255}
            className="mt-1"
            required
          />
        </label>

        <label className="block">
          <span className="text-sm font-medium">Portions <RequiredMark /></span>
          <Input
            type="text"
            inputMode="numeric"
            value={values.servings}
            onChange={(event) => setValue("servings", event.target.value)}
            className="mt-1"
            aria-invalid={servingsError !== null}
          />
        </label>
      </div>
      {servingsError && <p className="text-sm text-danger">Portions : {servingsError}</p>}

      <label className="block">
        <span className="text-sm font-medium">Description</span>
        <textarea
          value={values.description}
          onChange={(event) => setValue("description", event.target.value)}
          maxLength={2000}
          rows={3}
          className="mt-1 w-full rounded-l border border-border bg-field p-3 outline-none transition placeholder:text-muted focus:border-primary focus:ring-2 focus:ring-primary/30"
        />
      </label>
    </div>
  );
}
