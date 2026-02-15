import { render, screen } from "@testing-library/react";
import Home from "@/app/page";

vi.mock("@/features/users/CurrentUserCard.client", () => ({
  default: () => <div>Mocked user card</div>,
}));

vi.mock("@/features/users/UsersPaginationCard.client", () => ({
  default: () => <div>Mocked paginated users</div>,
}));

test("renders the nova home content", async () => {
  render(<Home />);
  expect(
    await screen.findByRole("heading", {
      name: /Build and ship faster/i,
    }),
  ).toBeInTheDocument();

  expect(screen.getByText(/REST-first backend and web template/i)).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: /Registration timeline/i }),
  ).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /Login/i })).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /Sign Up/i })).toBeInTheDocument();
});
