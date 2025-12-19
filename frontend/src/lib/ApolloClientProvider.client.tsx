"use client";

import { ApolloProvider } from "@apollo/client";
import type React from "react";
import client from "@/lib/apolloClient";

export default function ApolloClientProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return <ApolloProvider client={client}>{children}</ApolloProvider>;
}
