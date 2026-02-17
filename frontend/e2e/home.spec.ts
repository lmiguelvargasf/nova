import { expect, test } from "@playwright/test";

test.describe("Home Page", () => {
  test("should load and display main elements", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle("Nova");
    await expect(
      page.getByRole("heading", {
        name: /Build and ship faster/i,
      }),
    ).toBeVisible();
    await expect(
      page.getByRole("heading", { name: /Registration timeline/i }),
    ).toBeVisible();
    await expect(page.getByText(/Data source/i)).toBeVisible();
  });

  test("should expose manifest metadata in the document head", async ({
    page,
  }) => {
    await page.goto("/");

    await expect(page.locator('head link[rel="manifest"]')).toHaveAttribute(
      "href",
      "/manifest.webmanifest",
    );
  });

  test("should serve the web app manifest and service worker", async ({
    request,
  }) => {
    const manifestResponse = await request.get("/manifest.webmanifest");
    expect(manifestResponse.ok()).toBeTruthy();
    expect(manifestResponse.headers()["content-type"]).toContain("json");

    const manifestBody = await manifestResponse.json();
    expect(manifestBody.name).toBe("Nova");
    expect(manifestBody.display).toBe("standalone");
    expect(manifestBody.start_url).toBe("/");

    const serviceWorkerResponse = await request.get("/sw.js");
    expect(serviceWorkerResponse.ok()).toBeTruthy();
    expect(serviceWorkerResponse.headers()["content-type"]).toContain(
      "application/javascript",
    );
    expect(serviceWorkerResponse.headers()["cache-control"]).toContain(
      "no-cache",
    );
  });
});
