// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import "@testing-library/jest-dom";
import { resetApolloClientSingletons } from "@apollo/client-integration-nextjs";
import type React from "react";
import { server } from "@/mocks/server";

const makeStorage = (): Storage => {
  const store = new Map<string, string>();
  return {
    clear: () => store.clear(),
    getItem: (key: string) => store.get(key) ?? null,
    key: (index: number) => Array.from(store.keys())[index] ?? null,
    removeItem: (key: string) => {
      store.delete(key);
    },
    setItem: (key: string, value: string) => {
      store.set(key, String(value));
    },
    get length() {
      return store.size;
    },
  };
};

Object.defineProperty(globalThis, "localStorage", {
  configurable: true,
  value: makeStorage(),
});

Object.defineProperty(globalThis, "sessionStorage", {
  configurable: true,
  value: makeStorage(),
});

beforeAll(() => {
  server.listen({ onUnhandledRequest: "warn" });
});

afterEach(() => {
  server.resetHandlers();
});

// Reset Apollo Client singletons between tests (recommended by official docs)
afterEach(resetApolloClientSingletons);

afterAll(() => {
  server.close();
});

// Mock next/image to render a regular HTML <img> in tests
vi.mock("next/image", () => ({
  __esModule: true,
  default: (props: React.ComponentProps<"img">) => {
    // biome-ignore lint/performance/noImgElement: next/image is intentionally mocked to a plain <img> in tests
    return <img {...props} alt={props.alt ?? "Mocked Image"} />;
  },
}));
