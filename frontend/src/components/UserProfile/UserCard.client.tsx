"use client";

import { useSuspenseQuery } from "@apollo/client/react";
import {
  GetUserByIdDocument,
  type GetUserByIdQuery,
  type GetUserByIdQueryVariables,
} from "@/lib/graphql/graphql";

export default function UserCard({ userId }: { userId: string }) {
  const { data, error } = useSuspenseQuery<
    GetUserByIdQuery,
    GetUserByIdQueryVariables
  >(GetUserByIdDocument, {
    variables: { userId },
    errorPolicy: "all",
  });

  const isNotFoundError =
    typeof error?.message === "string" && /not found/i.test(error.message);

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
