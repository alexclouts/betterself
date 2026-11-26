import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { DailySummaryCard } from "../../components/journal/DailySummaryCard";
import { WeightChart } from "../../components/measurements/WeightChart";
import Card from "../../components/ui/Card";
import { useJournalDay } from "../../hooks/useJournalDay";
import { useMeasurements } from "../../hooks/useMeasurements";
import { todayKey } from "../../lib/date";
import { queryKeys } from "../../lib/queryClient";
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

    return (
    // w-full + max-w-md : largeur fixe, indépendante de la longueur du texte
    // (le #root centre ses enfants et les réduirait sinon à leur contenu).
    <main className="mx-auto w-full max-w-md px-4 py-6">
      {/* Salutation à gauche, accès au profil en haut à droite. */}
      <header className="flex items-center justify-between gap-3">
        <h1 className="min-w-0 break-words text-left text-3xl lg:text-4xl">
          {firstName ? `Bienvenue, ${firstName}` : "Bienvenue"}
        </h1>

        <button
          type="button"
          onClick={() => navigate("/profile")}
          aria-label="Mon profil"
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-surface text-foreground shadow-sm transition hover:bg-surface-raised active:scale-95"
        >
          <svg
            viewBox="0 0 24 24"
            className="h-6 w-6"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <circle cx="12" cy="8" r="4" />
            <path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7" />
          </svg>
        </button>
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
