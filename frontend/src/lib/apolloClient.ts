import { ApolloClient, InMemoryCache } from "@apollo/client";

const client = new ApolloClient({
  uri:
    process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT || "http://backend:8000/graphql",
  cache: new InMemoryCache(),
});

export default client;
