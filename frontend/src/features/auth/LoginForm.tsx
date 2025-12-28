"use client";

import { useApolloClient, useMutation } from "@apollo/client/react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { ErrorMessage } from "@/components/ui";
import { useDataSource } from "@/lib/dataSource";
import { LoginDocument } from "@/lib/graphql/graphql";
import { restLogin } from "@/lib/restClient";

export default function LoginForm() {
  const router = useRouter();
  const client = useApolloClient();
  const { mode } = useDataSource();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [restError, setRestError] = useState<string | null>(null);
  const [restLoading, setRestLoading] = useState(false);

  const [login, { loading, error }] = useMutation(LoginDocument);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (mode === "rest") {
      setRestLoading(true);
      setRestError(null);
      try {
        const result = await restLogin({ email, password });
        localStorage.setItem("token", result.token);
        localStorage.setItem("userId", String(result.user.id));
        if (result.reactivated) {
          sessionStorage.setItem(
            "toastMessage",
            "Account has been reactivated.",
          );
        }
        await client.resetStore();
        router.push("/");
      } catch (error: unknown) {
        const message =
          error instanceof Error ? error.message : "Login failed.";
        setRestError(message);
      } finally {
        setRestLoading(false);
      }
      return;
    }
    try {
      const result = await login({
        variables: { email, password },
      });
      const token = result.data?.login.token;
      const user = result.data?.login.user;
      const reactivated = result.data?.login.reactivated;
      if (token && user) {
        localStorage.setItem("token", token);
        localStorage.setItem("userId", user.id);
        if (reactivated) {
          sessionStorage.setItem(
            "toastMessage",
            "Account has been reactivated.",
          );
        }
        await client.resetStore();
        router.push("/");
      }
    } catch {
      // Error handled by error state
    }
  };

  const errorMessage = mode === "rest" ? restError : error?.message;
  const isLoading = mode === "rest" ? restLoading : loading;

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-sm mx-auto mt-10">
      <h2 className="text-xl font-bold">Login</h2>
      <div>
        <label
          htmlFor="email"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Email
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-800"
        />
      </div>
      <div>
        <label
          htmlFor="password"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-800"
        />
      </div>
      {errorMessage && <ErrorMessage message={errorMessage} />}
      <button
        type="submit"
        disabled={isLoading}
        className="flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
      >
        {isLoading ? "Logging in..." : "Login"}
      </button>
    </form>
  );
}
