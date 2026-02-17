"use client";

import { useEffect } from "react";

const SERVICE_WORKER_PATH = "/sw.js";

export default function ServiceWorkerRegistration() {
  useEffect(() => {
    if (!("serviceWorker" in navigator)) {
      return;
    }

    void navigator.serviceWorker
      .register(SERVICE_WORKER_PATH)
      .catch((error: unknown) => {
        if (process.env.NODE_ENV !== "production") {
          console.warn("Service worker registration failed:", error);
        }
      });
  }, []);

  return null;
}
