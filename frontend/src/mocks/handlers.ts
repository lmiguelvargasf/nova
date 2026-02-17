import type { RequestHandler } from "msw";

// Keep a shared handler registry for Vitest and Storybook.
export const handlers: RequestHandler[] = [];
