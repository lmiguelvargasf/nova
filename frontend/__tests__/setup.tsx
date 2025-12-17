// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import "@testing-library/jest-dom";
import type React from "react";
import { vi } from "vitest";

// Mock next/image to render a regular HTML <img> in tests
vi.mock("next/image", () => ({
  __esModule: true,
  default: (props: React.ComponentProps<"img">) => {
    return <img {...props} alt={props.alt ?? "Mocked Image"} />;
  },
}));
