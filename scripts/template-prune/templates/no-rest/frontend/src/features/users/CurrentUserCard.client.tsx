"use client";

import { useSuspenseQuery } from "@apollo/client/react";

import { ErrorMessage } from "@/components/ui";
import { GetMeDocument } from "@/lib/graphql/graphql";

export default function CurrentUserCard() {
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
        <span className="font-medium text-black dark:text-white">{user.email}</span>{" "}
        {user.firstName && user.lastName && `(${user.firstName} ${user.lastName})`}
      </p>
    </div>
  );
}
