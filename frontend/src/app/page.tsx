"use client";

import { useApolloClient } from "@apollo/client/react";
import Link from "next/link";
import { Suspense, useEffect, useState } from "react";
import { Toast } from "@/components/ui";
import CurrentUserCard from "@/features/users/CurrentUserCard.client";
import UsersPaginationCard, {
  UsersPaginationSkeleton,
} from "@/features/users/UsersPaginationCard.client";
import { useDataSource } from "@/lib/dataSource";

export default function Home() {
  const [userId, setUserId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const client = useApolloClient();
  const { mode, setMode } = useDataSource();

  useEffect(() => {
    const storedUserId = localStorage.getItem("userId");
    setUserId(storedUserId);
    const message = sessionStorage.getItem("toastMessage");
    if (message) {
      setToastMessage(message);
      sessionStorage.removeItem("toastMessage");
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    if (!toastMessage) return undefined;
    const timeout = window.setTimeout(() => {
      setToastMessage(null);
    }, 3000);
    return () => window.clearTimeout(timeout);
  }, [toastMessage]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    client.clearStore();
    setUserId(null);
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center p-10 text-center">
        Loading...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-linear-to-b from-slate-50 via-white to-slate-100 text-slate-900 dark:from-slate-950 dark:via-slate-900 dark:to-black dark:text-slate-50 font-(family-name:--font-geist-sans)">
      {toastMessage ? <Toast message={toastMessage} tone="success" /> : null}
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-10 px-6 py-12 sm:px-10 sm:py-16">
        <header className="flex flex-col gap-5">
          <p className="text-sm font-semibold uppercase tracking-[0.32em] text-slate-500 sm:text-base">
            Nova 🌟
          </p>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
            Build and ship faster
          </h1>
          <p className="max-w-2xl text-base text-slate-600 sm:text-lg dark:text-slate-300">
            Nova is a GraphQL-first full-stack template for fast PoCs that
            evolve smoothly into clean, scalable, production-ready MVPs, without
            rewrites.
          </p>
        </header>

        <section className="grid gap-6">
          <div className="rounded-2xl border border-slate-200 bg-white/70 p-6 shadow-sm backdrop-blur dark:border-white/10 dark:bg-white/5">
            <div className="flex flex-col gap-3">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <h2 className="text-xl font-semibold">Registration timeline</h2>
                <div className="flex items-center gap-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                  <span>Data source</span>
                  <div className="inline-flex rounded-full border border-slate-200 bg-white/70 p-1 text-[11px] font-semibold tracking-wide text-slate-600 dark:border-white/10 dark:bg-white/5 dark:text-slate-300">
                    <button
                      type="button"
                      aria-pressed={mode === "graphql"}
                      onClick={() => setMode("graphql")}
                      className={`rounded-full px-3 py-1 transition ${
                        mode === "graphql"
                          ? "bg-slate-900 text-white dark:bg-white dark:text-slate-900"
                          : "hover:bg-slate-100 dark:hover:bg-white/10"
                      }`}
                    >
                      GraphQL
                    </button>
                    <button
                      type="button"
                      aria-pressed={mode === "rest"}
                      onClick={() => setMode("rest")}
                      className={`rounded-full px-3 py-1 transition ${
                        mode === "rest"
                          ? "bg-slate-900 text-white dark:bg-white dark:text-slate-900"
                          : "hover:bg-slate-100 dark:hover:bg-white/10"
                      }`}
                    >
                      REST
                    </button>
                  </div>
                </div>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Browse sign-ups in chronological order, five at a time.
              </p>
            </div>

            <div className="mt-6 grid gap-4 lg:grid-cols-[minmax(0,1fr)_300px]">
              <div className="rounded-lg border border-slate-200 bg-white/80 p-4 dark:border-white/10 dark:bg-black/20">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                  Sign-up order
                </p>
                <div className="mt-4">
                  {userId ? (
                    <Suspense fallback={<UsersPaginationSkeleton />}>
                      <UsersPaginationCard />
                    </Suspense>
                  ) : (
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      Sign in to browse the registration timeline.
                    </p>
                  )}
                </div>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white/80 p-4 dark:border-white/10 dark:bg-black/20">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                  Your session
                </p>
                <div className="mt-4 flex flex-col gap-4">
                  {userId ? (
                    <>
                      <Suspense fallback={<p>Loading profile...</p>}>
                        <CurrentUserCard />
                      </Suspense>
                      <div className="flex flex-wrap items-center gap-3">
                        <Link
                          href="/profile"
                          className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
                        >
                          Update info
                        </Link>
                        <button
                          type="button"
                          onClick={handleLogout}
                          className="rounded-md bg-red-600 px-6 py-2 text-sm font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                        >
                          Logout
                        </button>
                      </div>
                    </>
                  ) : (
                    <>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        Log in to manage your profile and settings.
                      </p>
                      <div className="flex flex-wrap gap-3">
                        <Link
                          href="/login"
                          className="rounded-md bg-indigo-600 px-6 py-3 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                        >
                          Login
                        </Link>
                        <Link
                          href="/register"
                          className="rounded-md border border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
                        >
                          Sign Up
                        </Link>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
