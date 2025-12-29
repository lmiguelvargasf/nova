"use client";

import { useSuspenseQuery } from "@apollo/client/react";
import { ErrorMessage } from "@/components/ui";
import { GetUserByIdDocument } from "@/lib/graphql/graphql";

function hasErrorCode(error: unknown, code: string): boolean {
  if (!error || typeof error !== "object") return false;
  const graphQLErrors = (error as { graphQLErrors?: unknown[] }).graphQLErrors;
  if (!Array.isArray(graphQLErrors)) return false;
  return graphQLErrors.some(
    (e) =>
      e &&
      typeof e === "object" &&
      (e as { extensions?: { code?: string } }).extensions?.code === code,
  );
}

export default function UserCard({ userId }: { userId: string }) {
  const { data, error } = useSuspenseQuery(GetUserByIdDocument, {
    variables: { userId },
    errorPolicy: "all",
  });

  const isNotFoundError = hasErrorCode(error, "NOT_FOUND");

  if (error && !isNotFoundError) {
    return <ErrorMessage message={error.message} />;
  }

  const user = data?.userById;
  if (!user) {
    return <p>User with ID {userId} is not created or could not be found.</p>;
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
