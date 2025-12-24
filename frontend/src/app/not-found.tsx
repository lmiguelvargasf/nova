import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-linear-to-b from-slate-50 via-white to-slate-100 text-slate-900 dark:from-slate-950 dark:via-slate-900 dark:to-black dark:text-slate-50 font-(family-name:--font-geist-sans)">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-10 px-6 py-12 sm:px-10 sm:py-16">
        <header className="flex flex-col gap-5">
          <p className="text-sm font-semibold uppercase tracking-[0.32em] text-slate-500 sm:text-base">
            404
          </p>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
            Page not found
          </h1>
          <p className="max-w-2xl text-base text-slate-600 sm:text-lg dark:text-slate-300">
            Could not find the requested resource.
          </p>
        </header>

        <div>
          <Link
            href="/"
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-200"
          >
            Go back home
          </Link>
        </div>
      </div>
    </div>
  );
}
