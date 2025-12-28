interface ToastProps {
  message: string;
  tone?: "success" | "info";
}

const toneStyles: Record<NonNullable<ToastProps["tone"]>, string> = {
  success:
    "bg-emerald-600 text-white ring-emerald-500/40 dark:bg-emerald-500 dark:ring-emerald-400/50",
  info: "bg-slate-900 text-white ring-white/10 dark:bg-slate-100 dark:text-slate-900 dark:ring-slate-300/30",
};

export function Toast({ message, tone = "success" }: ToastProps) {
  return (
    <output
      aria-live="polite"
      className={`fixed left-1/2 top-6 z-50 w-[min(90vw,24rem)] -translate-x-1/2 rounded-full px-4 py-2 text-center text-sm font-medium shadow-lg ring-1 ${toneStyles[tone]}`}
    >
      {message}
    </output>
  );
}
