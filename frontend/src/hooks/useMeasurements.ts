import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import type { MeasurementRead } from "../api/generated/measurementRead";
import { queryKeys } from "../lib/queryClient";
import { measurementService } from "../services/measurementService";

/*
 * Mesures de poids de l'utilisateur, partagées par l'accueil (graphique) et la
 * page d'enregistrement (dernière mesure). Rechargées après chaque enregistrement
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
      if (!existing || measurement.id > existing.id) byDate.set(measurement.date, measurement);
    }
    return [...byDate.values()].sort((a, b) => a.date.localeCompare(b.date));
  }, [query.data]);

  return {
    measurements: daily,
    latest: daily.at(-1) ?? null,
    isLoading: query.isPending,
    error: query.error?.message ?? null,
  };
}
