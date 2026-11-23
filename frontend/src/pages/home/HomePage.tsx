import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import Button from "../../components/ui/Button";
import { DailySummaryCard } from "../../components/journal/DailySummaryCard";
import { useJournalDay } from "../../hooks/useJournalDay";
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

        <Button variant="secondary" onClick={handleLogout} className="mt-4">
          Se déconnecter
        </Button>
      </header>

      <section className="mt-6" aria-label="Résumé d’aujourd’hui">
        {isLoading ? (
          <p>Chargement de votre journée…</p>
        ) : error ? (
          <p className="text-danger" role="alert">{error}</p>
        ) : (
          <DailySummaryCard totals={totals} target={target} />
        )}
      </section>

      <div className="mt-6 flex flex-col gap-2">
        <Button className="w-full text-primary font-bold" onClick={() => navigate("/journal")}>
          Mon journal
        </Button>
        <Button className="w-full text-primary font-bold" onClick={() => navigate("/journal/add")}>
          Ajouter un aliment
        </Button>
      </div>
    </main>
    );
}
