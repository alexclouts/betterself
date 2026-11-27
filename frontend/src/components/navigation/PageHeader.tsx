import { useEffect, useRef, useState, type ReactNode } from "react";

// Hauteur de l'en-tête : un élément collé sous lui utilise `top-[calc(3.5rem+var(--safe-top))]`.
export const PAGE_HEADER_HEIGHT_CLASS = "h-14";

type PageHeaderProps = {
  onBack: () => void;
  // Texte affiché à côté de la flèche : « Retour », « Retour à mes recettes »…
  backLabel?: string;
  // Titre affiché dans l'en-tête une fois le grand titre défilé; par défaut, le texte du premier <h1> de la page.
  title?: string;
  // Action à droite, par exemple « Modifier ».
  action?: ReactNode;
};

/*
 * Titre de la page affiché dans l'en-tête quand le grand titre (<h1>) est passé
 * sous lui pendant le défilement. Sans <h1>, le titre apparaît dès que la page défile.
 */
function useCollapsedTitle(headerRef: React.RefObject<HTMLElement | null>) {
  const [collapsedTitle, setCollapsedTitle] = useState<string | null>(null);

  useEffect(() => {
    const header = headerRef.current;
    const heading = header?.parentElement?.querySelector("h1");
    if (!header || !heading) return;

    // Le grand titre est « sorti » quand il passe entièrement sous le bas de l'en-tête.
    const headerBottom = Math.round(header.getBoundingClientRect().bottom);
    const observer = new IntersectionObserver(
      ([entry]) => {
        setCollapsedTitle(entry.isIntersecting ? null : (heading.textContent?.trim() ?? null));
      },
      { rootMargin: `-${headerBottom}px 0px 0px 0px` },
    );
    observer.observe(heading);
    return () => observer.disconnect();
  }, [headerRef]);

  return collapsedTitle;
}

/*
 * En-tête des écrans de saisie : bouton de retour (flèche et texte) à gauche,
 * action facultative à droite. Il reste collé en haut pendant le défilement et
 * reprend alors le titre de la page, en plus petit, si la place le permet.
 * À placer en premier dans un <main className="px-4 py-6"> : il compense ces
 * marges pour toucher le haut de l'écran et couvrir toute la largeur.
 */
export function PageHeader({ onBack, backLabel = "Retour", title, action }: PageHeaderProps) {
  const headerRef = useRef<HTMLElement>(null);
  const collapsedTitle = useCollapsedTitle(headerRef);
  const shownTitle = collapsedTitle !== null ? (title ?? collapsedTitle) : null;

  return (
    <header
      ref={headerRef}
      className={`sticky top-[var(--safe-top)] z-40 -mx-4 -mt-6 grid ${PAGE_HEADER_HEIGHT_CLASS} grid-cols-[auto_1fr_auto] items-center gap-1 bg-[var(--bg)] px-2`}
    >
      <button
        type="button"
        onClick={onBack}
        className="flex h-11 min-w-0 items-center gap-1 rounded-full pr-3 pl-1.5 font-semibold text-muted transition hover:bg-surface-raised hover:text-foreground active:scale-95"
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

      {/* Le titre n'apparaît que s'il reste au moins 6rem de place à côté du bouton. */}
      <div className="@container min-w-0">
        <p
          aria-hidden="true"
          className={`hidden truncate text-left text-base font-semibold text-foreground transition-opacity duration-200 @[6rem]:block ${
            shownTitle ? "opacity-100" : "opacity-0"
          }`}
        >
          {shownTitle ?? " "}
        </p>
      </div>

      <div className="flex justify-end">{action}</div>
    </header>
  );
}
