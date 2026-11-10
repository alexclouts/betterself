import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { OnboardingProvider, useOnboarding } from "../context/OnboardingContext";
import Button from "../components/Button";

const steps = [
    { path: "/onboarding", label: "Objectif" },
    { path: "/onboarding/profile", label: "Profil" },
    { path: "/onboarding/review", label: "Récapitulatif" },
];

function OnboardingContent() {
    const location = useLocation();
    const navigate = useNavigate();
    const { data } = useOnboarding();

    // Conserve l'index de l'étape actuelle en fonction du chemin de l'URL.
    const currentIndex = steps.findIndex(
        (step) => step.path === location.pathname
    );
    // Calcule la progression en pourcentage.
    const progress = ((currentIndex + 1) / steps.length) * 100;

    // Fonction pour naviguer vers l'étape précédente.
    function goToPrevious() {
        if (currentIndex > 0) {
        navigate(steps[currentIndex - 1].path);
        }
    }

    // Fonction pour naviguer vers l'étape suivante.
    function goToNext() {
        if (currentIndex < steps.length - 1) {
        navigate(steps[currentIndex + 1].path);
        }
    }

    return (
        <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
        <div className="mx-auto max-w-xl px-4 py-6">
            <div className="mb-8">
            <p className="mb-2 text-sm">
                Étape {currentIndex + 1} sur {steps.length}
            </p>

            <div
                role="progressbar"
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={Math.round(progress)}
                className="h-2 w-full overflow-hidden rounded-full bg-gray-200"
            >
                <div
                className="h-full rounded-full bg-primary transition-all duration-300"
                style={{ width: `${progress}%` }}
                />
            </div>
            </div>

            <Outlet />

            <div className="mt-8 flex items-center justify-between">
            <Button
                variant="secondary"
                onClick={goToPrevious}
                disabled={currentIndex === 0}
            >
                Précédent
            </Button>

            <Button
                variant="primary"
                onClick={goToNext}
                disabled={currentIndex === steps.length - 1}
            >
                Suivant
            </Button>
            </div>
        </div>
        </div>
    );
}

export function OnboardingLayout() {
  return (
    <OnboardingProvider>
      <OnboardingContent />
    </OnboardingProvider>
  );
}