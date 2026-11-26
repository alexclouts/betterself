import { useEffect, useState, type ReactNode } from "react";

// Hauteur de l'en-tête : un élément collé sous lui utilise `top-14`.
export const PAGE_HEADER_HEIGHT_CLASS = "h-14";

// Vrai dès que la page a défilé : l'en-tête affiche alors sa bordure.
function useHasScrolled(): boolean {
  const [hasScrolled, setHasScrolled] = useState(() => window.scrollY > 0);

  useEffect(() => {
    const onScroll = () => setHasScrolled(window.scrollY > 0);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return hasScrolled;
}

type PageHeaderProps = {
  onBack: () => void;
  // Texte affiché à côté de la flèche : « Retour », « Retour à mes recettes »…
  backLabel?: string;
  // Titre court, centré; facultatif quand la page a déjà un grand titre.
  title?: string;
  // Action à droite, par exemple « Modifier ».
  action?: ReactNode;
};

/*
 * En-tête des écrans de saisie : bouton de retour (flèche et texte) à gauche, titre et action
 * facultatifs. Il reste collé en haut pendant le défilement. À placer en premier
 * dans un <main className="px-4 py-6"> : il compense ces marges pour toucher le
 * haut de l'écran et couvrir toute la largeur.
 */
export function PageHeader({ onBack, backLabel = "Retour", title, action }: PageHeaderProps) {
  const hasScrolled = useHasScrolled();

  return (
    <header
      className={`sticky top-0 z-40 -mx-4 -mt-6 grid ${PAGE_HEADER_HEIGHT_CLASS} grid-cols-[auto_1fr_auto] items-center gap-2 border-b bg-[var(--bg)] px-2 transition-colors ${
        hasScrolled ? "border-border" : "border-transparent"
      }`}
    >
      <button
        type="button"
        onClick={onBack}
        className="flex h-11 min-w-0 items-center gap-1 rounded-full pr-3 pl-1.5 font-semibold text-secondary transition hover:bg-surface-raised hover:text-secondary-dark active:scale-95"
      >
        <svg
          viewBox="0 0 24 24"
          className="h-6 w-6"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.25"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M15 5l-7 7 7 7" />
        </svg>
        <span className="truncate">{backLabel}</span>
      </button>

      <p className="truncate text-center font-semibold text-foreground">{title}</p>

      <div className="flex justify-end">{action}</div>
    </header>
  );
}
