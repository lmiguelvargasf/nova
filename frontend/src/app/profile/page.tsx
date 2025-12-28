"use client";

import { useApolloClient, useMutation, useQuery } from "@apollo/client/react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { ErrorMessage } from "@/components/ui";
import {
  GetUserByIdDocument,
  UpdateCurrentUserDocument,
  type UpdateCurrentUserMutationVariables,
} from "@/lib/graphql/graphql";

type UpdateUserInput = UpdateCurrentUserMutationVariables["userInput"];

type FormState = {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
};

const initialFormState: FormState = {
  firstName: "",
  lastName: "",
  email: "",
  password: "",
};

export default function ProfilePage() {
  const client = useApolloClient();
  const [ready, setReady] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [formState, setFormState] = useState<FormState>(initialFormState);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    const storedUserId = localStorage.getItem("userId");
    setUserId(storedUserId);
    setReady(true);
  }, []);

  const { data, loading, error } = useQuery(GetUserByIdDocument, {
    variables: { userId: userId ?? "" },
    skip: !userId,
  });

  useEffect(() => {
    if (data?.user) {
      setFormState({
        firstName: data.user.firstName ?? "",
        lastName: data.user.lastName ?? "",
        email: data.user.email ?? "",
        password: "",
      });
    }
  }, [data]);

  const [updateCurrentUser, { loading: saving, error: updateError }] =
    useMutation(UpdateCurrentUserDocument);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormState((prev) => ({ ...prev, [id]: value }));
    setSuccessMessage(null);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!userId) return;

    const userInput: UpdateUserInput = {
      firstName: formState.firstName,
      lastName: formState.lastName,
      email: formState.email,
    };

    if (formState.password) {
      userInput.password = formState.password;
    }

    try {
      const result = await updateCurrentUser({
        variables: { userInput },
      });
      if (result.data?.updateCurrentUser) {
        setFormState((prev) => ({ ...prev, password: "" }));
        setSuccessMessage("Profile updated.");
        await client.resetStore();
      }
    } catch {
      // Error handled by error state.
    }
  };

  let content = null;

  if (!ready) {
    content = <p className="text-sm text-slate-600">Loading...</p>;
  } else if (!userId) {
    content = (
      <div className="space-y-3">
        <p className="text-sm text-slate-600">
          You need to be logged in to update your profile.
        </p>
        <Link
          href="/login"
          className="inline-flex rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Go to login
        </Link>
      </div>
    );
  } else if (loading) {
    content = <p className="text-sm text-slate-600">Loading profile...</p>;
  } else if (error) {
    content = <ErrorMessage message={error.message} />;
  } else if (!data?.user) {
    content = (
      <p className="text-sm text-slate-600">We could not load your profile.</p>
    );
  } else {
    content = (
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="firstName"
            className="block text-sm font-medium text-slate-700"
          >
            First name
          </label>
          <input
            id="firstName"
            type="text"
            value={formState.firstName}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
          />
        </div>
        <div>
          <label
            htmlFor="lastName"
            className="block text-sm font-medium text-slate-700"
          >
            Last name
          </label>
          <input
            id="lastName"
            type="text"
            value={formState.lastName}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
          />
        </div>
        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-slate-700"
          >
            Email
          </label>
          <input
            id="email"
            type="email"
            value={formState.email}
            onChange={handleChange}
            required
            className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
          />
        </div>
        <div>
          <label
            htmlFor="password"
            className="block text-sm font-medium text-slate-700"
          >
            New password
          </label>
          <input
            id="password"
            type="password"
            value={formState.password}
            onChange={handleChange}
            className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500"
          />
          <p className="mt-1 text-xs text-slate-500">
            Leave blank to keep your current password.
          </p>
        </div>
        {updateError ? <ErrorMessage message={updateError.message} /> : null}
        {successMessage ? (
          <p className="text-sm text-emerald-600">{successMessage}</p>
        ) : null}
        <button
          type="submit"
          disabled={saving}
          className="inline-flex w-full justify-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {saving ? "Updating..." : "Update info"}
        </button>
      </form>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center py-10">
      <main className="flex w-full flex-1 flex-col items-center justify-center px-6 text-center">
        <div className="w-full max-w-md space-y-6 text-left">
          <div className="space-y-2">
            <h1 className="text-2xl font-semibold text-slate-900">
              Profile settings
            </h1>
            <p className="text-sm text-slate-600">
              Update your account details.
            </p>
          </div>
          {content}
        </div>
        <div className="mt-6">
          <Link
            href="/"
            className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
          >
            {"<- Back to Home"}
          </Link>
        </div>
      </main>
    </div>
  );
}
