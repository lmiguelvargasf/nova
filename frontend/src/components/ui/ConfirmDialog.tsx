interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  confirmTone?: "danger" | "primary";
  isBusy?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

const toneStyles: Record<
  NonNullable<ConfirmDialogProps["confirmTone"]>,
  string
> = {
  danger:
    "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 disabled:opacity-50",
  primary:
    "bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-500 disabled:opacity-50",
};

export function ConfirmDialog({
  isOpen,
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  confirmTone = "primary",
  isBusy = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      aria-describedby="confirm-dialog-description"
    >
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
        <div className="space-y-2">
          <h2
            id="confirm-dialog-title"
            className="text-lg font-semibold text-slate-900"
          >
            {title}
          </h2>
          <p id="confirm-dialog-description" className="text-sm text-slate-600">
            {description}
          </p>
        </div>
        <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={onCancel}
            disabled={isBusy}
            className="inline-flex items-center justify-center rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isBusy}
            className={`inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 ${toneStyles[confirmTone]}`}
          >
            {isBusy ? "Working..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
