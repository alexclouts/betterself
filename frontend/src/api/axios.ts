import axios, { type AxiosRequestConfig } from "axios";
import { getAccessToken } from "../lib/auth";
import { useAuthStore } from "../stores/authStore";

// Type représentant le détail d'une erreur renvoyée par l'API.
type ApiErrorDetail = {
  detail?: string | Array<{ msg?: string }>;
};

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Intercepteur pour ajouter le token d'accès aux requêtes sortantes.
api.interceptors.request.use((config) => {
  const token = getAccessToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercepteur de réponse : un 401 sur une requête authentifiée signifie que le
// token est invalide ou expiré. On vide l'authentification, ce qui renvoie
// l'utilisateur vers /login via ProtectedRoute.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      axios.isAxiosError(error) &&
      error.response?.status === 401 &&
      error.config?.headers?.Authorization
    ) {
      useAuthStore.getState().clearAuth();
    }
    return Promise.reject(error);
  },
);


// Fonction attendue par Orval : retourne directement les données.
export const customInstance = <T>(
  config: AxiosRequestConfig,
  options?: AxiosRequestConfig
): Promise<T> => {
  return api({
    ...config,
    ...options,
  }).then((response) => response.data as T);
};


/**
 * Récupère le message d'erreur à partir d'une erreur Axios.
 * @param error L'erreur à analyser.
 * @param fallback Message par défaut si aucun détail n'est disponible.
 * @returns Le message d'erreur.
 */
export function getErrorMessage(
  error: unknown,
  fallback: string
): string {
  if (axios.isAxiosError<ApiErrorDetail>(error)) {
    const detail = error.response?.data?.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      const firstMessage = detail[0]?.msg;

      if (firstMessage) {
        return firstMessage;
      }
    }
  }
  return fallback;
}