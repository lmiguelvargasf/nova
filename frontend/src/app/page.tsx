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
          <p className="text-xs font-semibold uppercase tracking-[0.4em] text-slate-500">
            Nova starter kit
          </p>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
            Ship a GraphQL-ready product faster.
          </h1>
          <p className="max-w-2xl text-base text-slate-600 sm:text-lg dark:text-slate-300">
            A Litestar and Next.js template with typed GraphQL operations and a
            clean UI baseline. This page doubles as a live sanity check for the
            API wiring.
          </p>
          <div className="flex flex-wrap gap-2 text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300">
            <span className="rounded-full border border-slate-200 px-3 py-1 dark:border-white/20">
              Litestar
            </span>
            <span className="rounded-full border border-slate-200 px-3 py-1 dark:border-white/20">
              GraphQL
            </span>
            <span className="rounded-full border border-slate-200 px-3 py-1 dark:border-white/20">
              Next.js
            </span>
            <span className="rounded-full border border-slate-200 px-3 py-1 dark:border-white/20">
              Tailwind
            </span>
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
          <div className="rounded-2xl border border-slate-200 bg-white/70 p-6 shadow-sm backdrop-blur dark:border-white/10 dark:bg-white/5">
            <div className="flex flex-col gap-2">
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">
                GraphQL
              </p>
              <h2 className="text-xl font-semibold">Live preview</h2>
              <p className="text-sm text-slate-600 dark:text-slate-300">
                Data below is fetched from the backend using generated
                operations.
              </p>
            </div>

            <div className="mt-6 space-y-6">
              <div>
                <h3 className="text-base font-semibold">User data (ID: 1)</h3>
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

              <div className="border-t border-slate-200 pt-5 dark:border-white/10">
                <h3 className="text-base font-semibold">Mutation demo</h3>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                  Create a random user and immediately query the new record.
                </p>
                <div className="mt-4">
                  <UserCreator />
                </div>
              </div>
            </div>
          </div>

          <aside className="rounded-2xl border border-slate-200 bg-slate-50/80 p-6 dark:border-white/10 dark:bg-white/5">
            <h2 className="text-lg font-semibold">Local checklist</h2>
            <ul className="mt-4 space-y-3 text-sm text-slate-600 dark:text-slate-300">
              <li>
                <span className="font-semibold text-slate-700 dark:text-slate-200">
                  Backend:
                </span>{" "}
                run{" "}
                <code className="font-(family-name:--font-geist-mono)">
                  task backend:dev
                </code>
              </li>
              <li>
                <span className="font-semibold text-slate-700 dark:text-slate-200">
                  Frontend:
                </span>{" "}
                run{" "}
                <code className="font-(family-name:--font-geist-mono)">
                  task frontend:dev
                </code>
              </li>
              <li>
                <span className="font-semibold text-slate-700 dark:text-slate-200">
                  GraphQL schema:
                </span>{" "}
                run{" "}
                <code className="font-(family-name:--font-geist-mono)">
                  task frontend:codegen
                </code>
              </li>
              <li>
                <span className="font-semibold text-slate-700 dark:text-slate-200">
                  Endpoint:
                </span>{" "}
                set{" "}
                <code className="font-(family-name:--font-geist-mono)">
                  NEXT_PUBLIC_GRAPHQL_ENDPOINT
                </code>
              </li>
            </ul>
          </aside>
        </section>
      </div>
    </div>
  );
}
