import React from "react";
import { AbsoluteFill } from "remotion";
import { SafeArea } from "../SafeArea";
import { SAFE_LEFT, SAFE_RIGHT } from "../settings";

// Reference layout showing the safe zone. Not an effect.
export const SafeZoneGuide: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#111" }}>
    <AbsoluteFill
      style={{ left: 0, width: SAFE_LEFT, backgroundColor: "rgba(255,0,0,0.35)" }}
    />
    <AbsoluteFill
      style={{ left: SAFE_RIGHT, right: 0, width: "auto", backgroundColor: "rgba(255,0,0,0.35)" }}
    />
    <SafeArea style={{ justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          color: "white",
          fontFamily: "sans-serif",
          fontSize: 64,
          fontWeight: 800,
          textAlign: "center",
        }}
      >
        Safe zone
        <br />
        x = {SAFE_LEFT} to {SAFE_RIGHT}
      </div>
    </SafeArea>
  </AbsoluteFill>
);
