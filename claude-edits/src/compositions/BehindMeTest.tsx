import React from "react";
import { BehindMe } from "../BehindMe";
import { SafeArea } from "../SafeArea";

// Checks BehindMe: the word should sit behind the person and in front of the background.
export const BehindMeTest: React.FC = () => (
  <BehindMe framing={{ startFrom: 600 }}>
    <SafeArea style={{ justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          fontFamily: "sans-serif",
          fontWeight: 900,
          fontSize: 210,
          lineHeight: 0.85,
          color: "#ffd400",
          textAlign: "center",
          marginTop: -300,
        }}
      >
        BEHIND
        <br />
        ME
      </div>
    </SafeArea>
  </BehindMe>
);
