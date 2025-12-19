import { ApolloClient, InMemoryCache } from "@apollo/client/core";
import { HttpLink } from "@apollo/client/link/http";
import { cache } from "react";

// Wrap the client creation in React cache for automatic deduplication per request
export const getClient = cache(() => {
  return new ApolloClient({
    cache: new InMemoryCache(),
    link: new HttpLink({
      uri:
        process.env.INTERNAL_GRAPHQL_ENDPOINT ||
        "http://localhost:8000/graphql",
    }),
  });
});
