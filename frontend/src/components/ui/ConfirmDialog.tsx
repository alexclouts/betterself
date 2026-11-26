import { useEffect, useRef } from "react";
import Button from "./Button";

type ConfirmDialogProps = {
  open: boolean;
  title: string;
  message: string;
  confirmLabel: string;
  cancelLabel: string;
  onConfirm: () => void;
  onCancel: () => void;
};

/*
 * Boîte de dialogue modale de confirmation (élément <dialog> natif :
 * focus piégé, Échap pour annuler). L'action par défaut est l'annulation.
 */
export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel,
  cancelLabel,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby="confirm-dialog-title"
      // Échap ferme le dialogue : on le traite comme une annulation.
      onCancel={(event) => {
        event.preventDefault();
        onCancel();
      }}
      className="m-auto w-[calc(100%-2rem)] max-w-sm rounded-2xl bg-surface-overlay p-6 text-left text-foreground shadow-lg backdrop:bg-black/40"
    >
      <h2 id="confirm-dialog-title" className="mt-0 text-left text-xl">
        {title}
      </h2>
      <p className="mt-2">{message}</p>
      <div className="mt-6 grid grid-cols-2 gap-2">
        <Button type="button" variant="ghost" onClick={onConfirm} className="font-semibold text-danger">
          {confirmLabel}
        </Button>
        <Button type="button" onClick={onCancel} className="font-bold" autoFocus>
          {cancelLabel}
        </Button>
      </div>
    </dialog>
  );
}
