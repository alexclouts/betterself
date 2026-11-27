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
        L’emballage n’indique pas le poids en grammes de cette portion. Elle est convertie de
        façon approximative : 1 ml ≈ 1 g pour un volume, et 1 tasse ≈ 250 g, 1 c. à soupe ≈ 15 g
        ou 1 c. à thé ≈ 5 g pour une mesure.
      </p>
      <p>
        Ces équivalences valent pour l’eau, mais varient selon l’aliment : une c. à soupe de
        farine pèse environ 8 g, celle de miel environ 21 g. Les calories et les macronutriments
        affichés n’ont donc pas pu être vérifiés. Pour plus de précision, pesez l’aliment et
        saisissez la quantité en grammes.
      </p>
    </WarningBanner>
  );
}
