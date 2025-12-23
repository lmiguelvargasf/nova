import { render, screen } from "@testing-library/react";

// Mock Apollo's useSuspenseQuery
vi.mock("@apollo/client/react", () => ({
  useSuspenseQuery: vi.fn(() => ({
    data: { user: { id: "1", email: "test@example.com" } },
    error: undefined,
  })),
}));

// Must import after mocking
import UserCard from "./UserCard.client";

describe("UserCard", () => {
  it("renders user email when data is available", () => {
    render(<UserCard userId="1" />);
    expect(screen.getByText("test@example.com")).toBeInTheDocument();
  });

  it("renders not found message when user is null", async () => {
    const { useSuspenseQuery } = await import("@apollo/client/react");
    vi.mocked(useSuspenseQuery).mockReturnValueOnce({
      data: { user: null },
      error: undefined,
    } as ReturnType<typeof useSuspenseQuery>);

    render(<UserCard userId="999" />);
    expect(
      screen.getByText(/is not created or could not be found/i),
    ).toBeInTheDocument();
  });
});
