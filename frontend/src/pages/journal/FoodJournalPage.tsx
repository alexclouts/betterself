import { useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
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
import { queryKeys } from "../../lib/queryClient";
import { journalService } from "../../services/journalService";
import { useHasScrolled } from "../../hooks/useHasScrolled";

export function FoodJournalPage() {
  const navigate = useNavigate();
  // La ligne sous la date n'apparaît qu'une fois la page défilée.
  const hasScrolled = useHasScrolled();
  // Recherche des paramètres de l'URL pour déterminer la journée affichée.
  const [searchParams, setSearchParams] = useSearchParams();

  // La journée affichée est dans l'URL (?date=YYYY-MM-DD) ; aujourd'hui par défaut.
  const requestedDate = searchParams.get("date");
  const dayKey = parseDateKey(requestedDate) ? requestedDate! : todayKey();
  const isToday = dayKey === todayKey();

  // État du journal pour la journée affichée.
  const { entries, totals, target, isLoading, error: loadError } = useJournalDay(dayKey);

  const queryClient = useQueryClient();
  
  // Suppression d'une entrée.
  const deleteMutation = useMutation({
    mutationFn: (entryId: string) => journalService.deleteEntry(entryId),
    onSuccess: (_result, entryId) => {
      // Retire l'entrée immédiatement de la journée affichée…
      queryClient.setQueryData<FoodConsumptionRead[]>(
        queryKeys.journal.day(dayKey),
        (current) => current?.filter((item) => item.id !== entryId),
      );
      // …puis marque tout le journal comme périmé (accueil, autres journées).
      void queryClient.invalidateQueries({ queryKey: queryKeys.journal.all });
      // L'aliment peut quitter l'historique proposé par la recherche.
      void queryClient.invalidateQueries({ queryKey: queryKeys.foods.all });
    },
  });

  // Identifiant de l'entrée en cours de suppression, pour désactiver son bouton.
  const deletingId = deleteMutation.isPending ? deleteMutation.variables : null;
  const error = loadError ?? deleteMutation.error?.message ?? null;

  // Regroupe les entrées par repas, dans l'ordre de la journée.
  const entriesByMeal = useMemo(() => {
    const groups = Object.fromEntries(MEAL_TYPE_ORDER.map((meal) => [meal, [] as FoodConsumptionRead[]])) as Record<MealType, FoodConsumptionRead[]>;

    // Initialise les groupes de repas avec des tableaux vides.
    for (const entry of entries) {
      groups[entry.meal_type]?.push(entry);
    }
    // Trie les entrées de chaque repas par ordre chronologique.
    for (const meal of MEAL_TYPE_ORDER) {
      groups[meal].sort((a, b) => a.consumed_at.localeCompare(b.consumed_at));
    }
    return groups;
  }, [entries]);

  // Navigue vers la journée spécifiée.
  function goToDay(key: string) {
    if (key === todayKey()) {
      setSearchParams({}, { replace: true });
    } else {
      setSearchParams({ date: key }, { replace: true });
    }
  }

  // Ajoute un aliment au journal pour le repas spécifié.
  function handleAdd(mealType: MealType) {
    navigate("/journal/add", { state: { mealType, date: dayKey } });
  }

  // Ouvre le détail d'une entrée du journal.
  function handleOpen(entry: FoodConsumptionRead) {
    // Une entrée provient d'un aliment ou d'une recette, chacun avec sa page.
    const path = entry.recipe_id ? `/journal/recipe-entry/${entry.id}` : `/journal/entry/${entry.id}`;
    navigate(path, { state: { entry } });
  }

  // Supprime une entrée du journal, après confirmation.
  function handleDelete(entry: FoodConsumptionRead) {
    if (!window.confirm(`Retirer « ${entry.item_name_snapshot} » du journal ?`)) {
      return;
    }
    deleteMutation.mutate(entry.id);
  }

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6 text-center">
      <h1>Journal alimentaire</h1>

      {/* Navigation entre les journées, collée en haut pendant le défilement,
          avec les calories de la journée toujours visibles. Le fond couvre
          toute la largeur pour masquer le contenu qui passe dessous. */}
      <nav
        className={`sticky top-0 z-30 -mx-4 flex items-center justify-between gap-2 border-b bg-[var(--bg)] px-4 py-2 transition-colors ${
          hasScrolled ? "border-border" : "border-transparent"
        }`}
        aria-label="Choisir la journée"
      >
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
          {!isLoading && (
            <span className="block text-sm text-muted">
              {formatNutrient(totals.calories_kcal, 0)}
              {target ? ` / ${formatNutrient(target.calories_target_kcal, 0)}` : ""} kcal
            </span>
          )}
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
                  <span className="text-sm font-bold text-foreground">
                    {formatNutrient(mealCalories, 0)} kcal
                  </span>
                </div>

                {mealEntries.length === 0 ? (
                  <p className="py-3">Aucun aliment.</p>
                ) : (
                  <ul className="divide-y divide-border">
                    {mealEntries.map((entry) => (
                      <li key={entry.id} className="flex items-center gap-3 py-3">
                        {/* Un clic ouvre la page de l'aliment ou de la recette pour modifier l'entrée. */}
                        <button
                          type="button"
                          onClick={() => {
                            handleOpen(entry);
                          }}
                          className="flex min-w-0 flex-1 items-baseline justify-between gap-3 rounded-lg px-2 py-1 text-left hover:bg-surface-raised"
                        >
                          <span className="min-w-0">
                            <span className="block truncate text-foreground">
                              {entry.item_name_snapshot}
                            </span>
                            <span className="text-sm text-muted">
                              {formatNutrient(entry.quantity_g)} g
                            </span>
                          </span>
                          {/* Calories en évidence, comme le total du repas. */}
                          <span className="shrink-0 text-sm font-bold text-foreground">
                            {formatNutrient(entry.calories_kcal, 0)} kcal
                          </span>
                        </button>

                        <button
                          type="button"
                          onClick={() => {
                            void handleDelete(entry)}
                          }
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
