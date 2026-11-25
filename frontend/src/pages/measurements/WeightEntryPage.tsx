import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
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

export function WeightEntryPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Dernière mesure, affichée à titre de référence.
  const { latest, isLoading: isLatestLoading, error: latestError } = useMeasurements();

  const [date, setDate] = useState(todayKey());
  const [weight, setWeight] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const weightError = validateWeight(weight);
  const dateError = validateDate(date);
  const canSubmit = weight.trim() !== "" && !weightError && !dateError && !isSubmitting;

  async function handleSubmit(event: React.SubmitEvent) {
    event.preventDefault();
    if (!canSubmit) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const created = await measurementService.createMeasurement({
        date,
        weight_kg: parseDecimal(weight),
      });
      void queryClient.invalidateQueries({ queryKey: queryKeys.measurements.all });
      // Le backend recalcule la cible avec le nouveau poids : le résumé doit la recharger.
      void queryClient.invalidateQueries({ queryKey: queryKeys.currentTarget });
      // Pop-up de confirmation sur l'accueil, avec la nouvelle cible si elle a changé.
      notifySaveResult("Votre mesure a été enregistrée avec succès.", created.target_update);
      // Mesure enregistrée : retour à l'accueil (replace : « Retour » ne ramène pas au formulaire).
      navigate("/", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Impossible d’enregistrer cette mesure.");
      setIsSubmitting(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      <Button type="button" variant="secondary" onClick={() => navigate(-1)} className="text-sm">
        ← Retour
      </Button>

      <h1>Enregistrer mon poids</h1>

      <p className="text-sm">
        {isLatestLoading
          ? "Chargement de votre dernière mesure…"
          : latestError
            ? "Dernière mesure indisponible."
            : latest
              ? `Dernière mesure : ${latest.weight_kg.toLocaleString("fr-CA")} kg le ${formatLongDate(latest.date)}.`
              : "Aucune mesure enregistrée pour l’instant."}
      </p>

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
    </main>
  );
}
