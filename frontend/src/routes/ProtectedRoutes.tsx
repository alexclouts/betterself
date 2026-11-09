// src/routes/ProtectedRoute.tsx
import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "../stores/authStore";

export function ProtectedRoute() {
    const accessToken = useAuthStore((state) => state.accessToken);

    // Si l'utilisateur n'est pas authentifié, redirige vers la page de connexion.
    if (!accessToken) {
        return <Navigate to="/login" replace />;
    }

    return <Outlet />;
}