import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { MeasurementRead } from "../../api/generated/measurementRead";
import { WeightChart } from "../../components/measurements/WeightChart";
import Button from "../../components/ui/Button";
import Card from "../../components/ui/Card";
import { useCurrentGoal } from "../../hooks/useCurrentGoal";
import { useMeasurements } from "../../hooks/useMeasurements";
import { formatLongDate } from "../../lib/date";
import { queryKeys } from "../../lib/queryClient";
import { notifySaveResult } from "../../lib/targetUpdate";
import { weightTrend, type WeightTrend } from "../../lib/weightTrend";
import { measurementService } from "../../services/measurementService";
import { useToastStore } from "../../stores/toastStore";

function formatWeight(value: number): string {
  return `${value.toLocaleString("fr-CA", { maximumFractionDigits: 2 })} kg`;
}

// Écart avec la mesure précédente : « +0,4 kg », « −1,2 kg » ou « = » si identique.
function formatDelta(delta: number): string {
  const rounded = Math.round(delta * 10) / 10;
  if (rounded === 0) return "";
  const sign = rounded > 0 ? "+" : "−";
  return `${sign}${Math.abs(rounded).toLocaleString("fr-CA", { minimumFractionDigits: 1 })} kg`;
}

// Vert si le poids se rapproche de l'objectif, rouge s'il s'en éloigne.
const TREND_CLASSES: Record<WeightTrend, string> = {
  toward: "text-primary-dark dark:text-primary",
  away: "text-danger",
  neutral: "text-muted",
};

// Ajouté au libellé de la ligne pour les lecteurs d'écran : la couleur seule ne doit pas porter l'information.
const TREND_LABELS: Record<WeightTrend, string | undefined> = {
  toward: "vers votre objectif",
  away: "s’éloigne de votre objectif",
  neutral: undefined,
};

/*
 * Historique des pesées, de la plus récente à la plus ancienne. Chaque mesure
 * peut être modifiée ou supprimée ; si la mesure la plus récente change, le
 * backend recalcule la cible et le pop-up l'annonce.
 */
export function MeasurementsPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { measurements, history, isLoading, error: loadError } = useMeasurements();
  // Sans objectif (ou en cas d'erreur), les variations restent en gris.
  const { goal } = useCurrentGoal();

  const deleteMutation = useMutation({
    mutationFn: (measurementId: number) => measurementService.deleteMeasurement(measurementId),
    onSuccess: (result, measurementId) => {
      // Retire la mesure immédiatement de la liste…
      queryClient.setQueryData<MeasurementRead[]>(
        queryKeys.measurements.list,
        (current) => current?.filter((item) => item.id !== measurementId),
      );
      // …puis recharge les mesures (graphique de l'accueil) et la cible, qui a pu être recalculée.
      void queryClient.invalidateQueries({ queryKey: queryKeys.measurements.all });
      void queryClient.invalidateQueries({ queryKey: queryKeys.currentTarget });
      notifySaveResult("Votre mesure a été supprimée.", result.target_update);
    },
  });

  const deletingId = deleteMutation.isPending ? deleteMutation.variables : null;
  const error = loadError ?? deleteMutation.error?.message ?? null;
  // Le poids actuel est nécessaire au calcul de la cible : l'API refuse de
  // supprimer la seule mesure restante.
  const isOnlyMeasurement = history.length <= 1;

  function handleDelete(measurement: MeasurementRead) {
    if (isOnlyMeasurement) {
      useToastStore.getState().showToast(
        "Votre seule mesure ne peut pas être supprimée, puisqu’elle sert au calcul de votre cible. Vous pouvez la modifier.",
        { variant: "error" },
      );
      return;
    }
    const label = `${formatWeight(measurement.weight_kg)} le ${formatLongDate(measurement.date)}`;
    if (!window.confirm(`Supprimer la mesure de ${label} ?`)) {
      return;
    }
    deleteMutation.mutate(measurement.id);
  }

  // Sous le graphique, ou sous le message s'il n'y a encore aucune mesure.
  const updateButton = (
    <Button
      type="button"
      className="mt-4 w-full font-bold"
      onClick={() => navigate("/measurements/new")}
    >
      Mettre à jour
    </Button>
  );

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6 text-center">
      <h1>Mes mesures</h1>

      {error && (
        <p className="mt-4 text-danger" role="alert">
          {error}
        </p>
      )}

      {isLoading ? (
        <p className="mt-6">Chargement de vos mesures…</p>
      ) : history.length === 0 ? (
        <>
          <p className="mt-6">Aucune mesure enregistrée pour l’instant.</p>
          {updateButton}
        </>
      ) : (
        <>
          {/* Même courbe que l'accueil (une mesure par jour), au-dessus de l'historique détaillé. */}
          <section className="mt-6" aria-labelledby="weight-chart-heading">
            <Card className="w-full bg-surface">
              <h2 id="weight-chart-heading" className="mt-0 mb-2 text-left text-xl">
                Mon poids
              </h2>
              <WeightChart measurements={measurements} showData={false} />
            </Card>
            {updateButton}
          </section>

          <h2 className="mt-8 mb-0 text-left text-xl">Historique</h2>
          <ul className="mt-2 divide-y divide-border text-left">
            {history.map((measurement, index) => {
              // La liste va de la plus récente à la plus ancienne : la précédente est la suivante.
              const previous = history[index + 1];
              const trend = previous ? weightTrend(previous.weight_kg, measurement.weight_kg, goal) : "neutral";
              const label = `${formatWeight(measurement.weight_kg)} le ${formatLongDate(measurement.date)}`;

              return (
                <li key={measurement.id} className="flex items-center gap-3 py-3">
                  {/* Un clic ouvre le formulaire de modification. */}
                  <button
                    type="button"
                    onClick={() => navigate(`/measurements/${measurement.id}/edit`)}
                    aria-label={[
                      `Modifier la mesure de ${label}`,
                      previous && formatDelta(measurement.weight_kg - previous.weight_kg),
                      TREND_LABELS[trend],
                    ].filter(Boolean).join(", ")}
                    className="flex min-w-0 flex-1 items-baseline justify-between gap-3 rounded-lg px-2 py-1 text-left hover:bg-surface-raised"
                  >
                    <span className="min-w-0">
                      <span className="block text-foreground">{formatLongDate(measurement.date)}</span>
                      {index === 0 && <span className="text-sm text-muted">Poids actuel</span>}
                    </span>
                    <span className="shrink-0 text-right">
                      <strong className="block text-foreground">{formatWeight(measurement.weight_kg)}</strong>
                      {previous && (
                        <span className={`text-sm ${TREND_CLASSES[trend]}`}>
                          {formatDelta(measurement.weight_kg - previous.weight_kg)}
                        </span>
                      )}
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => handleDelete(measurement)}
                    disabled={deletingId === measurement.id}
                    aria-label={`Supprimer la mesure de ${label}`}
                    className="rounded-full px-3 py-1 text-muted hover:bg-surface-raised hover:text-danger disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-muted"
                  >
                    ✕
                  </button>
                </li>
              );
            })}
          </ul>
        </>
      )}
    </main>
  );
}
