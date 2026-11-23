import { OnboardingProvider } from "./context/OnboardingContext";
import { AppRoutes } from "./routes/AppRoutes";
import { Toaster } from "./components/ui/Toaster";

// Composant principal de l'application BetterSelf.
function App() {
  return (
    <OnboardingProvider>
      <AppRoutes />
      {/* Pop-ups temporaires, visibles sur toutes les pages. */}
      <Toaster />
    </OnboardingProvider>
  );
}


export default App;