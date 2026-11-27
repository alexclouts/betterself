import { useId } from "react";
import Input from "./Input";
import Select from "./Select";
import type { UnitOption } from "../../lib/units";

type QuantityFieldProps<T extends string> = {
  value: string;
  onChange: (value: string) => void;
  unit: T;
  units: readonly UnitOption<T>[];
  onUnitChange?: (unit: T) => void;
  // Message affiché sous le champ; null si la saisie est valide.
  error?: string | null;
  // Précision affichée sous le champ quand la saisie est valide (« 2 tranches = 50 g »).
  hint?: string | null;
  autoFocus?: boolean;
};

/*
 * Champ « Quantité » : la saisie et le menu déroulant de l'unité sur la même rangée,
 * pour les aliments comme pour les recettes.
 */
export function QuantityField<T extends string>({
  value,
  onChange,
  unit,
  units,
  onUnitChange,
  error = null,
  hint = null,
  autoFocus,
}: QuantityFieldProps<T>) {
  const id = useId();

  return (
    <div className="text-left">
      <div className="flex gap-2">
        <div className="min-w-0 flex-1">
          <label htmlFor={`${id}-quantity`} className="text-sm font-medium">
            Quantité
          </label>
          <Input
            id={`${id}-quantity`}
            type="text"
            inputMode="decimal"
            value={value}
            onChange={(event) => onChange(event.target.value)}
            className="mt-1 h-13"
            aria-invalid={error !== null}
            aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
            autoFocus={autoFocus}
          />
        </div>
        <div className="w-32 shrink-0">
          <label htmlFor={`${id}-unit`} className="text-sm font-medium">
            Unité
          </label>
          <Select
            id={`${id}-unit`}
            value={unit}
            onChange={(event) => onUnitChange?.(event.target.value as T)}
            className="mt-1 h-13"
          >
            {units.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>
        </div>
      </div>
      {error ? (
        <span id={`${id}-error`} className="mt-1 block text-sm text-danger">
          {error}
        </span>
      ) : (
        hint && (
          <span id={`${id}-hint`} className="mt-1 block text-sm text-muted">
            {hint}
          </span>
        )
      )}
    </div>
  );
}
