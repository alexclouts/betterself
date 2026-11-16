import { useEffect, useState } from "react";

/*
 * Retourne `value` seulement après `delayMs` sans changement.
 * Utile pour ne pas lancer une recherche à chaque frappe.
 * La valeur initiale est retournée immédiatement (pas de délai au montage).
 */
export function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timeoutId = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timeoutId);
  }, [value, delayMs]);

  return debounced;
}
