"use client";

import { useApolloClient, useMutation, useQuery } from "@apollo/client/react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";

import { ConfirmDialog, ErrorMessage, Toast } from "@/components/ui";
import { useDataSource } from "@/lib/dataSource";
import {
  GetMeDocument,
  SoftDeleteCurrentUserDocument,
  UpdateCurrentUserDocument,
  type UpdateCurrentUserMutationVariables,
} from "@/lib/graphql/graphql";
import {
  AUTH_STATE_CHANGED_EVENT,
  clearStoredAuth,
  restGetMe,
  restSoftDeleteMe,
  restUpdateMe,
} from "@/lib/restClient";

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

type ProfileLayoutProps = {
  content: ReactNode;
  confirmDialog: ReactNode;
  toastMessage: string | null;
};

function ProfileLayout({
  content,
  confirmDialog,
  toastMessage,
}: ProfileLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center py-10">
      {toastMessage ? <Toast message={toastMessage} tone="success" /> : null}
      {confirmDialog}
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

function useToastState() {
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!toastMessage) return undefined;
    const timeout = window.setTimeout(() => {
      setToastMessage(null);
    }, 3000);
    return () => window.clearTimeout(timeout);
  }, [toastMessage]);

  return { toastMessage, setToastMessage };
}

function ProfileGraphQL() {
  const router = useRouter();
  const client = useApolloClient();
  const [ready, setReady] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [formState, setFormState] = useState<FormState>(initialFormState);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const { toastMessage, setToastMessage } = useToastState();

  useEffect(() => {
    const storedUserId = localStorage.getItem("userId");
    setUserId(storedUserId);
    setReady(true);
  }, []);

  const { data, loading, error } = useQuery(GetMeDocument, {
    skip: !userId,
  });

  useEffect(() => {
    if (data?.me) {
      setFormState({
        firstName: data.me.firstName ?? "",
        lastName: data.me.lastName ?? "",
        email: data.me.email ?? "",
        password: "",
      });
    }
  }, [data]);

  const [updateCurrentUser, { loading: saving, error: updateError }] =
    useMutation(UpdateCurrentUserDocument);
  const [softDeleteCurrentUser, { loading: deleting, error: deleteError }] =
    useMutation(SoftDeleteCurrentUserDocument);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormState((prev) => ({ ...prev, [id]: value }));
    setToastMessage(null);
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
        setToastMessage("Profile updated.");
        await client.resetStore();
      }
    } catch {
      // Error handled by error state.
    }
  };

  const handleDeleteConfirm = async () => {
    if (!userId) return;
    try {
      const result = await softDeleteCurrentUser();
      if (result.data?.softDeleteCurrentUser) {
        setShowDeleteDialog(false);
        clearStoredAuth();
        await client.clearStore();
        router.push("/");
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
  } else if (!data?.me) {
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
        <button
          type="submit"
          disabled={saving}
          className="inline-flex w-full justify-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {saving ? "Updating..." : "Update info"}
        </button>
        <div className="border-t border-slate-200 pt-4">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            Danger zone
          </p>
          <p className="mt-2 text-sm text-slate-600">
            This action can be reversed by logging in again.
          </p>
          {deleteError ? <ErrorMessage message={deleteError.message} /> : null}
          <button
            type="button"
            onClick={() => setShowDeleteDialog(true)}
            disabled={deleting}
            className="mt-3 inline-flex w-full justify-center rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {deleting ? "Deleting..." : "Delete account"}
          </button>
        </div>
      </form>
    );
  }

  const confirmDialog = (
    <ConfirmDialog
      isOpen={showDeleteDialog}
      title="Delete account?"
      description="This will remove your account from the app. You can reactivate by logging in again."
      confirmLabel="Delete account"
      confirmTone="danger"
      isBusy={deleting}
      onConfirm={handleDeleteConfirm}
      onCancel={() => setShowDeleteDialog(false)}
    />
  );

  return (
    <ProfileLayout
      content={content}
      confirmDialog={confirmDialog}
      toastMessage={toastMessage}
    />
  );
}

