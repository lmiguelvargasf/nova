import { Suspense } from "react";
import UserCard from "@/features/users/UserCard.client";
import UserCreator from "@/features/users/UserCreator.client";
import { PreloadQuery } from "@/lib/apollo/client.server";
import { GetUserByIdDocument } from "@/lib/graphql/graphql";

export const dynamic = "force-dynamic";

export default function Home() {
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

            <div className="mt-8 border-t border-slate-200 pt-6 dark:border-white/10">
              <h2 className="text-xl font-semibold">Demo</h2>
              <div className="mt-4 space-y-4">
                <div>
                  <h4 className="text-base font-semibold">Get user (ID: 1)</h4>
                  <div className="mt-3 rounded-lg border border-slate-200 bg-white/80 p-4 dark:border-white/10 dark:bg-black/20">
                    <PreloadQuery
                      query={GetUserByIdDocument}
                      variables={{ userId: "1" }}
                    >
                      <Suspense fallback={<p>Loading user...</p>}>
                        <UserCard userId="1" />
                      </Suspense>
                    </PreloadQuery>
                  </div>
                </div>

                <div>
                  <h4 className="text-base font-semibold">Create user</h4>
                  <div className="mt-4">
                    <UserCreator />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
