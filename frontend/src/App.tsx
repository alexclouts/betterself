import { Routes, Route } from "react-router-dom";
import { LoginPage } from "./pages/auth/LoginPage";
import { RegisterPage } from "./pages/auth/RegisterPage";
import { HomePage } from "./pages/home/HomePage";
import { OnboardingPage } from "./pages/onboarding/OnboardingPage";
import { ProtectedRoute } from "./routes/ProtectedRoutes";
import { OnboardingGuard } from "./routes/OnboardingGuard";

// Composant principal de l'application BetterSelf.
function App() {
  return (
<Routes>
  <Route
    path="/login"
    element={<LoginPage />}
  />
  <Route
    path="/register"
    element={<RegisterPage />}
  />
{/* Routes protégées par l'authentification */}
<Route element={<ProtectedRoute />}>
  <Route path="/onboarding" element={<OnboardingPage />} />

  {/* Routes nécessitant l'onboarding */}
  <Route element={<OnboardingGuard />}>
    <Route path="/" element={<HomePage />} />
  </Route>
</Route>
</Routes>
  );
}


export default App;