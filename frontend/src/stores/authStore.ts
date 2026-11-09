// src/stores/authStore.ts
import { create } from "zustand";

// Store pour gérer l'authentification de l'utilisateur (token d'accès).
type AuthState = {
    accessToken: string | null;
    setAuth: (token: string) => void;
    clearAuth: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
    // On initialise le token d'accès à partir du localStorage si disponible.
    accessToken: localStorage.getItem("betterSelf.accessToken"),

    // Méthode pour définir le token d'accès et le stocker dans le localStorage.
    setAuth: (token) => {
        localStorage.setItem("betterSelf.accessToken", token);
        set({ accessToken: token });
    },
    clearAuth: () => {
        localStorage.removeItem("betterSelf.accessToken");
        set({ accessToken: null });
    },
}));