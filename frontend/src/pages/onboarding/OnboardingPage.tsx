import { useEffect } from "react";
import { useNavigate } from "react-router";

import { useOnboarding, type OnboardingStep } from "../../context/OnboardingContext";

import { ProfileStep } from "../../components/onboarding/ProfileStep";
import { GoalStep } from "../../components/onboarding/GoalStep";
import { ReviewStep } from "../../components/onboarding/ReviewStep";


// Définition des étapes de l'onboarding
const steps: OnboardingStep[] = [
    "profile",
    "goal",
    "review",
];


export function OnboardingPage() {
  const navigate = useNavigate();

  const {
    status,
    currentStep,
    setCurrentStep,
    isLoadingStatus,
    isSubmitting,
    error,
    refreshStatus,
  } = useOnboarding();

  useEffect(() => {
    if (status?.is_complete) {
      navigate("/", { replace: true });
    }
  }, [status, navigate]);

  if (isLoadingStatus) {
    return (
      <div className="onboarding-loading">
        <p>Chargement de votre parcours…</p>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="onboarding-error">
        <p>
          Impossible de récupérer l’état de votre onboarding.
        </p>

        <button
          type="button"
          onClick={() => {
            void refreshStatus();
          }}
        >
          Réessayer
        </button>
      </div>
    );
  }

  // Prochaine étape de l'onboarding
  function handleNext() {
    const currentIndex = steps.indexOf(currentStep);
    const nextStep = steps[currentIndex + 1];

    if (nextStep) {
      setCurrentStep(nextStep);
      return;
    }
    navigate("/", { replace: true });
  }

  // Étape précédente de l'onboarding
  function handleBack() {
    const currentIndex = steps.indexOf(currentStep);

    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1]);
    }
  }

  return (
    <main className="onboarding-page">
      <header className="onboarding-header">
        <h1>Configuration de votre profil</h1>

        <p>
          Étape {steps.indexOf(currentStep) + 1} sur {steps.length}
        </p>
      </header>

      {error ? (
        <p className="onboarding-error" role="alert">
          {error}
        </p>
      ) : null}

      <section className="onboarding-content">
        {currentStep === "profile" ? (
          <ProfileStep
            onNext={handleNext}
            isSubmitting={isSubmitting}
          />
        ) : null}

        {currentStep === "goal" ? (
          <GoalStep
            onBack={handleBack}
            onNext={handleNext}
            isSubmitting={isSubmitting}
          />
        ) : null}

        {currentStep === "review" ? (
          <ReviewStep
            onBack={handleBack}
            onFinish={async () => {
              const nextStatus = await refreshStatus();

              if (nextStatus.is_complete) {
                navigate("/", { replace: true });
              }
            }}
            isSubmitting={isSubmitting}
          />
        ) : null}
      </section>
    </main>
  );
}