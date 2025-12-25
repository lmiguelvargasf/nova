"use client";

import Link from "next/link";
import { Suspense, useEffect, useState } from "react";

import UserCard from "@/features/users/UserCard.client";

export default function Home() {
  const [userId, setUserId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUserId = localStorage.getItem("userId");
    setUserId(storedUserId);
    setLoading(false);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    setUserId(null);
    window.location.reload();
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
            <div className="flex flex-col gap-2">
              <h2 className="text-xl font-semibold">Core stack</h2>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <div className="rounded-lg border border-slate-200 bg-white/80 p-4 dark:border-white/10 dark:bg-black/20">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                  Backend
                </p>
                <ul className="mt-3 space-y-1 text-sm text-slate-600 dark:text-slate-300">
                  <li>Python</li>
                  <li>uv</li>
                  <li>Litestar</li>
                  <li>Advanced Alchemy</li>
                  <li>PostgreSQL</li>
                </ul>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white/80 p-4 dark:border-white/10 dark:bg-black/20">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                  Frontend
                </p>
                <ul className="mt-3 space-y-1 text-sm text-slate-600 dark:text-slate-300">
                  <li>TypeScript</li>
                  <li>pnpm</li>
                  <li>Next.js</li>
                  <li>Tailwind CSS</li>
                  <li>Storybook</li>
                </ul>
              </div>
              <div className="rounded-lg border border-slate-200 bg-white/80 p-4 dark:border-white/10 dark:bg-black/20">
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                  Tooling
                </p>
                <ul className="mt-3 space-y-1 text-sm text-slate-600 dark:text-slate-300">
                  <li>Docker Compose</li>
                  <li>mise</li>
                  <li>Task</li>
                </ul>
              </div>
            </div>

            <div className="mt-4 pt-8">
              <div className="w-full flex flex-col items-center gap-6">
                {userId ? (
                  <>
                    <div className="w-full text-left">
                      <Suspense fallback={<p>Loading profile...</p>}>
                        <UserCard userId={userId} />
                      </Suspense>
                    </div>
                    <button
                      type="button"
                      onClick={handleLogout}
                      className="rounded-md bg-red-600 px-6 py-2 text-sm font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                    >
                      Logout
                    </button>
                  </>
                ) : (
                  <div className="flex justify-center gap-4">
                    <Link
                      href="/login"
                      className="rounded-md bg-indigo-600 px-6 py-3 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    >
                      Login
                    </Link>
                    <Link
                      href="/register"
                      className="rounded-md border border-gray-300 bg-white px-6 py-3 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
                    >
                      Sign Up
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
