import { useState } from "react";
import { InfoDialog } from "../ui/InfoDialog";

/*
 * Bandeau « Calories à vérifier sur l'emballage », en bas de la carte des valeurs
 * nutritives. Tout le bandeau est un bouton qui ouvre l'explication.
 */
export function CalorieWarning({ className = "" }: { className?: string }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        aria-haspopup="dialog"
        className={`flex w-full items-center gap-2 rounded-xl bg-warning/10 px-3 py-2 text-left text-sm font-semibold text-warning transition hover:bg-warning/20 ${className}`}
      >
        {/* Triangle d'avertissement. */}
        <svg
          viewBox="0 0 24 24"
          className="h-5 w-5 shrink-0"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" />
          <path d="M12 9v4M12 17h.01" />
        </svg>
        <span className="flex-1">Calories à vérifier sur l’emballage</span>
        {/* Cercle « i » : le bandeau ouvre une explication. */}
        <svg
          viewBox="0 0 24 24"
          className="h-5 w-5 shrink-0"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="9" />
          <path d="M12 11v5M12 8h.01" />
        </svg>
      </button>

      <InfoDialog open={isOpen} title="Calories à vérifier" onClose={() => setIsOpen(false)}>
        <p>
          Les calories indiquées ne correspondent pas à celles calculées à partir des
          macronutriments : 4 kcal par gramme de protéines et de glucides, 9 kcal par gramme de
          lipides.
        </p>
        <p>
          L’écart peut être normal, par exemple à cause des fibres, des polyols ou de l’alcool,
          mais il peut aussi venir d’une erreur dans la base de données. Comparez avec l’étiquette
          de l’emballage avant d’ajouter l’aliment.
        </p>
      </InfoDialog>
    </>
  );
}
