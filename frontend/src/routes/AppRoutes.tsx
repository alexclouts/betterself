// src/routes/AppRoutes.tsx
import { createBrowserRouter, createRoutesFromElements, Route } from "react-router-dom";
import App from "../App";
import { LoginPage } from "../pages/auth/LoginPage";
import { RegisterPage } from "../pages/auth/RegisterPage";
import { CheckEmailPage } from "../pages/auth/CheckEmailPage";
import { VerifyEmailPage } from "../pages/auth/VerifyEmailPage";
import { ProtectedRoute } from "../routes/ProtectedRoutes";
import { OnboardingGuard } from "../routes/OnboardingGuard";
import { TabLayout } from "../routes/TabLayout";
import { HomePage } from "../pages/home/HomePage";
import { OnboardingPage } from "../pages/onboarding/OnboardingPage";
import { FoodJournalPage } from "../pages/journal/FoodJournalPage";
import { FoodSearchPage } from "../pages/journal/FoodSearchPage";
import { FoodAddPage } from "../pages/journal/FoodAddPage";
import { FoodCreatePage } from "../pages/journal/FoodCreatePage";
import { RecipeAddPage, RecipeEntryEditPage } from "../pages/journal/RecipeAddPage";
import { BarcodeScanPage } from "../pages/journal/BarcodeScanPage";
import { WeightEntryPage } from "../pages/measurements/WeightEntryPage";
import { MeasurementsPage } from "../pages/measurements/MeasurementsPage";
import { ProfilePage } from "../pages/profile/ProfilePage";
import { RecipesPage } from "../pages/recipes/RecipesPage";
import { RecipeNewPage } from "../pages/recipes/RecipeNewPage";
import { RecipeEditPage } from "../pages/recipes/RecipeEditPage";
import { RecipeDetailsPage } from "../pages/recipes/RecipeDetailsPage";

/*
 * Routeur de données : nécessaire pour useBlocker (confirmation avant de
 * quitter un formulaire non enregistré). App sert de mise en page commune.
 */
export const router = createBrowserRouter(
    createRoutesFromElements(
        <Route element={<App />}>
            {/* Route publique pour la page de connexion */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            {/* Validation de l'adresse courriel après l'inscription */}
            <Route path="/check-email" element={<CheckEmailPage />} />
            <Route path="/verify-email" element={<VerifyEmailPage />} />

            {/* Routes protégées nécessitant une authentification */}
            <Route element={<ProtectedRoute />}>
                <Route path="/onboarding" element={<OnboardingPage />} />
                
                <Route element={<OnboardingGuard />}>
                    {/* Onglets principaux, avec la barre de navigation fixe. */}
                    <Route element={<TabLayout />}>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/journal" element={<FoodJournalPage />} />
                        <Route path="/recipes" element={<RecipesPage />} />
                        <Route path="/measurements" element={<MeasurementsPage />} />
                    </Route>

                    {/* Écrans de saisie, en plein écran. */}
                    <Route path="/journal/add" element={<FoodSearchPage />} />
                    <Route path="/journal/scan" element={<BarcodeScanPage />} />
                    <Route path="/journal/food/new" element={<FoodCreatePage />} />
                    <Route path="/journal/food/:id" element={<FoodAddPage />} />
                    <Route path="/journal/entry/:entryId" element={<FoodAddPage />} />
                    <Route path="/journal/recipe/:recipeId" element={<RecipeAddPage />} />
                    <Route path="/journal/recipe-entry/:entryId" element={<RecipeEntryEditPage />} />
                    <Route path="/measurements/new" element={<WeightEntryPage />} />
                    <Route path="/measurements/:measurementId/edit" element={<WeightEntryPage />} />
                    <Route path="/profile" element={<ProfilePage />} />
                    <Route path="/recipes/new" element={<RecipeNewPage />} />
                    <Route path="/recipes/:recipeId" element={<RecipeEditPage />} />
                    <Route path="/recipes/:recipeId/edit" element={<RecipeDetailsPage />} />
                </Route>
                
            </Route>
        </Route>
    )
);