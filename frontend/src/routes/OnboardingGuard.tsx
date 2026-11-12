import { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";

import { useOnboarding } from "../context/OnboardingContext";

/*
* Cette fonction protège les routes qui nécessitent que l'onboarding soit complété.
* Elle est intégrée dans le système de routage pour rediriger les utilisateurs vers l'onboarding si nécessaire.
*/

export function OnboardingGuard() {
  const {
    status,
    refreshStatus,
    isLoadingStatus,
  } = useOnboarding();

  const [hasChecked, setHasChecked] = useState(false);

  useEffect(() => {
    let isActive = true;

    const checkStatus = async () => {
      try {
        await refreshStatus();
      } catch {
        // L’erreur est déjà exposée par le contexte.
      } finally {
        if (isActive) {
          setHasChecked(true);
        }
      }
    };

    if (!status) {
      void checkStatus();
    } else {
      setHasChecked(true);
    }

    return () => {
      isActive = false;
    };
  }, [refreshStatus, status]);

  if (!hasChecked || isLoadingStatus) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p>Chargement…</p>
      </div>
    );
  }

  if (!status?.is_complete) {
    return (
      <Navigate
        to="/onboarding"
        replace
      />
    );
  }

  return <Outlet />;
}