import React from "react";
import {
  AbsoluteFill,
  CalculateMetadataFunction,
  interpolate,
  OffthreadVideo,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { usePersonMask } from "../BehindMe";
import { boxStyle } from "../Footage";
import { CONDENSED_FONT } from "../fonts";
import * as Art from "../illustrations";
import { AUDIT, HEIGHT, SAFE_LEFT, SAFE_RIGHT, WIDTH } from "../settings";
import { RisingWord, TEXT_BEHIND_FRAMES } from "./TextBehind";
import abnormal from "../reels/abnormal.json";

/**
 * Eddie's saved reel style, applied to a finished reel-editor edit (pinned title, captions, music already in it):
 * an illustration card beside his head for each phrase, and one key word rising behind his head.
 * Cards and the word sit behind him using a person mask made from the edit, so they never cover his face.
 * Each video's beats live in src/reels/<name>.json (see CLAUDE.md for how to write one).
 */
export type Side = "left" | "right";
export type BeatSpec = {
  from: number; // seconds in the edit
  to: number;
  side: Side;
  label: string; // his own words
  art: keyof typeof ART;
  artProps?: Record<string, unknown>; // frame timings are relative to the card appearing
  labelSwitch?: { at: number; text: string }; // seconds in the edit
};
export type StyledReelProps = {
  video: string; // in public/
  maskDir: string; // in public/, from tools/make_mask.py on the same video
  beats: BeatSpec[];
  word: { text: string; at: number; centerY: number } | null;
};
export const styledReelDefaults = abnormal as StyledReelProps;

// Illustrations by name (src/illustrations.tsx). Add new ones there and here.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const ART: Record<string, React.FC<any>> = {
  PromiseKept: Art.PromiseKept,
  CalendarFlip: Art.CalendarFlip,
  AlarmClock: Art.AlarmClock,
  MoonSleep: Art.MoonSleep,
  FoodLog: Art.FoodLog,
  PizzaSlice: Art.PizzaSlice,
  BatteryLow: Art.BatteryLow,
  StandOut: Art.StandOut,
  Diamond: Art.Diamond,
  MondayLoop: Art.MondayLoop,
  Tomorrow: Art.Tomorrow,
  SquarePeg: Art.SquarePeg,
  BrokenLink: Art.BrokenLink,
  Lightning: Art.Lightning,
  OddOneOut: Art.OddOneOut,
  CommentTyping: Art.CommentTyping,
};

// Beside his head (about x = 330-760 at this height), so nothing on the card is hidden behind him.
const CARD = { w: 210, h: 318, top: 560 };
const EXIT_FRAMES = 6;

const Card: React.FC<{ beat: BeatSpec; frames: number }> = ({ beat, frames }) => {
  const { fps: rate } = useVideoConfig();
  const ArtComponent = ART[beat.art];
  const t = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame: t, fps, config: { damping: 12, stiffness: 190, mass: 0.6 } });
  const out = interpolate(t, [frames - EXIT_FRAMES, frames], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // Pops from its outer bottom corner and tilts inward, so the outer edge never leaves the safe zone.
  const dir = beat.side === "left" ? 1 : -1;
  const float = Math.sin(t / 14) * 5;
  return (
    <div
      style={{
        position: "absolute",
        left: beat.side === "left" ? SAFE_LEFT : SAFE_RIGHT - CARD.w,
        top: CARD.top,
        width: CARD.w,
        height: CARD.h,
        boxSizing: "border-box",
        padding: "18px 12px 16px",
        borderRadius: 34,
        backgroundColor: "rgba(16, 17, 22, 0.72)",
        backdropFilter: "blur(18px)",
        border: "2px solid rgba(255, 255, 255, 0.14)",
        boxShadow: "0 22px 50px rgba(0, 0, 0, 0.35)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 6,
        opacity: Math.min(1, pop * 1.5) * out,
        transform: `translateY(${(1 - pop) * 40 + float}px) rotate(${(1 - Math.min(1, pop)) * 10 * dir}deg) scale(${(0.6 + 0.4 * pop) * (0.9 + 0.1 * out)})`,
        transformOrigin: beat.side === "left" ? "0% 100%" : "100% 100%",
      }}
    >
      <div
        style={{
          height: 66,
          display: "flex",
          alignItems: "center",
          fontFamily: CONDENSED_FONT,
          fontWeight: 800,
          fontSize: 31,
          lineHeight: 1,
          letterSpacing: 0.5,
          color: "white",
          textAlign: "center",
        }}
      >
        {beat.labelSwitch && t >= Math.round((beat.labelSwitch.at - beat.from) * rate) ? beat.labelSwitch.text : beat.label}
      </div>
      <div style={{ width: 186, height: 186 }}>
        <ArtComponent t={t} {...beat.artProps} />
      </div>
    </div>
  );
};

const FULL = { x: 0, y: 0, w: WIDTH, h: HEIGHT };

// The person, cut out of the edit, on top of the illustrations.
const Person: React.FC<{ video: string; maskDir: string }> = ({ video, maskDir }) => {
  const { box, maskStyle } = usePersonMask({ startFrom: 0 }, maskDir, FULL);
  if (AUDIT) return null;
  return <OffthreadVideo src={staticFile(video)} muted style={{ ...boxStyle(box), ...maskStyle }} />;
};

export const StyledReel: React.FC<StyledReelProps> = ({ video, maskDir, beats, word }) => {
  const { fps } = useVideoConfig();
  const f = (s: number) => Math.round(s * fps);
  return (
    <AbsoluteFill style={{ backgroundColor: AUDIT ? undefined : "black" }}>
      {AUDIT ? null : <OffthreadVideo src={staticFile(video)} style={{ width: WIDTH, height: HEIGHT }} />}
      {beats.map((b) => (
        <Sequence key={`${b.from}`} from={f(b.from)} durationInFrames={f(b.to) - f(b.from)} layout="none">
          <Card beat={b} frames={f(b.to) - f(b.from)} />
        </Sequence>
      ))}
      {word ? (
        <Sequence from={f(word.at)} durationInFrames={TEXT_BEHIND_FRAMES} layout="none">
          <RisingWord word={word.text} centerY={word.centerY} />
        </Sequence>
      ) : null}
      <Person video={video} maskDir={maskDir} />
    </AbsoluteFill>
  );
};

// As long as the edit (from the mask's frame count).
export const styledReelMetadata: CalculateMetadataFunction<StyledReelProps> = async ({ props }) => {
  const meta = await fetch(staticFile(`${props.maskDir}/meta.json`)).then((r) => r.json());
  return { durationInFrames: meta.frameCount };
};
