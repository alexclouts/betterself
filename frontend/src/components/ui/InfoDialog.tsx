import { useEffect, useId, useRef, type ReactNode } from "react";
import Button from "./Button";

type InfoDialogProps = {
  open: boolean;
  title: string;
  children: ReactNode;
  onClose: () => void;
  closeLabel?: string;
};

/*
 * Boîte de dialogue modale d'information, avec un seul bouton pour la fermer
 * (élément <dialog> natif : focus piégé, Échap pour fermer).
 */
export function InfoDialog({ open, title, children, onClose, closeLabel = "Compris" }: InfoDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const titleId = useId();

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby={titleId}
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
      // Un clic sur le fond (hors de la boîte) ferme aussi le dialogue.
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
      className="m-auto w-[calc(100%-2rem)] max-w-sm rounded-2xl bg-surface-overlay p-6 text-left text-foreground shadow-lg backdrop:bg-black/40"
    >
      <h2 id={titleId} className="mt-0 text-left text-xl">
        {title}
      </h2>
      <div className="mt-2 space-y-2 text-base text-foreground [&_p]:text-base [&_p]:text-foreground">
        {children}
      </div>
      <Button type="button" onClick={onClose} className="mt-6 w-full font-bold" autoFocus>
        {closeLabel}
      </Button>
    </dialog>
  );
}
