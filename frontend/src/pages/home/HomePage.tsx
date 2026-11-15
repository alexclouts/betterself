import { useNavigate } from "react-router-dom";
import Button from "../../components/ui/Button";
import { DailySummaryCard } from "../../components/journal/DailySummaryCard";
import { useJournalDay } from "../../hooks/useJournalDay";
import { todayKey } from "../../lib/date";
import { authService } from "../../services/authService";


export function HomePage() {
    const navigate = useNavigate();
    // Résumé de la journée en cours.
    const { totals, target, isLoading, error } = useJournalDay(todayKey());

    function handleLogout() {
        authService.logout();
        navigate("/login", { replace: true });
    }

    return (
    <div>
      <header>
        <h1>Welcome to the Home Page</h1>

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

      <div className="mt-4 flex flex-col gap-2">
        <Button onClick={() => navigate("/journal")}>
          Mon journal
        </Button>
        <Button onClick={() => navigate("/journal/add")}>
          Ajouter un aliment
        </Button>
      </div>
    </div>
    );
}