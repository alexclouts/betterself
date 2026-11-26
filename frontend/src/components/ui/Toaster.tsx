import { useEffect, useState } from "react";
import { useToastStore, type Toast } from "../../stores/toastStore";

const VARIANT_STYLES = {
  success: { accent: "border-l-primary", icon: "✓", iconColor: "text-primary-ink" },
  warning: { accent: "border-l-warning", icon: "⚠", iconColor: "text-warning" },
  error: { accent: "border-l-danger", icon: "!", iconColor: "text-danger" },
} as const;

// Un message : disparaît seul après `duration`, ou en cliquant sur ×.
function ToastItem({ toast }: { toast: Toast }) {
  const dismissToast = useToastStore((state) => state.dismissToast);
  const [isHovered, setIsHovered] = useState(false);
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    if (isHovered || isFocused) return;
    const timer = setTimeout(() => dismissToast(toast.id), toast.duration);
    return () => clearTimeout(timer);
  }, [toast.id, toast.duration, dismissToast, isHovered, isFocused]);

  const { accent, icon, iconColor } = VARIANT_STYLES[toast.variant];

  return (
    <div
      role={toast.variant === "success" ? "status" : "alert"}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onFocus={() => setIsFocused(true)}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget)) setIsFocused(false);
      }}
      className={`pointer-events-auto flex items-start gap-3 rounded-xl border border-border border-l-4 ${accent} bg-surface-overlay px-4 py-3 text-left text-sm text-foreground shadow-lg animate-[toast-in_200ms_ease-out] motion-reduce:animate-none`}
    >
      <span aria-hidden="true" className={`font-bold ${iconColor}`}>{icon}</span>
      <p className="flex-1 text-sm text-foreground">{toast.message}</p>
      <button
        type="button"
        onClick={() => dismissToast(toast.id)}
        className="-mr-1 rounded px-1 text-muted hover:text-foreground"
        aria-label="Fermer le message"
      >
        ×
      </button>
    </div>
  );
}

// Zone d'affichage des messages, en haut de l'écran. À monter une seule fois (App).
export function Toaster() {
  const toasts = useToastStore((state) => state.toasts);

  return (
    <div
      aria-live="polite"
      className="pointer-events-none fixed inset-x-0 top-[calc(1rem+var(--safe-top))] z-50 mx-auto flex w-full max-w-md flex-col gap-2 px-4"
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} />
      ))}
    </div>
  );
}
