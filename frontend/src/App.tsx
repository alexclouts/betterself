import { OnboardingProvider } from "./context/OnboardingContext";
import { Outlet } from "react-router-dom";
import { Toaster } from "./components/ui/Toaster";

// Mise en page commune à toutes les routes de BetterSelf.
function App() {
  return (
    <OnboardingProvider>
      {/* Bande opaque sous la barre d'état (encoche) : le contenu qui défile n'y apparaît pas. */}
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-x-0 top-0 z-50 h-[var(--safe-top)] bg-[var(--bg)]"
      />
      <Outlet />
      {/* Pop-ups temporaires, visibles sur toutes les pages. */}
      <Toaster />
    </OnboardingProvider>
  );
}


export default App;