import type { Meta, StoryObj } from "@storybook/react";

// Create a mock version of UserCard for Storybook
// (The real component requires Apollo context)
function UserCardMock({
  userId,
  email,
  loading,
  error,
  notFound,
}: {
  userId: string;
  email?: string;
  loading?: boolean;
  error?: string;
  notFound?: boolean;
}) {
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

const meta: Meta<typeof UserCardMock> = {
  title: "Features/Users/UserCard",
  component: UserCardMock,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    userId: { control: "text" },
    email: { control: "text" },
    loading: { control: "boolean" },
    error: { control: "text" },
    notFound: { control: "boolean" },
  },
};

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
