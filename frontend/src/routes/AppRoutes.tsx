// src/routes/AppRoutes.tsx
import { Route, Routes } from "react-router-dom";
import { LoginPage } from "../pages/auth/LoginPage";
import { RegisterPage } from "../pages/auth/RegisterPage";
import { ProtectedRoute } from "../routes/ProtectedRoutes";
import { HomePage } from "../pages/home/HomePage";
import { OnboardingPage } from "../pages/onboarding/OnboardingPage";

export function AppRoutes() {
    return (
        <Routes>
            {/* Route publique pour la page de connexion */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Routes protégées nécessitant une authentification */}
            <Route element={<ProtectedRoute />}>
                <Route path="/" element={<HomePage />} />
                <Route path="/onboarding" element={<OnboardingPage />} />
            </Route>
        </Routes>
    );
}