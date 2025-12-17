import Home from "@/app/page";
import { render, screen } from "@testing-library/react";
import type { ImageProps } from "next/image";
import { expect, test, vi } from "vitest";

// Mock the Apollo client module
vi.mock("@/lib/apolloClient.server", () => ({
  getClient: () => ({
    query: () =>
      Promise.resolve({
        data: {
          user: {
            username: "testuser",
          },
        },
      }),
  }),
}));

// Mock Next.js Image component
vi.mock("next/image", () => ({
  default: (
    props: Omit<ImageProps, "width" | "height"> & {
      width?: number;
      height?: number;
    },
  ) => {
    // Ensure alt prop is properly passed through to satisfy a11y requirements
    return (
      <img
        src={props.src as string}
        alt={props.alt}
        data-priority={props.priority ? "true" : undefined}
        width={props.width}
        height={props.height}
      />
    );
  },
}));

test("renders get started text", async () => {
  const HomeComponent = await Home();
  render(HomeComponent);
  expect(screen.getByText(/Get started by editing/i)).toBeInTheDocument();
});
