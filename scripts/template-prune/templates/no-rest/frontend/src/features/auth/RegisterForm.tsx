"use client";

import { useApolloClient, useMutation } from "@apollo/client/react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { ErrorMessage } from "@/components/ui";
import { CreateUserDocument } from "@/lib/graphql/graphql";

export default function RegisterForm() {
  const router = useRouter();
  const client = useApolloClient();
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
  });

  const [createUser, { loading, error }] = useMutation(CreateUserDocument);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.id]: e.target.value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await createUser({
        variables: {
          userInput: formData,
        },
      });
      if (result.data?.createUser) {
        const { token, user, reactivated } = result.data.createUser;
        if (token && user) {
          localStorage.setItem("token", token);
          localStorage.setItem("userId", user.id);
          if (reactivated) {
            sessionStorage.setItem("toastMessage", "Account has been reactivated.");
          }
          await client.resetStore();
          router.push("/");
        }
      }
    } catch {
      // Error handled by error state
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-sm mx-auto mt-10">
      <h2 className="text-xl font-bold">Register</h2>
      <div>
        <label
          htmlFor="firstName"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          First Name
        </label>
        <input
          id="firstName"
          type="text"
          value={formData.firstName}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-800"
        />
      </div>
      <div>
        <label
          htmlFor="lastName"
          className="block text-sm font-medium text-gray-700 dark:text-gray-300"
        >
          Last Name
        </label>
        <input
          id="lastName"
          type="text"
          value={formData.lastName}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-800"
        />
      </div>
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
          value={formData.email}
          onChange={handleChange}
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
          value={formData.password}
          onChange={handleChange}
          required
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 dark:border-gray-600 dark:bg-gray-800"
        />
      </div>
      {error?.message ? <ErrorMessage message={error.message} /> : null}
      <button
        type="submit"
        disabled={loading}
        className="flex w-full justify-center rounded-md border border-transparent bg-green-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
      >
        {loading ? "Registering..." : "Register"}
      </button>
    </form>
  );
}
