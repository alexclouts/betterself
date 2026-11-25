export type DetailRow = { label: string; value: string };

// Liste « libellé : valeur » des pages de consultation (profil, objectif).
export default function DetailList({ rows }: { rows: DetailRow[] }) {
  return (
    <dl className="space-y-3 text-left">
      {rows.map((row) => (
        <div key={row.label} className="flex justify-between gap-4">
          <dt className="text-muted">{row.label}</dt>
          <dd className="text-right font-medium text-foreground break-words">{row.value}</dd>
        </div>
      ))}
    </dl>
  );
}
