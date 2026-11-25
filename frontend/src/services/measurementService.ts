import { getErrorMessage } from "../api/axios";
import { getMesures } from "../api/generated/endpoints/mesures/mesures";
import type { MeasurementCreate } from "../api/generated/measurementCreate";
import type { MeasurementCreatedRead } from "../api/generated/measurementCreatedRead";
import type { MeasurementDeletedRead } from "../api/generated/measurementDeletedRead";
import type { MeasurementRead } from "../api/generated/measurementRead";
import type { MeasurementUpdate } from "../api/generated/measurementUpdate";
import type { MeasurementUpdatedRead } from "../api/generated/measurementUpdatedRead";

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
    // La réponse inclut `target_update` : le résultat du recalcul automatique de la cible.
    async createMeasurement(payload: MeasurementCreate): Promise<MeasurementCreatedRead> {
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

    // Modifie la date ou le poids d'une mesure.
    // La réponse inclut `target_update` si la mesure était ou devient la plus récente.
    async updateMeasurement(id: number, payload: MeasurementUpdate): Promise<MeasurementUpdatedRead> {
        try {
            const { updateMeasurementMeasurementsMeasurementIdPatch } = getMesures();
            return await updateMeasurementMeasurementsMeasurementIdPatch(id, payload);
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de modifier cette mesure."),
                { cause: error }
            );
        }
    },

    // Supprime une mesure. La réponse inclut `target_update` si la mesure supprimée
    // était la plus récente. L'API refuse (409) de supprimer la seule mesure restante.
    async deleteMeasurement(id: number): Promise<MeasurementDeletedRead> {
        try {
            const { deleteMeasurementMeasurementsMeasurementIdDelete } = getMesures();
            return await deleteMeasurementMeasurementsMeasurementIdDelete(id);
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de supprimer cette mesure."),
                { cause: error }
            );
        }
    },
};
