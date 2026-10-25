import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { BehindMe } from "../BehindMe";
import { Camera, Key, popIn } from "../Camera";
import { UI_FONT } from "../fonts";
import { glass } from "../Glass";

export type ProofCard = { label: string; value: string; unit?: string };

export type OverTheShoulderProps = {
  before: ProofCard;
  after: ProofCard;
  startFrom?: number;
};

export const overTheShoulderDefaults: OverTheShoulderProps = {
  // Placeholder numbers: replace with your real ones.
  before: { label: "BEFORE", value: "1,204", unit: "views" },
  after: { label: "AFTER", value: "412K", unit: "views" },
  startFrom: 1200,
};

// Camera: slides over the left shoulder, back across, over the right shoulder, then home.
const KEYS: Key[] = [
  { frame: 0, scale: 1, u: 0, v: 0 },
  { frame: 5, scale: 1, u: 0, v: 0 },
  { frame: 20, scale: 1.3, u: 1, v: -0.45 },
  { frame: 27, scale: 1.31, u: 0.96, v: -0.47 },
  { frame: 36, scale: 1.12, u: 0, v: -0.3 },
  { frame: 46, scale: 1.3, u: -1, v: -0.45 },
  { frame: 55, scale: 1.31, u: -0.96, v: -0.47 },
  { frame: 70, scale: 1, u: 0, v: 0 },
];

// Card positions in the shot (before the camera move), just above each shoulder.
const CARD_W = 240;
const CARD_BOTTOM = 1230;
// Far enough in that the card in focus stays inside x = 120 to 960 through the whole push.
const LEFT_X = 168;
const RIGHT_X = 1080 - LEFT_X - CARD_W;

// Text sits on the outer side of each card, away from the head.
const Card: React.FC<{ card: ProofCard; x: number; at: number; align: "left" | "right" }> = ({
  card,
  x,
  at,
  align,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { scale, opacity } = popIn(frame, at, fps);
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        bottom: 1920 - CARD_BOTTOM,
        width: CARD_W,
        padding: "24px 24px 22px",
        borderRadius: 28,
        boxSizing: "border-box",
        fontFamily: UI_FONT,
        textAlign: align,
        opacity,
        transform: `scale(${scale})`,
        transformOrigin: "50% 100%",
        ...glass("dark"),
      }}
    >
      <div style={{ color: "#B9BAC2", fontSize: 24, fontWeight: 700, letterSpacing: 5 }}>{card.label}</div>
      <div style={{ color: "white", fontSize: 58, fontWeight: 700, lineHeight: 1.05, marginTop: 6 }}>
        {card.value}
      </div>
      {card.unit ? (
        <div style={{ color: "#B9BAC2", fontSize: 26, fontWeight: 500, marginTop: 2 }}>{card.unit}</div>
      ) : null}
    </div>
  );
};

export const OverTheShoulder: React.FC<OverTheShoulderProps> = ({
  before,
  after,
  startFrom = overTheShoulderDefaults.startFrom!,
}) => (
  <Camera keys={KEYS}>
    <BehindMe framing={{ startFrom, centerX: 0.578 }}>
      <Card card={before} x={LEFT_X} at={10} align="left" />
      <Card card={after} x={RIGHT_X} at={40} align="right" />
    </BehindMe>
  </Camera>
);

// Exposed for the safe-zone check.
export const OVER_THE_SHOULDER_KEYS = KEYS;
export const OVER_THE_SHOULDER_CARDS = { width: CARD_W, bottom: CARD_BOTTOM, left: LEFT_X, right: RIGHT_X };
