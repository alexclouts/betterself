import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { BarcodeScanner } from "../../components/journal/BarcodeScanner";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import { normalizeBarcode } from "../../lib/barcode";
import { readJournalNavState } from "../../lib/journal";
import { queryKeys } from "../../lib/queryClient";
import { foodService, type BarcodeLookup } from "../../services/foodService";

/*
 * Ajout d'un aliment par son code-barres (scanné ou saisi).
 * - Produit trouvé : on ouvre directement sa page d'ajout au journal (un produit
 *   du catalogue est d'abord importé, comme depuis la recherche).
 * - Code inconnu (ou catalogue indisponible) : on propose de créer l'aliment avec
 *   ce code, pour qu'il soit retrouvé au prochain scan.
 */
export function BarcodeScanPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const location = useLocation();
  // Repas et journée choisis depuis le journal, relayés jusqu'à la page d'ajout.
  const journalNavState = readJournalNavState(location.state);

  // Change à chaque « Scanner un autre produit » : redémarre la caméra.
  const [scanKey, setScanKey] = useState(0);
  const [manualCode, setManualCode] = useState("");
  const [manualError, setManualError] = useState<string | null>(null);

  const lookup = useMutation({
    mutationFn: async (code: string): Promise<{ code: string; lookup: BarcodeLookup }> => {
      const lookup = await foodService.findByBarcode(code);
      if (lookup.status !== "found") return { code, lookup };

      const { result } = lookup;
      if (result.food_id) {
        navigate(`/journal/food/${result.food_id}`, { replace: true, state: journalNavState });
      } else if (result.catalog_code) {
        const food = await foodService.importCatalogProduct(result.catalog_code);
        void queryClient.invalidateQueries({ queryKey: queryKeys.foods.all });
        navigate(`/journal/food/${food.id}`, { replace: true, state: { ...journalNavState, food } });
      }
      return { code, lookup };
    },
  });

  const outcome = lookup.data;
  const notFound = outcome && outcome.lookup.status !== "found" ? outcome : null;
  const isScanning = !lookup.isPending && !notFound && !lookup.error;

  function handleCode(code: string) {
    setManualError(null);
    lookup.mutate(code);
  }

  function handleManualSubmit(event: React.SubmitEvent) {
    event.preventDefault();
    const code = normalizeBarcode(manualCode);
    if (!code) {
      setManualError("Entrez les 8 à 14 chiffres sous le code-barres.");
      return;
    }
    handleCode(code);
  }

  function scanAgain() {
    lookup.reset();
    setManualCode("");
    setScanKey((key) => key + 1);
  }

  function createFood(code: string) {
    navigate("/journal/food/new", { state: { ...journalNavState, barcode: code } });
  }

  return (
    <main className="mx-auto w-full max-w-md px-4 py-6">
      <Button type="button" variant="secondary" onClick={() => navigate(-1)} className="text-sm">
        ← Retour
      </Button>

      <h1>Scanner un code-barres</h1>

      {isScanning && <BarcodeScanner key={scanKey} onDetected={handleCode} />}

      {lookup.isPending && (
        <p className="mt-6 text-center" role="status">
          Recherche du produit {lookup.variables}…
        </p>
      )}

      {lookup.error && (
        <div className="mt-6 space-y-4" role="alert">
          <p className="text-danger">{lookup.error.message}</p>
          <Button type="button" className="w-full font-bold" onClick={scanAgain}>
            Réessayer
          </Button>
        </div>
      )}

      {notFound && (
        <div className="mt-6 space-y-4 rounded-2xl bg-surface p-4" role="status">
          <p className="font-semibold text-foreground">
            {notFound.lookup.status === "unknown"
              ? "Produit inconnu"
              : "Catalogue indisponible pour le moment"}
          </p>
          <p className="text-sm">
            {notFound.lookup.status === "unknown"
              ? `Aucun aliment ne correspond au code ${notFound.code}. Créez-le une fois : il sera reconnu à votre prochain scan.`
              : `Le code ${notFound.code} n’a pas pu être vérifié dans le catalogue. Vous pouvez réessayer plus tard ou créer l’aliment.`}
          </p>
          <Button type="button" className="w-full font-bold" onClick={() => createFood(notFound.code)}>
            Créer cet aliment
          </Button>
          <Button type="button" variant="ghost" className="w-full" onClick={scanAgain}>
            Scanner un autre produit
          </Button>
        </div>
      )}

      {/* Saisie du code : sans caméra, ou si l'étiquette ne se lit pas. */}
      {isScanning && (
        <form onSubmit={handleManualSubmit} className="mt-6 space-y-2 text-left" noValidate>
          <label className="block">
            <span className="text-sm font-medium">Saisissez le code</span>
            <Input
              type="text"
              inputMode="numeric"
              autoComplete="off"
              placeholder="ex. 0055653170259"
              value={manualCode}
              onChange={(event) => setManualCode(event.target.value)}
              className="mt-1"
              aria-invalid={manualError !== null}
            />
          </label>
          {manualError && <p className="text-sm text-danger">{manualError}</p>}
          <Button
            type="submit"
            variant="secondary"
            className="w-full disabled:cursor-not-allowed disabled:opacity-50 mt-2"
            disabled={manualCode.trim() === ""}
          >
            Rechercher
          </Button>
        </form>
      )}
    </main>
  );
}
