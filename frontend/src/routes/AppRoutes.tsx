// src/routes/AppRoutes.tsx
import { Route, Routes } from "react-router-dom";
import { LoginPage } from "../pages/auth/LoginPage";
import { RegisterPage } from "../pages/auth/RegisterPage";
import { ProtectedRoute } from "../routes/ProtectedRoutes";
import { OnboardingGuard } from "../routes/OnboardingGuard";
import { HomePage } from "../pages/home/HomePage";
import { OnboardingPage } from "../pages/onboarding/OnboardingPage";
// import { FoodJournalPage } from "../pages/journal/FoodJournalPage";
import { FoodSearchPage } from "../pages/journal/FoodSearchPage";
import { FoodAddPage } from "../pages/journal/FoodAddPage";
import { FoodCreatePage } from "../pages/journal/FoodCreatePage";

export function AppRoutes() {
    return (
        <Routes>
            {/* Route publique pour la page de connexion */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Routes protégées nécessitant une authentification */}
            <Route element={<ProtectedRoute />}>
                <Route path="/onboarding" element={<OnboardingPage />} />
                
                <Route element={<OnboardingGuard />}>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/journal/add" element={<FoodSearchPage />} />
                    <Route path="/journal/food/new" element={<FoodCreatePage />} />
                    <Route path="/journal/food/:id" element={<FoodAddPage />} />
                </Route>
                
            </Route>
        </Routes>
    );
}