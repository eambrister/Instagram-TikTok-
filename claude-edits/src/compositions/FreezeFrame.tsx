import React from "react";
import {
  AbsoluteFill,
  Easing,
  Freeze,
  interpolate,
  OffthreadVideo,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { usePersonMask } from "../BehindMe";
import { popIn } from "../Camera";
import { Footage, Framing, boxStyle } from "../Footage";
import { UI_FONT } from "../fonts";
import { AUDIT, SOURCE_CLIP } from "../settings";

export type FreezeFrameProps = {
  name: string;
  role: string;
  startFrom?: number;
};

export const freezeFrameDefaults: FreezeFrameProps = {
  // Placeholder name tag: replace with yours.
  name: "Edison Ambrister",
  role: "FITNESS COACH",
  startFrom: 1080,
};

const FREEZE_AT = 15;
const RELEASE = 60;
const RELEASE_END = 70;
const OUTLINE_PX = 12;
const CENTER_X = 0.586;
// The sticker scales about the middle of the body.
const ORIGIN = "540px 1450px";
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

type Look = { grey: number; outline: number; scale: number };

// One frame of the scene: grey background, white sticker outline, the person in colour on top.
const Scene: React.FC<{ framing: Framing; look: Look }> = ({ framing, look }) => {
  const { box, maskStyle } = usePersonMask(framing);
  const sticker: React.CSSProperties = { transform: `scale(${look.scale})`, transformOrigin: ORIGIN };
  // The sticker is the person, so the audit leaves it out with the footage.
  if (AUDIT) return null;
  return (
    <AbsoluteFill>
      <Footage
        framing={framing}
        style={{ filter: `grayscale(${look.grey}) brightness(${1 - 0.4 * look.grey})` }}
      />
      {look.outline > 0 ? (
        <AbsoluteFill style={{ ...sticker, opacity: look.outline }}>
          <svg width={0} height={0} style={{ position: "absolute" }}>
            <filter id="sticker-edge" x="-10%" y="-10%" width="120%" height="120%">
              <feMorphology operator="dilate" radius={OUTLINE_PX} />
              <feDropShadow dx="0" dy="12" stdDeviation="14" floodColor="#000" floodOpacity="0.45" />
            </filter>
          </svg>
          {/* Filter on the wrapper so it grows the already-masked white silhouette. */}
          <AbsoluteFill style={{ filter: "url(#sticker-edge)" }}>
            <div style={{ ...boxStyle(box), ...maskStyle, backgroundColor: "white" }} />
          </AbsoluteFill>
        </AbsoluteFill>
      ) : null}
      <AbsoluteFill style={sticker}>
        <OffthreadVideo
          src={staticFile(SOURCE_CLIP)}
          startFrom={framing.startFrom}
          muted
          style={{ ...boxStyle(box), ...maskStyle }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const NameTag: React.FC<{ name: string; role: string; opacity: number; scale: number }> = ({
  name,
  role,
  opacity,
  scale,
}) => (
  <AbsoluteFill style={{ alignItems: "center", top: 1600, height: "auto", opacity }}>
    <div
      style={{
        maxWidth: 840,
        padding: "22px 52px 24px",
        borderRadius: 999,
        backgroundColor: "rgba(14, 14, 18, 0.88)",
        boxShadow: "0 16px 40px rgba(0, 0, 0, 0.4)",
        textAlign: "center",
        fontFamily: UI_FONT,
        transform: `scale(${scale})`,
      }}
    >
      <div style={{ color: "white", fontSize: 54, fontWeight: 700, lineHeight: 1.1, whiteSpace: "nowrap" }}>
        {name}
      </div>
      <div style={{ color: "#C9CAD2", fontSize: 22, fontWeight: 700, letterSpacing: 9, marginTop: 8 }}>
        {role}
      </div>
    </div>
  </AbsoluteFill>
);

export const FreezeFrame: React.FC<FreezeFrameProps> = ({ name, role, startFrom = freezeFrameDefaults.startFrom! }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Into the freeze (under the flash) and back out on release.
  const into = interpolate(frame, [FREEZE_AT, FREEZE_AT + 6], [0, 1], clamp);
  const out = interpolate(frame, [RELEASE, RELEASE_END], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const amount = into * (1 - out);
  const pop = spring({ frame: frame - FREEZE_AT, fps, config: { damping: 10, stiffness: 180, mass: 0.6 } });
  const look: Look = {
    grey: amount,
    outline: amount,
    scale: 1 + 0.04 * (frame < RELEASE ? pop : 1 - out),
  };
  const tag = popIn(frame, FREEZE_AT + 6, fps);
  const flash = frame < FREEZE_AT ? 0 : interpolate(frame, [FREEZE_AT, FREEZE_AT + 6], [0.8, 0], clamp);
  const frozen: Framing = { startFrom: startFrom + FREEZE_AT, plateFrom: startFrom, centerX: CENTER_X };

  return (
    <AbsoluteFill>
      <Sequence durationInFrames={FREEZE_AT} layout="none">
        <Footage framing={{ startFrom, centerX: CENTER_X }} />
      </Sequence>
      <Sequence from={FREEZE_AT} durationInFrames={RELEASE - FREEZE_AT} layout="none">
        <Freeze frame={0}>
          <Scene framing={frozen} look={look} />
        </Freeze>
      </Sequence>
      {/* Plays on from the frozen frame. */}
      <Sequence from={RELEASE} layout="none">
        <Scene framing={frozen} look={look} />
      </Sequence>
      {frame >= FREEZE_AT ? (
        <NameTag name={name} role={role} opacity={tag.opacity * (1 - out)} scale={tag.scale} />
      ) : null}
      {flash > 0 && !AUDIT ? <AbsoluteFill style={{ backgroundColor: "white", opacity: flash }} /> : null}
    </AbsoluteFill>
  );
};
