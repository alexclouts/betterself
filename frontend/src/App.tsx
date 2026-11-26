import { OnboardingProvider } from "./context/OnboardingContext";
import { Outlet } from "react-router-dom";
import { Toaster } from "./components/ui/Toaster";

// Mise en page commune à toutes les routes de BetterSelf.
function App() {
  return (
    <OnboardingProvider>
      <Outlet />
      {/* Pop-ups temporaires, visibles sur toutes les pages. */}
      <Toaster />
    </OnboardingProvider>
  );
}


export default App;