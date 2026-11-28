import { getAuthentication } from "../api/generated/endpoints/authentication/authentication"
import axios from "axios";
import { getErrorMessage } from "../api/axios";
import { useAuthStore } from "../stores/authStore";

export type LoginPayload = {
  email: string;
  password: string;
};

export type LoginResponse = {
  access_token: string;
  token_type?: string;
};

export type RegisterPayload = {
  email: string;
  password: string;
};

export type MessageResponse = {
  message: string;
};

// Le mot de passe est correct, mais l'adresse courriel n'est pas encore confirmée (403).
export class EmailNotVerifiedError extends Error {}

// Le lien de vérification est valide, mais le mot de passe entré est incorrect (401).
export class IncorrectPasswordError extends Error {}


export const authService = {

    // Passe par le store pour que le localStorage et l'état React restent synchronisés.
    getToken() {
        return useAuthStore.getState().accessToken;
    },
    setToken(token: string) {
        useAuthStore.getState().setAuth(token);
    },
    logout() {
        useAuthStore.getState().clearAuth();
    },

    // Réalise l'appel à l'API pour l'inscription
    async register(payload: RegisterPayload): Promise<MessageResponse> {
        try {
            const { registerUserAuthRegisterPost } = getAuthentication();
            return await registerUserAuthRegisterPost(payload);
        } catch (error) {
            throw new Error(getErrorMessage(error, "Impossible de créer le compte."), { cause: error });
        }
    },

    // Confirme l'adresse courriel avec le jeton reçu dans le lien et le mot de passe du compte.
    // Retourne un jeton d'accès : l'utilisateur est connecté directement.
    async verifyEmail(token: string, password: string): Promise<LoginResponse> {
        try {
            const { verifyEmailAuthVerifyEmailPost } = getAuthentication();
            return await verifyEmailAuthVerifyEmailPost({ token, password });
        } catch (error) {
            if (axios.isAxiosError(error) && error.response?.status === 401) {
                throw new IncorrectPasswordError(
                    getErrorMessage(error, "Le mot de passe est incorrect."),
                    { cause: error },
                );
            }
            throw new Error(getErrorMessage(error, "Impossible de confirmer l'adresse courriel."), { cause: error });
        }
    },

    // Demande un nouveau lien de vérification
    async resendVerification(email: string): Promise<MessageResponse> {
        try {
            const { resendVerificationAuthResendVerificationPost } = getAuthentication();
            return await resendVerificationAuthResendVerificationPost({ email });
        } catch (error) {
            throw new Error(getErrorMessage(error, "Impossible d'envoyer le courriel. Réessayez plus tard."), { cause: error });
        }
    },

    // Fonction de connexion
    async login(
    credentials: LoginPayload
    ): Promise<LoginResponse> {
        try {
            const { loginUserAuthLoginPost } = getAuthentication();
            return await loginUserAuthLoginPost({
                username: credentials.email,
                password: credentials.password
            });
        } catch (error) {
            if (axios.isAxiosError(error) && error.response?.status === 403) {
                throw new EmailNotVerifiedError(
                    getErrorMessage(error, "Veuillez confirmer votre adresse courriel."),
                    { cause: error },
                );
            }
            throw new Error(
                getErrorMessage(error, "Impossible de se connecter."),
                { cause: error },
            );
        }
    }
};
