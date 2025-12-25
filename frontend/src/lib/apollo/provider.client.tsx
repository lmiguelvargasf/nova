"use client";

import { HttpLink } from "@apollo/client";
import { SetContextLink } from "@apollo/client/link/context";
import {
  ApolloClient,
  ApolloNextAppProvider,
  InMemoryCache,
} from "@apollo/client-integration-nextjs";
import type { ReactNode } from "react";

const endpoint = process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT;
if (!endpoint && process.env.NODE_ENV === "production") {
  throw new Error("NEXT_PUBLIC_GRAPHQL_ENDPOINT is required in production.");
}

function makeClient() {
  const httpLink = new HttpLink({
    uri: endpoint ?? "http://localhost:8000/graphql",
  });

  const authLink = new SetContextLink(({ headers }) => {
    const token = localStorage.getItem("token");
    return {
      headers: {
        ...headers,
        authorization: token ? `Bearer ${token}` : "",
      },
    };
  });

  return new ApolloClient({
    cache: new InMemoryCache(),
    link: authLink.concat(httpLink),
  });
}

export default function ApolloClientProvider({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <ApolloNextAppProvider makeClient={makeClient}>
      {children}
    </ApolloNextAppProvider>
  );
}
