import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { measureText } from "@remotion/layout-utils";
import { BehindMe } from "../BehindMe";
import { DISPLAY_FONT } from "../fonts";
import { SAFE_LEFT, SAFE_WIDTH } from "../settings";

export type TextBehindProps = {
  word: string;
  startFrom?: number;
};

export const textBehindDefaults: TextBehindProps = {
  // Placeholder word: replace with yours.
  word: "VIRAL",
  startFrom: 1320,
};

const LETTER_HEIGHT = 330; // px, height of the capitals
const CAP_HEIGHT_PER_EM = 0.86; // Anton
const LETTER_SPACING = 4;
// Middle of the letters, set so the head (top at about y = 792 here) covers the lower half.
const WORD_CENTER_Y = 790;
// Length of the effect, so its exit timing holds when it plays inside a longer sequence.
const TEXT_BEHIND_FRAMES = 90;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Biggest size up to LETTER_HEIGHT that still fits inside the safe zone.
const fitFontSize = (word: string) => {
  const wanted = LETTER_HEIGHT / CAP_HEIGHT_PER_EM;
  const { width } = measureText({
    text: word,
    fontFamily: DISPLAY_FONT,
    fontSize: wanted,
    fontWeight: "400",
    letterSpacing: `${LETTER_SPACING}px`,
  });
  return width <= SAFE_WIDTH ? wanted : wanted * (SAFE_WIDTH / width);
};

export const TextBehind: React.FC<TextBehindProps> = ({ word, startFrom = textBehindDefaults.startFrom! }) => {
  const frame = useCurrentFrame();
  const fontSize = fitFontSize(word);

  const rise = interpolate(frame, [0, 10], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const fall = interpolate(frame, [75, TEXT_BEHIND_FRAMES], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const lift = interpolate(frame, [10, 75], [0, 20], { ...clamp, easing: Easing.inOut(Easing.sin) });
  const y = (1 - rise) * 140 - lift + fall * 120;

  return (
    <BehindMe framing={{ startFrom, centerX: 0.572 }}>
      <div
        style={{
          position: "absolute",
          left: SAFE_LEFT,
          width: SAFE_WIDTH,
          top: WORD_CENTER_Y,
          display: "flex",
          justifyContent: "center",
          transform: `translateY(calc(-50% + ${y}px))`,
        }}
      >
        <div
          style={{
            fontFamily: DISPLAY_FONT,
            fontSize,
            // Line box equal to the capitals, so the word's centre is the letters' centre.
            lineHeight: `${CAP_HEIGHT_PER_EM}em`,
            letterSpacing: LETTER_SPACING,
            color: "white",
            whiteSpace: "nowrap",
            opacity: rise * (1 - fall),
            filter: `blur(${(1 - rise) * 18 + fall * 10}px)`,
            textShadow: "0 10px 50px rgba(0,0,0,0.3)",
          }}
        >
          {word}
        </div>
      </div>
    </BehindMe>
  );
};
