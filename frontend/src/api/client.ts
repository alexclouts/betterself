// src/api/client.ts
import { useAuthStore } from "../stores/authStore";

const API_URL = import.meta.env.VITE_API_URL;

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = useAuthStore.getState().accessToken;

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...options.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  if (response.status === 401) {
    useAuthStore.getState().clearAuth();
    throw new Error("UNAUTHENTICATED");
  }

  if (!response.ok) {
    throw new Error(`API_ERROR_${response.status}`);
  }

  return (await response.json()) as T;
}