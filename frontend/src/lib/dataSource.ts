import { useEffect, useState } from "react";

export type DataSource = "graphql" | "rest";

const STORAGE_KEY = "dataSource";
const CHANGE_EVENT = "dataSourceChange";

export function getStoredDataSource(): DataSource {
  if (typeof window === "undefined") {
    return "graphql";
  }
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored === "rest" ? "rest" : "graphql";
}

export function setStoredDataSource(next: DataSource) {
  localStorage.setItem(STORAGE_KEY, next);
  window.dispatchEvent(new Event(CHANGE_EVENT));
}

export function useDataSource() {
  const [mode, setMode] = useState<DataSource>("graphql");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const sync = () => {
      setMode(getStoredDataSource());
      setReady(true);
    };
    sync();
    window.addEventListener(CHANGE_EVENT, sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener(CHANGE_EVENT, sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  const updateMode = (next: DataSource) => {
    setMode(next);
    setReady(true);
    setStoredDataSource(next);
  };

  return { mode, setMode: updateMode, ready };
}
