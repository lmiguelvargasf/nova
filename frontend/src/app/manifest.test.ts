import manifest from "@/app/manifest";

test("returns installable web app metadata", () => {
  const appManifest = manifest();

  expect(appManifest.name).toBe("Nova");
  expect(appManifest.short_name).toBe("Nova");
  expect(appManifest.start_url).toBe("/");
  expect(appManifest.display).toBe("standalone");
  expect(appManifest.background_color).toBe("#ffffff");
  expect(appManifest.theme_color).toBe("#0f172a");
  expect(appManifest.icons).toContainEqual({
    src: "/icon-192x192.png",
    sizes: "192x192",
    type: "image/png",
  });
  expect(appManifest.icons).toContainEqual({
    src: "/icon-512x512.png",
    sizes: "512x512",
    type: "image/png",
  });
});
