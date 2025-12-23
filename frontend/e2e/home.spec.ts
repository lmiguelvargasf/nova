import { expect, test } from "@playwright/test";

test.describe("Home Page", () => {
  test("should load and display main elements", async ({ page }) => {
    await page.goto("http://localhost:3000");
    await expect(page).toHaveTitle("Nova 🌟");
    await expect(
      page.getByRole("heading", {
        name: /Ship a GraphQL-ready product faster/i,
      }),
    ).toBeVisible();
    await expect(
      page.getByRole("heading", { name: /Live preview/i }),
    ).toBeVisible();
    await expect(page.getByText(/Python \+ Litestar/i)).toBeVisible();
  });
});
