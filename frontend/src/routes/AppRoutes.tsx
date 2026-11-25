// src/routes/AppRoutes.tsx
import { Route, Routes } from "react-router-dom";
import { LoginPage } from "../pages/auth/LoginPage";
import { RegisterPage } from "../pages/auth/RegisterPage";
import { ProtectedRoute } from "../routes/ProtectedRoutes";
import { OnboardingGuard } from "../routes/OnboardingGuard";
import { HomePage } from "../pages/home/HomePage";
import { OnboardingPage } from "../pages/onboarding/OnboardingPage";
import { FoodJournalPage } from "../pages/journal/FoodJournalPage";
import { FoodSearchPage } from "../pages/journal/FoodSearchPage";
import { FoodAddPage } from "../pages/journal/FoodAddPage";
import { FoodCreatePage } from "../pages/journal/FoodCreatePage";
import { BarcodeScanPage } from "../pages/journal/BarcodeScanPage";
import { WeightEntryPage } from "../pages/measurements/WeightEntryPage";
import { MeasurementsPage } from "../pages/measurements/MeasurementsPage";
import { ProfilePage } from "../pages/profile/ProfilePage";
import { RecipesPage } from "../pages/recipes/RecipesPage";

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
                    <Route path="/journal" element={<FoodJournalPage />} />
                    <Route path="/journal/add" element={<FoodSearchPage />} />
                    <Route path="/journal/scan" element={<BarcodeScanPage />} />
                    <Route path="/journal/food/new" element={<FoodCreatePage />} />
                    <Route path="/journal/food/:id" element={<FoodAddPage />} />
                    <Route path="/journal/entry/:entryId" element={<FoodAddPage />} />
                    <Route path="/measurements" element={<MeasurementsPage />} />
                    <Route path="/measurements/new" element={<WeightEntryPage />} />
                    <Route path="/measurements/:measurementId/edit" element={<WeightEntryPage />} />
                    <Route path="/profile" element={<ProfilePage />} />
                    <Route path="/recipes" element={<RecipesPage />} />
                </Route>
                
            </Route>
        </Routes>
    );
}