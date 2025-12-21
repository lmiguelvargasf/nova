import { ApolloClient, InMemoryCache } from "@apollo/client/core";
import { HttpLink } from "@apollo/client/link/http";

const endpoint = process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT;
if (!endpoint && process.env.NODE_ENV === "production") {
  throw new Error("NEXT_PUBLIC_GRAPHQL_ENDPOINT is required in production.");
}

const client = new ApolloClient({
  link: new HttpLink({
    uri: endpoint ?? "http://localhost:8000/graphql",
  }),
  cache: new InMemoryCache(),
});

export default client;
