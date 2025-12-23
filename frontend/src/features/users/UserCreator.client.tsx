"use client";

import { useMutation } from "@apollo/client/react";
import { Suspense, useState } from "react";
import { ErrorMessage } from "@/components/ui";
import UserCard from "@/features/users/UserCard.client";
import {
  CreateUserDocument,
  type CreateUserMutationVariables,
} from "@/lib/graphql/graphql";

type CreateUserInput = CreateUserMutationVariables["userInput"];

function buildRandomUserInput(): CreateUserInput {
  const suffix = Math.random().toString(36).slice(2, 8);
  const stamp = Date.now().toString(36);
  const firstName = "Test";
  const lastName = `User-${suffix}`;

  return {
    email: `user-${stamp}-${suffix}@example.com`,
    password: `ChangeMe-${suffix}!`,
    firstName,
    lastName,
  };
}

export default function UserCreator() {
  const [createdUserId, setCreatedUserId] = useState<string | null>(null);
  const [createUser, { data, loading, error }] = useMutation(
    CreateUserDocument,
    {
      errorPolicy: "all",
    },
  );

  const handleCreate = async () => {
    const userInput = buildRandomUserInput();
    try {
      const result = await createUser({ variables: { userInput } });
      const user = result.data?.createUser;
      if (user) {
        setCreatedUserId(user.id);
      }
    } catch {
      // The hook's `error` state handles display; avoid unhandled rejections.
    }
  };

  const createdUser = data?.createUser;
  const errorMessage =
    error?.message === "Failed to fetch"
      ? "Failed to reach GraphQL. Check NEXT_PUBLIC_GRAPHQL_ENDPOINT and that the backend is running."
      : error?.message;

  return (
    <div className="space-y-3">
      <button
        type="button"
        onClick={handleCreate}
        disabled={loading}
        className="rounded-md border border-black/[.12] px-3 py-2 text-sm font-medium hover:bg-black/[.04] disabled:opacity-60 dark:border-white/[.2] dark:hover:bg-white/[.08]"
      >
        {loading ? "Creating user..." : "Create random user"}
      </button>
      {errorMessage ? <ErrorMessage message={errorMessage} /> : null}
      {createdUser ? (
        <div className="text-sm">
          <p>
            <strong>Created:</strong> {createdUser.firstName}{" "}
            {createdUser.lastName} ({createdUser.email})
          </p>
          <p className="text-black/60 dark:text-white/60">
            ID: {createdUser.id}
          </p>
        </div>
      ) : (
        <p className="text-sm text-black/60 dark:text-white/60">
          Click the button to create a user with random data.
        </p>
      )}
      {createdUserId ? (
        <div className="border-t border-black/[.08] pt-3 dark:border-white/[.14]">
          <p className="text-sm font-semibold">Query created user</p>
          <Suspense fallback={<p className="text-sm">Loading user...</p>}>
            <UserCard userId={createdUserId} />
          </Suspense>
        </div>
      ) : null}
    </div>
  );
}
