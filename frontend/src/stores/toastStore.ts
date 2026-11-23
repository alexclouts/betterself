// src/stores/toastStore.ts
import { create } from "zustand";

/*
 * Messages temporaires (« toasts ») affichés par-dessus la page.
 * Le store est global : un message ajouté juste avant une redirection
 * reste visible sur la page suivante.
 */
export type ToastVariant = "success" | "warning";

export type Toast = {
  id: number;
  message: string;
  variant: ToastVariant;
  // Durée d'affichage en millisecondes avant la disparition automatique.
  duration: number;
};

type ToastState = {
  toasts: Toast[];
  showToast: (message: string, options?: { variant?: ToastVariant; duration?: number }) => void;
  dismissToast: (id: number) => void;
};

let nextId = 1;

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],
  showToast: (message, { variant = "success", duration = 5000 } = {}) =>
    set((state) => ({
      toasts: [...state.toasts, { id: nextId++, message, variant, duration }],
    })),
  dismissToast: (id) =>
    set((state) => ({ toasts: state.toasts.filter((toast) => toast.id !== id) })),
}));
