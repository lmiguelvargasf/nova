import { render, screen } from "@testing-library/react";
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

test("renders the nova home content", async () => {
  const HomeComponent = await Home();
  render(HomeComponent);
  expect(
    screen.getByRole("heading", {
      name: /Build and ship faster/i,
    }),
  ).toBeInTheDocument();
  expect(
    screen.getByText(/GraphQL-first full-stack template/i),
  ).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: /Live preview/i }),
  ).toBeInTheDocument();
  expect(screen.getByText("Mocked user card")).toBeInTheDocument();
  expect(screen.getByText("Mocked user creator")).toBeInTheDocument();
});
