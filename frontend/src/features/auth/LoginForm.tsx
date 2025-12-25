"use client";

import { useMutation } from "@apollo/client/react";
import { useState } from "react";

import { ErrorMessage } from "@/components/ui";
import { LoginDocument } from "@/lib/graphql/graphql";

export default function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [login, { loading, error }] = useMutation(LoginDocument);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await login({
        variables: { email, password },
      });
      const token = result.data?.login.token;
      const user = result.data?.login.user;
      if (token && user) {
        localStorage.setItem("token", token);
        localStorage.setItem("userId", user.id);
        // Force a reload or reset apollo store to ensure auth link picks up the token
        // For now, router.push might be enough if we just need to go to home,
        // but Apollo Client might need a reset.
        // Simple way:
        window.location.href = "/";
      }
    } catch {
      // Error handled by error state
    }
  };

  const errorMessage = error?.message;

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
        disabled={loading}
        className="flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
      >
        {loading ? "Logging in..." : "Login"}
      </button>
    </form>
  );
}
