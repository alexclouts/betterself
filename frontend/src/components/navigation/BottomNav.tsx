import type { ReactNode } from "react";
import { NavLink, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { parseDateKey } from "../../lib/date";

// Icônes au trait, dessinées dans une grille de 24 × 24.
function Icon({ children }: { children: ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-6 w-6"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

const icons = {
  home: (
    <Icon>
      <path d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-4.5v-6h-5v6H5a1 1 0 0 1-1-1z" />
    </Icon>
  ),
  journal: (
    <Icon>
      <rect x="5" y="3.5" width="14" height="17" rx="2" />
      <path d="M9 8.5h6M9 12h6M9 15.5h3.5" />
    </Icon>
  ),
  recipes: (
    <Icon>
      <path d="M3.5 11.5h17a8.5 8.5 0 0 1-17 0z" />
      <path d="M9 8c0-1.5 1-1.5 1-3M14 8c0-1.5 1-1.5 1-3" />
    </Icon>
  ),
  weight: (
    <Icon>
      <rect x="4" y="4" width="16" height="16" rx="3" />
      <path d="M8.5 9.5a4.5 4.5 0 0 1 7 0M12 9.5l1.25-2" />
    </Icon>
  ),
};

type TabProps = {
  to: string;
  label: string;
  icon: ReactNode;
  // Onglet actif seulement sur ce chemin exact (l'accueil « / » préfixe tout).
  end?: boolean;
};

function Tab({ to, label, icon, end = false }: TabProps) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `flex min-w-0 flex-1 flex-col items-center gap-0.5 rounded-xl px-1 py-1.5 text-xs transition ${
          isActive ? "font-semibold text-primary" : "text-muted hover:text-foreground"
        }`
      }
    >
      {icon}
      <span className="truncate">{label}</span>
    </NavLink>
  );
}

/*
 * Barre de navigation fixée en bas de l'écran, toujours visible pendant le défilement.
 * Le bouton central ouvre l'ajout d'un aliment depuis n'importe quel onglet.
 */
export function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  // Depuis le journal d'une autre journée, l'ajout se fait dans cette journée.
  // Le repas est proposé selon l'heure par la page d'ajout.
  function openAdd() {
    const date = location.pathname === "/journal" ? searchParams.get("date") : null;
    navigate("/journal/add", { state: date && parseDateKey(date) ? { date } : undefined });
  }

  return (
    <nav
      aria-label="Navigation principale"
      className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-surface pb-[env(safe-area-inset-bottom)]"
    >
      <div className="mx-auto flex w-full max-w-md items-center gap-1 px-2 py-1">
        <Tab to="/" end label="Accueil" icon={icons.home} />
        <Tab to="/journal" label="Journal" icon={icons.journal} />

        <div className="flex flex-1 justify-center">
          <button
            type="button"
            onClick={openAdd}
            aria-label="Ajouter un aliment"
            className="-mt-6 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-white shadow-lg ring-4 ring-surface transition hover:bg-primary-dark active:scale-95"
          >
            <svg viewBox="0 0 24 24" className="h-7 w-7" fill="none" stroke="currentColor" strokeWidth="2.25" strokeLinecap="round" aria-hidden="true">
              <path d="M12 5v14M5 12h14" />
            </svg>
          </button>
        </div>

        <Tab to="/recipes" label="Recettes" icon={icons.recipes} />
        <Tab to="/measurements" label="Poids" icon={icons.weight} />
      </div>
    </nav>
  );
}
