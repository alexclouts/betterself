import { Routes, Route } from "react-router-dom";
import { LoginPage } from "./pages/auth/LoginPage";
import { RegisterPage } from "./pages/auth/RegisterPage";
import { HomePage } from "./pages/home/HomePage";
import { OnboardingPage } from "./pages/onboarding/OnboardingPage";
import { ProtectedRoute } from "./routes/ProtectedRoutes";

// Composant principal de l'application BetterSelf.
function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<ProtectedRoute />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
      </Route>

      <Route path="*" element={<LoginPage />} />
    </Routes>
  );
}


export default App;