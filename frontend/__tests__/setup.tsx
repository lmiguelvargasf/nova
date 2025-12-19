// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import "@testing-library/jest-dom";
import type React from "react";

// Mock next/image to render a regular HTML <img> in tests
vi.mock("next/image", () => ({
  __esModule: true,
  default: (props: React.ComponentProps<"img">) => {
    // biome-ignore lint/performance/noImgElement: next/image is intentionally mocked to a plain <img> in tests
    return <img {...props} alt={props.alt ?? "Mocked Image"} />;
  },
}));
