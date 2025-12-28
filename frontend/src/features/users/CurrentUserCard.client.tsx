"use client";

import { useSuspenseQuery } from "@apollo/client/react";
import { useEffect, useState } from "react";

import { ErrorMessage } from "@/components/ui";
import { useDataSource } from "@/lib/dataSource";
import { GetMeDocument } from "@/lib/graphql/graphql";
import { restGetMe } from "@/lib/restClient";

type RestUser = {
  email: string;
  firstName: string | null;
  lastName: string | null;
};

function CurrentUserCardGraphQL() {
  const { data, error } = useSuspenseQuery(GetMeDocument, {
    errorPolicy: "all",
  });

  if (error) {
    return <ErrorMessage message={error.message} />;
  }

  const user = data?.me;
  if (!user) {
    return <p>Unable to load your profile.</p>;
  }

  return (
    <div className="flex flex-row items-baseline gap-2 text-left text-sm">
      <p className="text-slate-700 dark:text-slate-300">
        Logged in as{" "}
        <span className="font-medium text-black dark:text-white">
          {user.email}
        </span>{" "}
        {user.firstName &&
          user.lastName &&
          `(${user.firstName} ${user.lastName})`}
      </p>
    </div>
  );
}

function CurrentUserCardRest() {
  const [user, setUser] = useState<RestUser | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setErrorMessage(null);
    restGetMe()
      .then((response) => {
        if (!active) return;
        setUser({
          email: response.email,
          firstName: response.first_name,
          lastName: response.last_name,
        });
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
    return <p>Loading profile...</p>;
  }

  if (errorMessage) {
    return <ErrorMessage message={errorMessage} />;
  }

  if (!user) {
    return <p>Unable to load your profile.</p>;
  }

  return (
    <div className="flex flex-row items-baseline gap-2 text-left text-sm">
      <p className="text-slate-700 dark:text-slate-300">
        Logged in as{" "}
        <span className="font-medium text-black dark:text-white">
          {user.email}
        </span>{" "}
        {user.firstName &&
          user.lastName &&
          `(${user.firstName} ${user.lastName})`}
      </p>
    </div>
  );
}

export default function CurrentUserCard() {
  const { mode, ready } = useDataSource();

  if (!ready) {
    return <p>Loading profile...</p>;
  }

  return mode === "rest" ? <CurrentUserCardRest /> : <CurrentUserCardGraphQL />;
}
