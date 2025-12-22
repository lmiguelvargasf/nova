import { HttpLink } from "@apollo/client";
import {
  ApolloClient,
  InMemoryCache,
  registerApolloClient,
} from "@apollo/client-integration-nextjs";

const endpoint = process.env.INTERNAL_GRAPHQL_ENDPOINT;
if (!endpoint && process.env.NODE_ENV === "production") {
  throw new Error("INTERNAL_GRAPHQL_ENDPOINT is required in production.");
}

export const { getClient, query, PreloadQuery } = registerApolloClient(() => {
  return new ApolloClient({
    cache: new InMemoryCache(),
    link: new HttpLink({
      uri: endpoint ?? "http://localhost:8000/graphql",
    }),
  });
});
