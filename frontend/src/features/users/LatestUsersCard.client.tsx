"use client";

import { useSuspenseQuery } from "@apollo/client/react";
import { useEffect, useState } from "react";

import { ErrorMessage } from "@/components/ui";
import { useDataSource } from "@/lib/dataSource";
import { GetLatestUsersDocument } from "@/lib/graphql/graphql";
import { restGetLatestUsers } from "@/lib/restClient";

type LatestUser = {
  id: string;
  email: string;
  firstName?: string | null;
  lastName?: string | null;
};

const LATEST_USERS_LIMIT = 5;

function getDisplayName(user: LatestUser) {
  const fullName = [user.firstName, user.lastName]
    .filter(Boolean)
    .join(" ")
    .trim();
  return fullName || "Name unavailable";
}

function getInitials(user: LatestUser) {
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

function LatestUsersList({ users }: { users: LatestUser[] }) {
  if (users.length === 0) {
    return (
      <p className="text-sm text-slate-500 dark:text-slate-400">
        No recent registrations yet.
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

function LatestUsersGraphQL() {
  const { data, error } = useSuspenseQuery(GetLatestUsersDocument, {
    variables: { limit: LATEST_USERS_LIMIT },
    errorPolicy: "all",
  });

  if (error) {
    return <ErrorMessage message={error.message} />;
  }

  const users: LatestUser[] = (data?.latestUsers ?? []).map((user) => ({
    id: user.id,
    email: user.email,
    firstName: user.firstName,
    lastName: user.lastName,
  }));

  return <LatestUsersList users={users} />;
}

function LatestUsersRest() {
  const [users, setUsers] = useState<LatestUser[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setErrorMessage(null);
    restGetLatestUsers(LATEST_USERS_LIMIT)
      .then((response) => {
        if (!active) return;
        setUsers(
          response.map((user) => ({
            id: String(user.id),
            email: user.email,
            firstName: user.first_name,
            lastName: user.last_name,
          })),
        );
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
  }, []);

  if (loading) {
    return <p>Loading latest users...</p>;
  }

  if (errorMessage) {
    return <ErrorMessage message={errorMessage} />;
  }

  return <LatestUsersList users={users} />;
}

export default function LatestUsersCard() {
  const { mode, ready } = useDataSource();

  if (!ready) {
    return <p>Loading latest users...</p>;
  }

  return mode === "rest" ? <LatestUsersRest /> : <LatestUsersGraphQL />;
}
