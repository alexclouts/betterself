type SegmentedControlProps<T extends string> = {
  // Nom du groupe, lu par les lecteurs d'écran.
  label: string;
  options: readonly { value: T; label: string }[];
  value: T;
  onChange: (value: T) => void;
  // Couleur de l'option choisie.
  color?: "primary" | "secondary";
  className?: string;
};

// Choix exclusif entre quelques options, présentées comme une pilule à segments.
export function SegmentedControl<T extends string>({
  label,
  options,
  value,
  onChange,
  color = "primary",
  className = "",
}: SegmentedControlProps<T>) {
  const selectedClass = color === "secondary" ? "bg-secondary text-white" : "bg-primary text-white";

  return (
    <div
      role="group"
      aria-label={label}
      className={`inline-flex rounded-full border border-border p-0.5 text-sm ${className}`}
    >
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          aria-pressed={value === option.value}
          className={`rounded-full px-3 py-0.5 ${
            value === option.value ? selectedClass : "text-muted hover:text-foreground"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
