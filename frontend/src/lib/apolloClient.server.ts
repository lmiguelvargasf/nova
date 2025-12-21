import { ApolloClient, InMemoryCache } from "@apollo/client/core";
import { HttpLink } from "@apollo/client/link/http";
import { cache } from "react";

// Wrap the client creation in React cache for automatic deduplication per request
export const getClient = cache(() => {
  const endpoint = process.env.INTERNAL_GRAPHQL_ENDPOINT;
  if (!endpoint && process.env.NODE_ENV === "production") {
    throw new Error("INTERNAL_GRAPHQL_ENDPOINT is required in production.");
  }

  return new ApolloClient({
    cache: new InMemoryCache(),
    link: new HttpLink({
      uri: endpoint ?? "http://localhost:8000/graphql",
    }),
  });
});
