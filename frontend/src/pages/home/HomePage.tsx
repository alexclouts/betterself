import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import Button from "../../components/ui/Button";
import { DailySummaryCard } from "../../components/journal/DailySummaryCard";
import { WeightChart } from "../../components/measurements/WeightChart";
import Card from "../../components/ui/Card";
import { useJournalDay } from "../../hooks/useJournalDay";
import { useMeasurements } from "../../hooks/useMeasurements";
import { todayKey } from "../../lib/date";
import { queryKeys } from "../../lib/queryClient";
import { authService } from "../../services/authService";
import { userService } from "../../services/userService";


export function HomePage() {
    const navigate = useNavigate();
    // Résumé de la journée en cours.
    const { totals, target, isLoading, error } = useJournalDay(todayKey());

    // Profil de l'utilisateur, pour le saluer par son prénom.
    // Sans prénom (chargement, erreur ou champ vide), on affiche seulement « Bienvenue ».
    const profileQuery = useQuery({
        queryKey: queryKeys.profile,
        queryFn: () => userService.getProfile(),
    });
    const firstName = profileQuery.data?.first_name?.trim();

    // Mesures de poids, pour la courbe de progression.
    const weight = useMeasurements();

    function handleLogout() {
        authService.logout();
        navigate("/login", { replace: true });
    }

    return (
    // w-full + max-w-md : largeur fixe, indépendante de la longueur du texte
    // (le #root centre ses enfants et les réduirait sinon à leur contenu).
    <main className="mx-auto w-full max-w-md px-4 py-6">
      <header>
        <h1 className="break-words">
          {firstName ? `Bienvenue, ${firstName}` : "Bienvenue"}
        </h1>

        <div className="mt-4 flex justify-center gap-2">
          <Button onClick={() => navigate("/profile")}>
            Mon profil
          </Button>
          <Button variant="secondary" onClick={handleLogout}>
            Se déconnecter
          </Button>
        </div>
      </header>

      <section className="mt-8" aria-label="Résumé d’aujourd’hui">
        {isLoading ? (
          <p>Chargement de votre journée…</p>
        ) : error ? (
          <p className="text-danger" role="alert">{error}</p>
        ) : (
          <DailySummaryCard totals={totals} target={target} />
        )}
      </section>

      <section className="mt-8" aria-labelledby="weight-heading">
        <Card className="w-full bg-surface">
          <h2 id="weight-heading" className="mt-0 mb-2 text-left text-xl">Mon poids</h2>
          {weight.isLoading ? (
            <p>Chargement de vos mesures…</p>
          ) : weight.error ? (
            <p className="text-danger" role="alert">{weight.error}</p>
          ) : (
            <WeightChart measurements={weight.measurements} />
          )}
        </Card>
      </section>
    </main>
    );
}
