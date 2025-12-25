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
  render(<Home />);
  expect(
    await screen.findByRole("heading", {
      name: /Build and ship faster/i,
    }),
  ).toBeInTheDocument();

  expect(
    screen.getByText(/GraphQL-first full-stack template/i),
  ).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: /Core stack/i }),
  ).toBeInTheDocument();
  // We expect login/signup buttons by default now since no user is logged in
  expect(screen.getByRole("link", { name: /Login/i })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /Sign Up/i })).toBeInTheDocument();
});
