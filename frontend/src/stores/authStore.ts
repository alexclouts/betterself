// src/stores/authStore.ts
import { create } from "zustand";
import { setAccessToken, clearAccessToken, getAccessToken } from "../lib/auth";

// Store pour gérer l'authentification de l'utilisateur (token d'accès).
type AuthState = {
    accessToken: string | null;
    setAuth: (token: string) => void;
    clearAuth: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
    // On initialise le token d'accès à partir du localStorage si disponible.
    accessToken: getAccessToken(),

    // Méthode pour définir le token d'accès et le stocker dans le localStorage.
    setAuth: (token) => {
        setAccessToken(token);
        set({ accessToken: token });
    },
    clearAuth: () => {
        clearAccessToken();
        set({ accessToken: null });
    },
}));