function ProfileRest() {
  const router = useRouter();
  const client = useApolloClient();
  const [ready, setReady] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [formState, setFormState] = useState<FormState>(initialFormState);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [updateError, setUpdateError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const { toastMessage, setToastMessage } = useToastState();

  useEffect(() => {
    const syncUserId = () => {
      setUserId(localStorage.getItem("userId"));
    };

    syncUserId();

    const handleAuthStateChanged = () => {
      syncUserId();
    };

    window.addEventListener(AUTH_STATE_CHANGED_EVENT, handleAuthStateChanged);
    setReady(true);

    return () => {
      window.removeEventListener(
        AUTH_STATE_CHANGED_EVENT,
        handleAuthStateChanged,
      );
    };
  }, []);

  useEffect(() => {
    if (!userId) return;
    setLoading(true);
    setErrorMessage(null);
    restGetMe()
      .then((response) => {
        setFormState({
          firstName: response.first_name ?? "",
          lastName: response.last_name ?? "",
          email: response.email ?? "",
          password: "",
        });
      })
      .catch((error: unknown) => {
        const message =
          error instanceof Error
            ? error.message
            : "Unable to load your profile.";
        setErrorMessage(message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [userId]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormState((prev) => ({ ...prev, [id]: value }));
    setToastMessage(null);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!userId) return;
    setSaving(true);
    setUpdateError(null);
    try {
      await restUpdateMe({
        email: formState.email,
        firstName: formState.firstName,
        lastName: formState.lastName,
        ...(formState.password ? { password: formState.password } : {}),
      });
      setFormState((prev) => ({ ...prev, password: "" }));
      setToastMessage("Profile updated.");
      await client.resetStore();
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Update failed.";
      setUpdateError(message);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!userId) return;
    setDeleting(true);
    setDeleteError(null);
    try {
      const result = await restSoftDeleteMe();
      if (result.deleted) {
        setShowDeleteDialog(false);
        clearStoredAuth();
        await client.clearStore();
        router.push("/");
      }
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "Delete failed.";
      setDeleteError(message);
    } finally {
      setDeleting(false);
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
  } else if (errorMessage) {
    content = <ErrorMessage message={errorMessage} />;
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
        {updateError ? <ErrorMessage message={updateError} /> : null}
        <button
          type="submit"
          disabled={saving}
          className="inline-flex w-full justify-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {saving ? "Updating..." : "Update info"}
        </button>
        <div className="border-t border-slate-200 pt-4">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
            Danger zone
          </p>
          <p className="mt-2 text-sm text-slate-600">
            This action can be reversed by logging in again.
          </p>
          {deleteError ? <ErrorMessage message={deleteError} /> : null}
          <button
            type="button"
            onClick={() => setShowDeleteDialog(true)}
            disabled={deleting}
            className="mt-3 inline-flex w-full justify-center rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {deleting ? "Deleting..." : "Delete account"}
          </button>
        </div>
      </form>
    );
  }

  const confirmDialog = (
    <ConfirmDialog
      isOpen={showDeleteDialog}
      title="Delete account?"
      description="This will remove your account from the app. You can reactivate by logging in again."
      confirmLabel="Delete account"
      confirmTone="danger"
      isBusy={deleting}
      onConfirm={handleDeleteConfirm}
      onCancel={() => setShowDeleteDialog(false)}
    />
  );

  return (
    <ProfileLayout
      content={content}
      confirmDialog={confirmDialog}
      toastMessage={toastMessage}
    />
  );
}

export default function ProfilePage() {
  const { mode, ready } = useDataSource();

  if (!ready) {
    return (
      <ProfileLayout
        content={<p className="text-sm text-slate-600">Loading...</p>}
        confirmDialog={null}
        toastMessage={null}
      />
    );
  }

  return mode === "rest" ? <ProfileRest /> : <ProfileGraphQL />;
}
