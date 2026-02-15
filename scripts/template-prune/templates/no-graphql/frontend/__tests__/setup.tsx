import "@testing-library/jest-dom";
import type React from "react";

vi.mock("next/image", () => ({
  __esModule: true,
  default: (props: React.ComponentProps<"img">) => {
    // biome-ignore lint/performance/noImgElement: next/image is intentionally mocked to a plain <img> in tests
    return <img {...props} alt={props.alt ?? "Mocked Image"} />;
  },
}));
