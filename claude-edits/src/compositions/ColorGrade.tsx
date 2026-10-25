import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { Footage, Framing } from "../Footage";
import { UI_FONT } from "../fonts";
import { AUDIT, SAFE_LEFT, SAFE_RIGHT, WIDTH } from "../settings";

export type ColorGradeProps = { startFrom?: number };
export const colorGradeDefaults: ColorGradeProps = { startFrom: 1800 };

const WIPE_START = 25;
const WIPE_END = 45;
const LABEL_Y = 270;
const LABEL_W = 190;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Per-channel curves, 0 to 1. A gentle S-curve; shadows lean teal (more green and blue),
// highlights lean warm (less blue), and the middle stays neutral so skin keeps its colour.
const GRADE = {
  r: "0 0.04 0.15 0.3 0.5 0.692 0.845 0.945 1",
  g: "0.012 0.065 0.17 0.31 0.5 0.688 0.838 0.938 0.995",
  b: "0.035 0.095 0.188 0.322 0.497 0.675 0.818 0.912 0.97",
};

const Filters: React.FC = () => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    {/* Flat, like ungraded LOG: low contrast, low saturation, lifted blacks, a bit grey. */}
    <filter id="look-flat" colorInterpolationFilters="sRGB">
      <feColorMatrix type="saturate" values="0.55" />
      <feComponentTransfer>
        <feFuncR type="linear" slope="0.74" intercept="0.12" />
        <feFuncG type="linear" slope="0.74" intercept="0.12" />
        <feFuncB type="linear" slope="0.74" intercept="0.125" />
      </feComponentTransfer>
    </filter>
    <filter id="look-graded" colorInterpolationFilters="sRGB">
      <feComponentTransfer>
        <feFuncR type="table" tableValues={GRADE.r} />
        <feFuncG type="table" tableValues={GRADE.g} />
        <feFuncB type="table" tableValues={GRADE.b} />
      </feComponentTransfer>
      <feColorMatrix type="saturate" values="1.0" />
    </filter>
  </svg>
);

const Label: React.FC<{ text: string; center: number; opacity: number }> = ({ text, center, opacity }) =>
  opacity > 0 ? (
    <div
      style={{
        position: "absolute",
        top: LABEL_Y,
        left: Math.min(SAFE_RIGHT - LABEL_W, Math.max(SAFE_LEFT, center - LABEL_W / 2)),
        width: LABEL_W,
        height: 56,
        borderRadius: 999,
        backgroundColor: "rgba(12, 12, 16, 0.78)",
        color: "white",
        fontFamily: UI_FONT,
        fontWeight: 700,
        fontSize: 22,
        letterSpacing: 6,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        opacity,
      }}
    >
      {text}
    </div>
  ) : null;

export const ColorGrade: React.FC<ColorGradeProps> = ({ startFrom = colorGradeDefaults.startFrom! }) => {
  const frame = useCurrentFrame();
  const framing: Framing = { startFrom, centerX: 0.575 };
  // Position of the line of light; everything left of it is graded.
  const x = interpolate(frame, [WIPE_START, WIPE_END], [0, WIDTH], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const wiping = frame >= WIPE_START && frame <= WIPE_END;

  // Each label sits in the middle of its side and fades as its side gets too small to hold it.
  const afterOpacity = interpolate(x, [80, 300], [0, 1], clamp);
  const beforeOpacity = interpolate(WIDTH - x, [80, 300], [0, 1], clamp);

  return (
    <AbsoluteFill>
      <Filters />
      <Footage framing={framing} style={{ filter: "url(#look-flat)" }} />
      <AbsoluteFill style={{ clipPath: `inset(0 ${WIDTH - x}px 0 0)` }}>
        <Footage framing={framing} style={{ filter: "url(#look-graded)" }} />
        {/* Gentle dark vignette, part of the graded look. */}
        <AbsoluteFill
          hidden={AUDIT}
          style={{
            background: "radial-gradient(ellipse 75% 60% at 50% 52%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.45) 100%)",
          }}
        />
      </AbsoluteFill>
      {/* The line of light is a full-frame transition, so the audit leaves it out. */}
      {wiping && x > 0 && x < WIDTH && !AUDIT ? (
        <div
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            left: x - 2,
            width: 4,
            backgroundColor: "white",
            boxShadow: "0 0 18px 6px rgba(255, 244, 225, 0.85), 0 0 60px 18px rgba(255, 236, 205, 0.45)",
          }}
        />
      ) : null}
      <Label text="BEFORE" center={(x + WIDTH) / 2} opacity={beforeOpacity} />
      <Label text="AFTER" center={x / 2} opacity={afterOpacity} />
    </AbsoluteFill>
  );
};
