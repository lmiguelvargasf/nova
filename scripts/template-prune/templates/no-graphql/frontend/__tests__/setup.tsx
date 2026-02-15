import "@testing-library/jest-dom";
import type React from "react";

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

vi.mock("next/image", () => ({
  __esModule: true,
  default: (props: React.ComponentProps<"img">) => {
    // biome-ignore lint/performance/noImgElement: next/image is intentionally mocked to a plain <img> in tests
    return <img {...props} alt={props.alt ?? "Mocked Image"} />;
  },
}));
