import { useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import type { FoodConsumptionRead } from "../../api/generated/foodConsumptionRead";
import type { MealType } from "../../api/generated/mealType";
import Button from "../../components/ui/Button";
import { DailySummaryCard } from "../../components/journal/DailySummaryCard";
import { useJournalDay } from "../../hooks/useJournalDay";
import { addDays, formatDayLabel, parseDateKey, todayKey } from "../../lib/date";
import {
  formatNutrient,
  MEAL_TYPE_LABELS,
  MEAL_TYPE_ORDER,
  sumNutrients,
} from "../../lib/food";
import { journalService } from "../../services/journalService";

export function FoodJournalPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // La journée affichée est dans l'URL (?date=YYYY-MM-DD) ; aujourd'hui par défaut.
  const requestedDate = searchParams.get("date");
  const dayKey = parseDateKey(requestedDate) ? requestedDate! : todayKey();
  const isToday = dayKey === todayKey();

  const { entries, setEntries, totals, target, isLoading, error, setError } =
    useJournalDay(dayKey);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Regroupe les entrées par repas, dans l'ordre de la journée.
  const entriesByMeal = useMemo(() => {
    const groups = Object.fromEntries(
      MEAL_TYPE_ORDER.map((meal) => [meal, [] as FoodConsumptionRead[]]),
    ) as Record<MealType, FoodConsumptionRead[]>;

    for (const entry of entries) {
      groups[entry.meal_type]?.push(entry);
    }
    for (const meal of MEAL_TYPE_ORDER) {
      groups[meal].sort((a, b) => a.consumed_at.localeCompare(b.consumed_at));
    }
    return groups;
  }, [entries]);

  function goToDay(key: string) {
    if (key === todayKey()) {
      setSearchParams({}, { replace: true });
    } else {
      setSearchParams({ date: key }, { replace: true });
    }
  }

  function handleAdd(mealType: MealType) {
    navigate("/journal/add", { state: { mealType, date: dayKey } });
  }

  async function handleDelete(entry: FoodConsumptionRead) {
    if (!window.confirm(`Retirer « ${entry.item_name_snapshot} » du journal ?`)) {
      return;
    }

    setDeletingId(entry.id);
    setError(null);

    try {
      await journalService.deleteEntry(entry.id);
      setEntries((current) => current.filter((item) => item.id !== entry.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Impossible de supprimer cette entrée.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6 text-center">
      <Button
        type="button"
        variant="secondary"
        onClick={() => navigate("/")}
        className="text-sm"
      >
        ← Accueil
      </Button>

      <h1>Journal alimentaire</h1>

      {/* Navigation entre les journées */}
      <nav className="flex items-center justify-between gap-2" aria-label="Choisir la journée">
        <Button
          type="button"
          variant="ghost"
          onClick={() => goToDay(addDays(dayKey, -1))}
          aria-label="Jour précédent"
        >
          ‹
        </Button>

        <div className="text-center">
          <strong className="block text-lg text-foreground">{formatDayLabel(dayKey)}</strong>
          {!isToday && (
            <button
              type="button"
              onClick={() => goToDay(todayKey())}
              className="text-sm text-primary"
            >
              Revenir à aujourd’hui
            </button>
          )}
        </div>

        <Button
          type="button"
          variant="ghost"
          onClick={() => goToDay(addDays(dayKey, 1))}
          disabled={isToday}
          aria-label="Jour suivant"
          className="disabled:opacity-30"
        >
          ›
        </Button>
      </nav>

      {/* Résumé de la journée */}
      <DailySummaryCard totals={totals} target={target} className="mt-6" />

      {error && (
        <p className="mt-4 text-danger" role="alert">
          {error}
        </p>
      )}

      {/* Repas de la journée */}
      {isLoading ? (
        <p className="mt-6">Chargement…</p>
      ) : (
        <div className="mt-6 space-y-6">
          {MEAL_TYPE_ORDER.map((meal) => {
            const mealEntries = entriesByMeal[meal];
            const mealCalories = sumNutrients(mealEntries).calories_kcal;

            return (
              <section key={meal} aria-labelledby={`meal-${meal}`}>
                <div className="flex items-baseline justify-between border-b border-border pb-2">
                  <h3 id={`meal-${meal}`} className="text-lg font-semibold text-foreground">
                    {MEAL_TYPE_LABELS[meal]}
                  </h3>
                  <span className="text-sm text-muted">
                    {formatNutrient(mealCalories, 0)} kcal
                  </span>
                </div>

                {mealEntries.length === 0 ? (
                  <p className="py-3">Aucun aliment.</p>
                ) : (
                  <ul className="divide-y divide-border">
                    {mealEntries.map((entry) => (
                      <li key={entry.id} className="flex items-center gap-3 py-3">
                        <div className="min-w-0 flex-1">
                          <span className="block truncate text-foreground">
                            {entry.item_name_snapshot}
                          </span>
                          <span className="text-sm text-muted">
                            {formatNutrient(entry.quantity_g)} g ·{" "}
                            {formatNutrient(entry.calories_kcal, 0)} kcal
                          </span>
                        </div>

                        <button
                          type="button"
                          onClick={() => void handleDelete(entry)}
                          disabled={deletingId === entry.id}
                          aria-label={`Retirer ${entry.item_name_snapshot}`}
                          className="rounded-full px-3 py-1 text-muted hover:bg-surface-raised hover:text-danger disabled:opacity-50"
                        >
                          ✕
                        </button>
                      </li>
                    ))}
                  </ul>
                )}

                <button
                  type="button"
                  onClick={() => handleAdd(meal)}
                  className="mt-1 text-sm font-semibold text-primary"
                >
                  + Ajouter un aliment
                </button>
              </section>
            );
          })}
        </div>
      )}
    </main>
  );
}
