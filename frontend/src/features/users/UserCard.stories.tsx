import type { Meta, StoryObj } from "@storybook/react";

interface UserCardUIProps {
  userId: string;
  email?: string;
  loading?: boolean;
  error?: string;
  notFound?: boolean;
}

function UserCardUI({
  userId,
  email,
  loading,
  error,
  notFound,
}: UserCardUIProps) {
  if (loading) {
    return <p>Loading user...</p>;
  }

  if (error) {
    return <p className="text-red-500">Error: {error}</p>;
  }

  if (notFound) {
    return <p>User with ID {userId} is not created or could not be found.</p>;
  }

  return (
    <div className="text-sm">
      <p>
        <strong>Email:</strong> {email}
      </p>
    </div>
  );
}

const meta = {
  title: "Features/Users/UserCard",
  component: UserCardUI,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    userId: { control: "text", description: "The user ID to display" },
    email: { control: "text", description: "User email address" },
    loading: { control: "boolean", description: "Show loading state" },
    error: { control: "text", description: "Error message to display" },
    notFound: { control: "boolean", description: "Show not found state" },
  },
} satisfies Meta<typeof UserCardUI>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    userId: "1",
    email: "user@example.com",
  },
};

export const Loading: Story = {
  args: {
    userId: "1",
    loading: true,
  },
};

export const NotFound: Story = {
  args: {
    userId: "999",
    notFound: true,
  },
};

export const WithError: Story = {
  args: {
    userId: "1",
    error: "Failed to fetch user data",
  },
};
