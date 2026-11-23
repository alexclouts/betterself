import { getErrorMessage } from "../api/axios";
import { getMesures } from "../api/generated/endpoints/mesures/mesures";
import type { MeasurementCreate } from "../api/generated/measurementCreate";
import type { MeasurementRead } from "../api/generated/measurementRead";

export const measurementService = {
    // Récupère toutes les mesures de l'utilisateur, triées par date croissante (tri de l'API).
    async listMeasurements(): Promise<MeasurementRead[]> {
        try {
            const { getMeasurementsMeasurementsGet } = getMesures();
            return await getMeasurementsMeasurementsGet();
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de charger vos mesures."),
                { cause: error }
            );
        }
    },

    // Enregistre une mesure de poids pour l'utilisateur connecté.
    async createMeasurement(payload: MeasurementCreate): Promise<MeasurementRead> {
        try {
            const { createMeasurementMeasurementsPost } = getMesures();
            return await createMeasurementMeasurementsPost(payload);
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible d’enregistrer cette mesure."),
                { cause: error }
            );
        }
    },
};
