"use client";

import { useSuspenseQuery } from "@apollo/client/react";
import { useEffect, useState } from "react";

import { ErrorMessage } from "@/components/ui";
import { useDataSource } from "@/lib/dataSource";
import { GetUsersPageDocument } from "@/lib/graphql/graphql";
import { restGetUsersPage } from "@/lib/restClient";

type UserEntry = {
  id: string;
  email: string;
  firstName?: string | null;
  lastName?: string | null;
};

const PAGE_SIZE = 5;

function getDisplayName(user: UserEntry) {
  const fullName = [user.firstName, user.lastName]
    .filter(Boolean)
    .join(" ")
    .trim();
  return fullName || "Name unavailable";
}

function getInitials(user: UserEntry) {
  const fullName = [user.firstName, user.lastName]
    .filter(Boolean)
    .join(" ")
    .trim();
  const base = fullName || user.email;
  const parts = base.split(/\s+/).filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }
  return base.slice(0, 2).toUpperCase();
}

function UsersList({ users }: { users: UserEntry[] }) {
  if (users.length === 0) {
    return (
      <p className="text-sm text-slate-500 dark:text-slate-400">
        No registrations yet.
      </p>
    );
  }

  return (
    <ul className="divide-y divide-slate-200/70 dark:divide-white/10">
      {users.map((user) => (
        <li key={user.id} className="flex items-center gap-4 py-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-slate-100 text-xs font-semibold uppercase text-slate-600 dark:border-white/10 dark:bg-white/10 dark:text-slate-200">
            {getInitials(user)}
          </div>
          <div>
            <p className="text-sm font-medium text-slate-900 dark:text-slate-50">
              {getDisplayName(user)}
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {user.email}
            </p>
          </div>
        </li>
      ))}
    </ul>
  );
}

function PaginationFooter(props: {
  pageIndex: number;
  hasNext: boolean;
  isLoading?: boolean;
  onNext: () => void;
  onReset: () => void;
}) {
  const { pageIndex, hasNext, isLoading, onNext, onReset } = props;

  return (
    <div className="flex items-center justify-between border-t border-slate-200/70 pt-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-400 dark:border-white/10">
      <span>Page {pageIndex + 1}</span>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onReset}
          disabled={pageIndex === 0 || isLoading}
          className="rounded-full border border-slate-200 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500 transition enabled:hover:bg-slate-100 disabled:opacity-40 dark:border-white/10 dark:text-slate-300 dark:enabled:hover:bg-white/10"
        >
          Start over
        </button>
        <button
          type="button"
          onClick={onNext}
          disabled={!hasNext || isLoading}
          className="rounded-full border border-slate-200 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500 transition enabled:hover:bg-slate-100 disabled:opacity-40 dark:border-white/10 dark:text-slate-300 dark:enabled:hover:bg-white/10"
        >
          Next
        </button>
      </div>
    </div>
  );
}

function UsersPaginationGraphQL() {
  const [after, setAfter] = useState<string | null>(null);
  const [pageIndex, setPageIndex] = useState(0);
  const { data, error } = useSuspenseQuery(GetUsersPageDocument, {
    variables: { first: PAGE_SIZE, after },
    errorPolicy: "all",
  });

  if (error) {
    return <ErrorMessage message={error.message} />;
  }

  const edges = data?.users.edges ?? [];
  const users: UserEntry[] = edges.map((edge) => ({
    id: edge.node.id,
    email: edge.node.email,
    firstName: edge.node.firstName,
    lastName: edge.node.lastName,
  }));
  const pageInfo = data?.users.pageInfo;
  const nextCursor = pageInfo?.endCursor ?? null;
  const hasNext = pageInfo?.hasNextPage ?? false;

  const handleNext = () => {
    if (!nextCursor) return;
    setAfter(nextCursor);
    setPageIndex((prev) => prev + 1);
  };

  const handleReset = () => {
    setAfter(null);
    setPageIndex(0);
  };

  return (
    <div className="space-y-4">
      <UsersList users={users} />
      <PaginationFooter
        pageIndex={pageIndex}
        hasNext={hasNext}
        onNext={handleNext}
        onReset={handleReset}
      />
    </div>
  );
}

function UsersPaginationRest() {
  const [cursor, setCursor] = useState<string | null>(null);
  const [pageIndex, setPageIndex] = useState(0);
  const [users, setUsers] = useState<UserEntry[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasNext, setHasNext] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setErrorMessage(null);
    restGetUsersPage({ limit: PAGE_SIZE, cursor })
      .then((response) => {
        if (!active) return;
        setUsers(
          response.items.map((user) => ({
            id: String(user.id),
            email: user.email,
            firstName: user.first_name,
            lastName: user.last_name,
          })),
        );
        setNextCursor(response.page.next_cursor);
        setHasNext(response.page.has_next);
      })
      .catch((error: unknown) => {
        if (!active) return;
        const message =
          error instanceof Error ? error.message : "Request failed.";
        setErrorMessage(message);
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [cursor]);

  if (loading) {
    return <p>Loading users...</p>;
  }

  if (errorMessage) {
    return <ErrorMessage message={errorMessage} />;
  }

  const handleNext = () => {
    if (!nextCursor) return;
    setCursor(nextCursor);
    setPageIndex((prev) => prev + 1);
  };

  const handleReset = () => {
    setCursor(null);
    setPageIndex(0);
  };

  return (
    <div className="space-y-4">
      <UsersList users={users} />
      <PaginationFooter
        pageIndex={pageIndex}
        hasNext={hasNext}
        isLoading={loading}
        onNext={handleNext}
        onReset={handleReset}
      />
    </div>
  );
}

export default function UsersPaginationCard() {
  const { mode, ready } = useDataSource();

  if (!ready) {
    return <p>Loading users...</p>;
  }

  return mode === "rest" ? <UsersPaginationRest /> : <UsersPaginationGraphQL />;
}
