import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import type { MeasurementRead } from "../../api/generated/measurementRead";
import type { TargetUpdateRead } from "../../api/generated/targetUpdateRead";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import { useMeasurements } from "../../hooks/useMeasurements";
import { formatLongDate, parseDateKey, todayKey } from "../../lib/date";
import { queryKeys } from "../../lib/queryClient";
import { notifySaveResult } from "../../lib/targetUpdate";
import { measurementService } from "../../services/measurementService";

// Mêmes bornes que le backend (MeasurementCreate et contraintes de la table measurements).
const MIN_WEIGHT_KG = 30; // exclu
const MAX_WEIGHT_KG = 500; // inclus
const MIN_DATE = "2020-01-01";

// Accepte la virgule comme séparateur décimal ; NaN si vide ou invalide.
function parseDecimal(value: string): number {
  if (value.trim() === "") return NaN;
  return Number(value.replace(",", "."));
}

// Retourne le message d'erreur du poids saisi, ou null s'il est valide (ou vide).
function validateWeight(raw: string): string | null {
  if (raw.trim() === "") return null;
  const value = parseDecimal(raw);
  if (!Number.isFinite(value)) return "Valeur invalide.";
  if (value <= MIN_WEIGHT_KG) return `Doit être supérieur à ${MIN_WEIGHT_KG} kg.`;
  if (value > MAX_WEIGHT_KG) return `Maximum ${MAX_WEIGHT_KG} kg.`;
  return null;
}

// Retourne le message d'erreur de la date choisie, ou null si elle est valide.
// Les clés "YYYY-MM-DD" se comparent correctement comme des chaînes.
function validateDate(key: string): string | null {
  if (!parseDateKey(key)) return "Date invalide.";
  if (key < MIN_DATE) return "La date doit être postérieure au 1er janvier 2020.";
  if (key > todayKey()) return "La date ne peut pas être dans le futur.";
  return null;
}

/*
 * Enregistrement d'un poids (/measurements/new) ou modification d'une mesure
 * existante (/measurements/:measurementId/edit). En modification, le formulaire
 * attend que la mesure soit chargée pour s'initialiser avec ses valeurs.
 */
export function WeightEntryPage() {
  const navigate = useNavigate();
  const { measurementId } = useParams();
  const { history, latest, isLoading, error } = useMeasurements();

  const isEditing = measurementId !== undefined;
  const editedMeasurement = isEditing
    ? history.find((measurement) => String(measurement.id) === measurementId) ?? null
    : null;

  // Message de référence sous le titre.
  const reference = isLoading
    ? "Chargement de vos mesures…"
    : error
      ? "Dernière mesure indisponible."
      : isEditing
        ? editedMeasurement
          ? `Valeur enregistrée : ${editedMeasurement.weight_kg.toLocaleString("fr-CA")} kg le ${formatLongDate(editedMeasurement.date)}.`
          : null
        : latest
          ? `Dernière mesure : ${latest.weight_kg.toLocaleString("fr-CA")} kg le ${formatLongDate(latest.date)}.`
          : "Aucune mesure enregistrée pour l’instant.";

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      <Button type="button" variant="secondary" onClick={() => navigate(-1)} className="text-sm">
        ← Retour
      </Button>

      <h1>{isEditing ? "Modifier une mesure" : "Enregistrer mon poids"}</h1>

      {reference && <p className="text-sm">{reference}</p>}

      {!isEditing ? (
        <WeightForm />
      ) : isLoading ? null : editedMeasurement ? (
        // key : réinitialise le formulaire si on passe d'une mesure à une autre.
        <WeightForm key={editedMeasurement.id} measurement={editedMeasurement} />
      ) : (
        <p className="mt-6 text-danger" role="alert">
          {error ?? "Cette mesure est introuvable."}
        </p>
      )}
    </main>
  );
}

function WeightForm({ measurement }: { measurement?: MeasurementRead }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEditing = measurement !== undefined;

  const [date, setDate] = useState(measurement?.date ?? todayKey());
  const [weight, setWeight] = useState(
    measurement ? String(measurement.weight_kg).replace(".", ",") : "",
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const weightError = validateWeight(weight);
  const dateError = validateDate(date);
  // En modification, rien à enregistrer tant que les valeurs n'ont pas changé.
  const hasChanges =
    !measurement || date !== measurement.date || parseDecimal(weight) !== measurement.weight_kg;
  const canSubmit =
    weight.trim() !== "" && !weightError && !dateError && hasChanges && !isSubmitting;

  async function handleSubmit(event: React.SubmitEvent) {
    event.preventDefault();
    if (!canSubmit) return;

    setIsSubmitting(true);
    setError(null);

    const payload = { date, weight_kg: parseDecimal(weight) };

    try {
      let targetUpdate: TargetUpdateRead | null | undefined;
      if (measurement) {
        const updated = await measurementService.updateMeasurement(measurement.id, payload);
        targetUpdate = updated.target_update;
      } else {
        const created = await measurementService.createMeasurement(payload);
        targetUpdate = created.target_update;
      }

      void queryClient.invalidateQueries({ queryKey: queryKeys.measurements.all });
      // Le backend peut avoir recalculé la cible avec ce poids : le résumé doit la recharger.
      void queryClient.invalidateQueries({ queryKey: queryKeys.currentTarget });
      // Pop-up de confirmation, avec la nouvelle cible si elle a changé.
      notifySaveResult(
        isEditing
          ? "Votre mesure a été modifiée avec succès."
          : "Votre mesure a été enregistrée avec succès.",
        targetUpdate,
      );
      // Retour à l'historique (modification) ou à l'accueil (nouvelle mesure).
      // replace : « Retour » ne ramène pas au formulaire.
      navigate(isEditing ? "/measurements" : "/", { replace: true });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : isEditing
            ? "Impossible de modifier cette mesure."
            : "Impossible d’enregistrer cette mesure.",
      );
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-6 space-y-4 text-left">
      <label className="block">
        <span className="text-sm font-medium">Date *</span>
        <Input
          type="date"
          value={date}
          min={MIN_DATE}
          max={todayKey()}
          onChange={(event) => setDate(event.target.value)}
          className="mt-1"
          aria-invalid={dateError !== null}
          required
        />
        {dateError && <span className="mt-1 block text-sm text-danger">{dateError}</span>}
      </label>

      <label className="block">
        <span className="text-sm font-medium">Poids (kg) *</span>
        <Input
          type="text"
          inputMode="decimal"
          placeholder="ex. 72,5"
          value={weight}
          onChange={(event) => setWeight(event.target.value)}
          className="mt-1"
          aria-invalid={weightError !== null}
          required
        />
        {weightError && <span className="mt-1 block text-sm text-danger">{weightError}</span>}
      </label>

      {error && <p className="text-danger" role="alert">{error}</p>}

      <Button type="submit" className="w-full mt-2 font-bold" disabled={!canSubmit}>
        {isSubmitting ? "Enregistrement…" : "Enregistrer"}
      </Button>
    </form>
  );
}
