// src/lib/auth.ts

/*
 * Gestion de l'authentification et du token d'accès.
 */
export const ACCESS_TOKEN_STORAGE_KEY = "betterSelf.accessToken";

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);
}

export function setAccessToken(token: string): void {
  localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, token);
}

export function clearAccessToken(): void {
  localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
}