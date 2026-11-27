import { WarningBanner } from "./WarningBanner";

/*
 * Bandeau « Calories à vérifier sur l'emballage » : les calories ne correspondent pas
 * à celles calculées à partir des macronutriments.
 */
export function CalorieWarning({ className = "" }: { className?: string }) {
  return (
    <WarningBanner
      label="Calories à vérifier sur l’emballage"
      title="Calories à vérifier"
      className={className}
    >
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
    </WarningBanner>
  );
}
