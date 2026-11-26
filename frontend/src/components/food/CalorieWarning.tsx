import { useState } from "react";
import { InfoDialog } from "../ui/InfoDialog";

/*
 * Mention « Calories à vérifier sur l'emballage », avec un bouton « i » qui
 * ouvre un dialogue expliquant d'où vient l'avertissement.
 */
export function CalorieWarning({ className = "" }: { className?: string }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={`flex items-center justify-center gap-2 text-sm ${className}`}>
      <span className="text-warning">Calories à vérifier sur l’emballage</span>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        aria-haspopup="dialog"
        aria-label="Pourquoi vérifier les calories ?"
        className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 border-warning font-serif text-xs font-bold text-warning italic hover:bg-warning hover:text-white"
      >
        i
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
    </div>
  );
}
