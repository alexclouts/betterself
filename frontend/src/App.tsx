import { OnboardingProvider } from "./context/OnboardingContext";
import { AppRoutes } from "./routes/AppRoutes";

// Composant principal de l'application BetterSelf.
function App() {
  return (
    <OnboardingProvider>
      <AppRoutes />
    </OnboardingProvider>
  );
}


export default App;