"use client";

import { useEffect, useState } from "react";

import { ErrorMessage } from "@/components/ui";
import { restGetUsersPage } from "@/lib/restClient";

type UserEntry = {
  id: string;
  email: string;
  firstName?: string | null;
  lastName?: string | null;
};

const PAGE_SIZE = 5;
const SKELETON_ITEMS = Array.from({ length: PAGE_SIZE }, (_, index) => index);

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

export function UsersPaginationSkeleton() {
  return (
    <ul
      className="divide-y divide-slate-200/70 dark:divide-white/10"
      aria-busy="true"
      aria-live="polite"
    >
      {SKELETON_ITEMS.map((item) => (
        <li key={item} className="flex items-center gap-4 py-3">
          <div className="h-10 w-10 rounded-full bg-slate-200/80 dark:bg-white/10" />
          <div className="flex-1 space-y-2">
            <div className="h-3 w-32 rounded-full bg-slate-200/80 dark:bg-white/10" />
            <div className="h-2 w-44 rounded-full bg-slate-200/60 dark:bg-white/10" />
          </div>
        </li>
      ))}
    </ul>
  );
}

function PaginationFooter(props: {
  pageIndex: number;
  hasNext: boolean;
  hasPrev: boolean;
  isLoading?: boolean;
  onPrev: () => void;
  onNext: () => void;
  onReset: () => void;
}) {
  const { pageIndex, hasNext, hasPrev, isLoading, onPrev, onNext, onReset } =
    props;

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
          First page
        </button>
        <button
          type="button"
          onClick={onPrev}
          disabled={!hasPrev || isLoading}
          className="rounded-full border border-slate-200 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500 transition enabled:hover:bg-slate-100 disabled:opacity-40 dark:border-white/10 dark:text-slate-300 dark:enabled:hover:bg-white/10"
        >
          Previous
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

export default function UsersPaginationCard() {
  const [cursorStack, setCursorStack] = useState<(string | null)[]>([null]);
  const cursor = cursorStack[cursorStack.length - 1] ?? null;
  const pageIndex = cursorStack.length - 1;
  const [users, setUsers] = useState<UserEntry[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasNext, setHasNext] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const hasPrev = cursorStack.length > 1;

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
        const message = error instanceof Error ? error.message : "Request failed.";
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
    return <UsersPaginationSkeleton />;
  }

  if (errorMessage) {
    return <ErrorMessage message={errorMessage} />;
  }

  const handleNext = () => {
    if (!nextCursor) return;
    setCursorStack((prev) => [...prev, nextCursor]);
  };

  const handlePrev = () => {
    setCursorStack((prev) => (prev.length > 1 ? prev.slice(0, -1) : prev));
  };

  const handleReset = () => {
    setCursorStack([null]);
  };

  return (
    <div className="space-y-4">
      <UsersList users={users} />
      <PaginationFooter
        pageIndex={pageIndex}
        hasNext={hasNext}
        hasPrev={hasPrev}
        isLoading={loading}
        onPrev={handlePrev}
        onNext={handleNext}
        onReset={handleReset}
      />
    </div>
  );
}
