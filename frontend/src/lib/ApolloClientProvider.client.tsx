"use client";

import { ApolloProvider } from "@apollo/client/react";
import type { ReactNode } from "react";
import client from "@/lib/apolloClient";

export default function ApolloClientProvider({
  children,
}: {
  children: ReactNode;
}) {
  return <ApolloProvider client={client}>{children}</ApolloProvider>;
}
