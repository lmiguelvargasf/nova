import tsconfigPaths from "vite-tsconfig-paths";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [tsconfigPaths()],
  server: {
    host: "0.0.0.0",
    port: 51204,
    strictPort: true,
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./__tests__/setup.tsx",
    restoreMocks: true,
    environmentOptions: {
      jsdom: { url: "http://localhost" },
    },
    include: [
      "src/**/*.{test,spec}.{ts,tsx}",
      "__tests__/**/*.{test,spec}.{ts,tsx}",
    ],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      reportsDirectory: "./coverage",
      include: ["src/**/*.{ts,tsx}"],
      // Exclude build/config files from coverage by default
      exclude: [
        // type declarations
        "**/*.d.ts",
        // framework and build configs
        "**/next.config.ts",
        "**/postcss.config.mjs",
        "**/vitest.config.ts",
        "**/playwright.config.ts",
        // Next.js build output and HMR client files
        "**/.next/**",
        // Playwright test files
        "**/e2e/**",
        "**/tests-examples/**",
        "**/playwright-report/**",
        // Storybook files
        "vitest.shims.d.ts",
        ".storybook/**",
        "**/storybook-static/**",
        // GraphQL files
        "src/lib/graphql/**",
        "schema/schema.graphql",
      ],
    },
  },
});
