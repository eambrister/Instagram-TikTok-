import React from "react";

// Shared glass card look.
export const glass = (tint: "dark" | "light"): React.CSSProperties => ({
  backgroundColor: tint === "dark" ? "rgba(18, 18, 22, 0.55)" : "rgba(255, 255, 255, 0.10)",
  backdropFilter: "blur(28px) saturate(1.2)",
  border: "2px solid rgba(255, 255, 255, 0.2)",
  boxShadow: "0 24px 60px rgba(0, 0, 0, 0.35)",
});
