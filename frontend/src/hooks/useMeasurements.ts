import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import type { MeasurementRead } from "../api/generated/measurementRead";
import { queryKeys } from "../lib/queryClient";
import { measurementService } from "../services/measurementService";

/*
 * Mesures de poids de l'utilisateur, partagées par l'accueil (graphique), la
 * page d'enregistrement (dernière mesure) et l'historique. Rechargées après chaque enregistrement
 * grâce à l'invalidation de queryKeys.measurements.all.
 */
export function useMeasurements() {
  const query = useQuery({
    queryKey: queryKeys.measurements.list,
    queryFn: () => measurementService.listMeasurements(),
  });

  // Une seule valeur par jour : en cas de doublon, la mesure saisie en dernier
  // (id le plus grand) l'emporte. Le résultat reste trié par date croissante.
  const daily = useMemo(() => {
    const byDate = new Map<string, MeasurementRead>();
    for (const measurement of query.data ?? []) {
      const existing = byDate.get(measurement.date);
      
      if (!existing || measurement.id > existing.id) 
        byDate.set(measurement.date, measurement);
    }
    return [...byDate.values()].sort((a, b) => a.date.localeCompare(b.date));
  }, [query.data]);

  // Toutes les mesures, doublons compris, de la plus récente à la plus ancienne :
  // l'historique doit permettre de corriger ou supprimer chacune d'elles.
  const history = useMemo(
    () => [...(query.data ?? [])].sort((a, b) => b.date.localeCompare(a.date) || b.id - a.id),
    [query.data],
  );

  return {
    measurements: daily,
    history,
    latest: daily.at(-1) ?? null,
    isLoading: query.isPending,
    error: query.error?.message ?? null,
  };
}
