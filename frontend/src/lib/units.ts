// Unités de saisie des quantités (components/ui/QuantityField).
export type UnitOption<T extends string> = { value: T; label: string };

// Unité des aliments pour l'instant; d'autres unités s'ajouteront à cette liste.
export const GRAM_UNIT_OPTIONS = [{ value: "grams", label: "g" }] as const;
