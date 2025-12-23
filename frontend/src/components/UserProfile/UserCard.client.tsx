"use client";

import { useSuspenseQuery } from "@apollo/client/react";
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
    return <p className="text-red-500">Error: {error.message}</p>;
  }

  const user = data?.user;
  if (!user) {
    return <p>User with ID {userId} is not created or could not be found.</p>;
  }

  return (
    <div className="text-sm">
      <p>
        <strong>Email:</strong> {user.email}
      </p>
    </div>
  );
}
