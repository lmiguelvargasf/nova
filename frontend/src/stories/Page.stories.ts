import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "@storybook/test";

import { Page } from "./Page";

const meta = {
  title: "Example/Page",
  component: Page,
  parameters: {
    // More on how to position stories at: https://storybook.js.org/docs/configure/story-layout
    layout: "fullscreen",
  },
} satisfies Meta<typeof Page>;

export default meta;
type Story = StoryObj<typeof meta>;

export const LoggedOut: Story = {};

// More on component testing: https://storybook.js.org/docs/writing-tests/component-testing
export const LoggedIn: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const loginButton = await canvas.findByRole("button", { name: /Log in/i });
    await userEvent.click(loginButton);
    await expect(
      canvas.queryByRole("button", { name: /Log in/i }),
    ).not.toBeInTheDocument();

    const logoutButton = await canvas.findByRole("button", {
      name: /Log out/i,
    });
    await expect(logoutButton).toBeInTheDocument();
  },
};
