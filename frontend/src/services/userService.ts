import { getErrorMessage } from "../api/axios";
import { getUsers } from "../api/generated/endpoints/users/users";
import type { UserProfileRead } from "../api/generated/userProfileRead";

export const userService = {
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
};
