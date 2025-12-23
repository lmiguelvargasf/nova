import type { Meta, StoryObj } from "@storybook/react";

// Create a mock version of UserCreator for Storybook
// (The real component requires Apollo context)
function UserCreatorMock({
  loading,
  error,
  createdUser,
  onCreateClick,
}: {
  loading?: boolean;
  error?: string;
  createdUser?: {
    firstName: string;
    lastName: string;
    email: string;
    id: string;
  };
  onCreateClick?: () => void;
}) {
  return (
    <div className="space-y-3">
      <button
        type="button"
        onClick={onCreateClick}
        disabled={loading}
        className="rounded-md border border-black/[.12] px-3 py-2 text-sm font-medium hover:bg-black/[.04] disabled:opacity-60 dark:border-white/[.2] dark:hover:bg-white/[.08]"
      >
        {loading ? "Creating user..." : "Create random user"}
      </button>
      {error ? <p className="text-sm text-red-500">Error: {error}</p> : null}
      {createdUser ? (
        <div className="text-sm">
          <p>
            <strong>Created:</strong> {createdUser.firstName}{" "}
            {createdUser.lastName} ({createdUser.email})
          </p>
          <p className="text-black/60 dark:text-white/60">
            ID: {createdUser.id}
          </p>
        </div>
      ) : (
        <p className="text-sm text-black/60 dark:text-white/60">
          Click the button to create a user with random data.
        </p>
      )}
    </div>
  );
}

const meta: Meta<typeof UserCreatorMock> = {
  title: "Features/Users/UserCreator",
  component: UserCreatorMock,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    loading: { control: "boolean" },
    error: { control: "text" },
    createdUser: { control: "object" },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
};

export const Loading: Story = {
  args: {
    loading: true,
  },
};

export const Success: Story = {
  args: {
    createdUser: {
      id: "123",
      firstName: "Test",
      lastName: "User-abc123",
      email: "user-abc123@example.com",
    },
  },
};

export const WithError: Story = {
  args: {
    error:
      "Failed to reach GraphQL. Check NEXT_PUBLIC_GRAPHQL_ENDPOINT and that the backend is running.",
  },
};
