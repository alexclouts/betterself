import { formatDayLabel } from "../../lib/date";

type JournalDayBadgeProps = {
  dayKey: string;
  // Entrée existante (« Consommé ») ou nouvel ajout (« Ajout pour »).
  isEntry: boolean;
  className?: string;
};

/*
 * Journée du journal visée quand ce n'est pas aujourd'hui, en évidence :
 * « Consommé hier », « Ajout pour le mardi 3 novembre »…
 */
export function JournalDayBadge({ dayKey, isEntry, className = "" }: JournalDayBadgeProps) {
  const label = formatDayLabel(dayKey);
  const isRelative = label === "Hier" || label === "Demain";
  const day = isRelative ? label.toLowerCase() : `le ${label.charAt(0).toLowerCase()}${label.slice(1)}`;

  return (
    <p
      className={`inline-flex items-center gap-1.5 rounded-full bg-surface px-3 py-1 text-sm text-foreground ${className}`}
    >
      <svg
        viewBox="0 0 24 24"
        className="h-4 w-4 shrink-0 text-muted"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <rect x="3" y="5" width="18" height="16" rx="2" />
        <path d="M3 10h18M8 3v4M16 3v4" />
      </svg>
      <span>
        {isEntry ? "Consommé" : "Ajout pour"} <strong className="font-semibold">{day}</strong>
      </span>
    </p>
  );
}
