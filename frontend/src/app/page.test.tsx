import { render, screen } from "@testing-library/react";
import type { ImageProps } from "next/image";
import type { ReactNode } from "react";
import Home from "@/app/page";

// Mock the Apollo client module
vi.mock("@/lib/apollo/client.server", () => ({
  PreloadQuery: ({ children }: { children: ReactNode }) => children,
}));

vi.mock("@/features/users/UserCard.client", () => ({
  default: () => <div>Mocked user card</div>,
}));

vi.mock("@/features/users/UserCreator.client", () => ({
  default: () => <div>Mocked user creator</div>,
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
      // biome-ignore lint/performance/noImgElement: next/image is intentionally mocked to a plain <img> in tests
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
