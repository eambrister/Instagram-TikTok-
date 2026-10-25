import React from "react";
import { AbsoluteFill } from "remotion";
import { SAFE_LEFT, SAFE_WIDTH } from "./settings";

// Wrap text and graphics in this so they stay between x = 120 and x = 960.
export const SafeArea: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ children, style }) => (
  <AbsoluteFill
    style={{ left: SAFE_LEFT, width: SAFE_WIDTH, right: "auto", ...style }}
  >
    {children}
  </AbsoluteFill>
);
