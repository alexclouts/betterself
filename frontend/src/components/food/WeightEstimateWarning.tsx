import { WarningBanner } from "./WarningBanner";

/*
 * Bandeau « Poids estimé » : la portion ou l'unité de l'aliment n'a pas de poids
 * sur l'étiquette (volume en ml, ou mesure de cuisine sans poids). Les grammes,
 * et donc les macronutriments calculés, n'ont pas pu être vérifiés.
 */
export function WeightEstimateWarning({ className = "" }: { className?: string }) {
  return (
    <WarningBanner
      label="Poids estimé : macronutriments non vérifiés"
      title="Poids estimé"
      className={className}
    >
      <p>
        Nos données pour cet emballage n’indique pas le poids en grammes de cette portion. Elle est convertie de
        façon approximative, ce qui peut produire des erreurs de calcul. Vérifiez la valeur
        nutritionnelle pour confirmer l'exactitude des informations affichées.
      </p>
    </WarningBanner>
  );
}
