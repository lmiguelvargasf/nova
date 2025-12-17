"use client";

import client from "@/lib/apolloClient";
import { ApolloProvider } from "@apollo/client";
import type React from "react";

export default function ApolloClientProvider({
  children,
}: { children: React.ReactNode }) {
  return <ApolloProvider client={client}>{children}</ApolloProvider>;
}
