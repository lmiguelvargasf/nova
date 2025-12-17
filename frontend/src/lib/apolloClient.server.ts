import { ApolloClient, HttpLink, InMemoryCache } from "@apollo/client";
import { cache } from "react";

// Wrap the client creation in React cache for automatic deduplication per request
export const getClient = cache(() => {
  return new ApolloClient({
    cache: new InMemoryCache(),
    link: new HttpLink({
      uri:
        process.env.INTERNAL_GRAPHQL_ENDPOINT || "http://backend:8000/graphql",
    }),
  });
});
