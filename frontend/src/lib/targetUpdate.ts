// src/lib/targetUpdate.ts
import type { TargetUpdateRead } from "../api/generated/targetUpdateRead";
import { useToastStore } from "../stores/toastStore";

function formatKcal(value: number): string {
  return `${value.toLocaleString("fr-CA")} kcal`;
}

/*
 * Confirme un enregistrement (nouvelle mesure, modification du profil) par un pop-up,
 * en y joignant le résultat du recalcul automatique de la cible renvoyé par l'API :
 * - cible modifiée : un seul pop-up (confirmation + nouvelles calories) ;
 * - recalcul impossible : la confirmation, puis un second pop-up d'avertissement ;
 * - aucun recalcul ou calories inchangées : la confirmation seule.
 */
export function notifySaveResult(
  successMessage: string,
  update: TargetUpdateRead | null | undefined,
): void {
  const { showToast } = useToastStore.getState();
  const previous = update?.previous_calories_target_kcal ?? null;
  const current = update?.calories_target_kcal ?? null;

  if (update?.status === "failed") {
    showToast(successMessage);
    const kept = previous !== null ? ` Votre cible actuelle (${formatKcal(previous)}) est conservée.` : "";
    showToast(
      `Votre cible n’a pas pu être recalculée. ${update.message ?? ""}${kept}`.replace(/\s+/g, " ").trim(),
      // Message plus long et plus important : il reste affiché plus longtemps.
      { variant: "warning", duration: 9000 },
    );
    return;
  }

  if (update?.status === "updated" && current !== null && current !== previous) {
    showToast(
      previous !== null
        ? `${successMessage} Votre cible passe de ${formatKcal(previous)} à ${formatKcal(current)} par jour.`
        : `${successMessage} Votre cible est maintenant de ${formatKcal(current)} par jour.`,
      // Deux phrases à lire : un peu plus de temps.
      { duration: 7000 },
    );
    return;
  }

  showToast(successMessage);
}
