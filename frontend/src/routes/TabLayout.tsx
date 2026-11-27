import { Outlet } from "react-router-dom";
import { BottomNav } from "../components/navigation/BottomNav";

/*
 * Mise en page des onglets principaux (accueil, journal, recettes, poids) :
 * la barre de navigation reste fixée en bas pendant le défilement.
 * Les écrans de saisie (ajout, scan, formulaires) n'en font pas partie et
 * gardent tout l'écran.
 */
export function TabLayout() {
  return (
    <>
      {/* Réserve la hauteur de la barre pour que la fin du contenu reste visible. */}
      <div className="flex w-full flex-1 flex-col items-center pb-[calc(5rem+var(--safe-bottom))]">
        <Outlet />
      </div>
      <BottomNav />
    </>
  );
}
