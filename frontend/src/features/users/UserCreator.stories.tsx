import type { Meta, StoryObj } from "@storybook/react";

interface CreatedUser {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
}

interface UserCreatorUIProps {
  loading?: boolean;
  error?: string;
  createdUser?: CreatedUser;
  onCreateClick?: () => void;
}

function UserCreatorUI({
  loading,
  error,
  createdUser,
  onCreateClick,
}: UserCreatorUIProps) {
  return (
    <div className="space-y-3">
      <button
        type="button"
        onClick={onCreateClick}
        disabled={loading}
        className="rounded-md border border-black/12 px-3 py-2 text-sm font-medium hover:bg-black/4 disabled:opacity-60 dark:border-white/20 dark:hover:bg-white/8"
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

const meta = {
  title: "Features/Users/UserCreator",
  component: UserCreatorUI,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    loading: { control: "boolean", description: "Show loading state" },
    error: { control: "text", description: "Error message to display" },
    createdUser: { control: "object", description: "Created user data" },
    onCreateClick: { action: "clicked", description: "Create button handler" },
  },
} satisfies Meta<typeof UserCreatorUI>;

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
