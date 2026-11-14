import { getAuthentication } from "../api/generated/authentication/authentication"
import { getErrorMessage } from "../api/axios";
import { getAccessToken, setAccessToken, clearAccessToken } from "../lib/auth";

export type LoginPayload = {
  email: string;
  password: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export type RegisterPayload = {
  email: string;
  password: string;
};

export type RegisterResponse = {
  id: string;
  email: string;
  is_active: boolean;
};


export const authService = {

    getToken() {
        return getAccessToken();
    },
    setToken(token: string) {
        setAccessToken(token);
    },
    logout() {
        clearAccessToken();
    },

    // Réalise l'appel à l'API pour l'inscription
    async register(payload: RegisterPayload) {
        try {
            const { registerUserAuthRegisterPost } = getAuthentication();
            return await registerUserAuthRegisterPost(payload);
        } catch (error) {
            throw new Error(getErrorMessage(error, "Impossible de créer le compte."));
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
            throw new Error(
                getErrorMessage(error, "Impossible de se connecter.")
            );
        }
    }
};
