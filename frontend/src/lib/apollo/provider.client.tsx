"use client";

import { HttpLink } from "@apollo/client";
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
  return new ApolloClient({
    cache: new InMemoryCache(),
    link: new HttpLink({
      uri: endpoint ?? "http://localhost:8000/graphql",
    }),
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
