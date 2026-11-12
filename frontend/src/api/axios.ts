import axios, { type AxiosRequestConfig } from "axios";
import { getAccessToken } from "../lib/auth";

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