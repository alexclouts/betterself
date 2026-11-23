import { getErrorMessage } from "../api/axios";
import { getUsers } from "../api/generated/endpoints/users/users";
import type { UserProfileRead } from "../api/generated/userProfileRead";
import type { UserProfileUpdate } from "../api/generated/userProfileUpdate";
import type { UserRead } from "../api/generated/userRead";

export const userService = {
    // Récupère le compte de l'utilisateur connecté (courriel).
    async getCurrentUser(): Promise<UserRead> {
        try {
            const { readCurrentUserUsersMeGet } = getUsers();
            return await readCurrentUserUsersMeGet();
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de charger votre compte."),
                { cause: error }
            );
        }
    },

    // Récupère le profil de l'utilisateur connecté (prénom, taille, etc.).
    async getProfile(): Promise<UserProfileRead> {
        try {
            const { getCurrentUserProfileUsersMeProfileGet } = getUsers();
            return await getCurrentUserProfileUsersMeProfileGet();
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible de charger votre profil."),
                { cause: error }
            );
        }
    },

    // Met à jour le profil de l'utilisateur connecté (PUT : tous les champs sont envoyés).
    async updateProfile(payload: UserProfileUpdate): Promise<UserProfileRead> {
        try {
            const { createOrUpdateCurrentUserProfileUsersMeProfilePut } = getUsers();
            return await createOrUpdateCurrentUserProfileUsersMeProfilePut(payload);
        } catch (error) {
            throw new Error(
                getErrorMessage(error, "Impossible d’enregistrer votre profil."),
                { cause: error }
            );
        }
    },
};
