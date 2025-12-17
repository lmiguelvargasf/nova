import tsconfigPaths from "vite-tsconfig-paths";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [tsconfigPaths()],
  // Add esbuild configuration for automatic JSX runtime
  esbuild: {
    jsx: "automatic",
  },
  server: {
    host: "0.0.0.0",
    port: 51204,
    strictPort: true,
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./__tests__/setup.tsx",
    include: [
      "src/**/*.{test,spec}.{ts,tsx}",
      "__tests__/**/*.{test,spec}.{ts,tsx}",
    ],
    open: false,
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      reportsDirectory: "./coverage",
      // Exclude build/config files from coverage by default
      exclude: [
        // framework and build configs
        "**/next.config.ts",
        "**/postcss.config.mjs",
        "**/eslint.config.mjs",
        "**/vitest.config.ts",
        "**/playwright.config.ts",
        // type declarations
        "**/next-env.d.ts",
        // Next.js build output and HMR client files
        "**/.next/**",
        // Playwright test files
        "**/e2e/**",
        "**/tests-examples/**",
        "**/playwright-report/**",
        // Storybook files
        "vitest.shims.d.ts",
        "vitest.workspace.ts",
        ".storybook/**",
        "**/storybook-static/**",
        // GraphQL files
        "src/lib/graphql/**",
        "schema/schema.graphql",
      ],
    },
  },
});
