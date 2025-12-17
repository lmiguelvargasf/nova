import { expect, test } from "@playwright/test";

test.describe("Home Page", () => {
  test("should load and display main elements", async ({ page }) => {
    await page.goto("http://localhost:3000");
    await expect(page).toHaveTitle("Create Next App");
    const logo = page.getByRole("img", { name: "Next.js logo" });
    await expect(logo).toBeVisible();
    await expect(page.getByText(/Get started by editing/)).toBeVisible();
  });
});
