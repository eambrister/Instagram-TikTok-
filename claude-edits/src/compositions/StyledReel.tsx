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
import { GlassGraphCard } from "./GlassGraph";
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
  // Optional GlassGraph card at chest height (3 s) for a number he says. Leave the burned-in captions out
  // for that window with reel-editor's --caption-gap, so the card doesn't sit on them.
  graph?: { at: number; title: string; from: number; to: number; fullNumber?: boolean; top?: number; scale?: number } | null;
  // Card top in px (default 560). Lower it beside his head when he sits low in the frame.
  cardTop?: number;
  // A list video: one card beside his head that ticks each item as he says it (seconds in the edit).
  // Keep illustration beats on the other side while it is up.
  checklist?: { from: number; to: number; side: "left" | "right"; title: string; items: { label: string; at: number }[] } | null;
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
  Lightbulb: Art.Lightbulb,
  Footsteps: Art.Footsteps,
  Target: Art.Target,
  Feather: Art.Feather,
  StreakCalendar: Art.StreakCalendar,
  Dumbbell: Art.Dumbbell,
  NoGym: Art.NoGym,
  Sneaker: Art.Sneaker,
  Runner: Art.Runner,
  HeartPulse: Art.HeartPulse,
  Flame: Art.Flame,
  Chair: Art.Chair,
  EmptyPlate: Art.EmptyPlate,
  Fridge: Art.Fridge,
  Apple: Art.Apple,
};

// Beside his head (about x = 330-760 at this height), so nothing on the card is hidden behind him.
const CARD = { w: 210, h: 318, top: 560 };
const EXIT_FRAMES = 6;

const Card: React.FC<{ beat: BeatSpec; frames: number; top: number }> = ({ beat, frames, top }) => {
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
        top,
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

const LIST_W = 224;
const ACCENT = Art.ACCENT;

const ChecklistCard: React.FC<{ list: NonNullable<StyledReelProps["checklist"]>; frames: number; top: number }> = ({ list, frames, top }) => {
  const t = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame: t, fps, config: { damping: 12, stiffness: 190, mass: 0.6 } });
  const out = interpolate(t, [frames - EXIT_FRAMES, frames], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const dir = list.side === "left" ? 1 : -1;
  return (
    <div
      style={{
        position: "absolute",
        left: list.side === "left" ? SAFE_LEFT : SAFE_RIGHT - LIST_W,
        top,
        width: LIST_W,
        boxSizing: "border-box",
        padding: "16px 14px 18px",
        borderRadius: 30,
        backgroundColor: "rgba(16, 17, 22, 0.72)",
        backdropFilter: "blur(18px)",
        border: "2px solid rgba(255, 255, 255, 0.14)",
        boxShadow: "0 22px 50px rgba(0, 0, 0, 0.35)",
        display: "flex",
        flexDirection: "column",
        gap: 10,
        opacity: Math.min(1, pop * 1.5) * out,
        transform: `translateY(${(1 - pop) * 40}px) rotate(${(1 - Math.min(1, pop)) * 10 * dir}deg) scale(${0.6 + 0.4 * pop})`,
        transformOrigin: list.side === "left" ? "0% 100%" : "100% 100%",
      }}
    >
      <div style={{ fontFamily: CONDENSED_FONT, fontWeight: 800, fontSize: 27, color: ACCENT, letterSpacing: 0.5, lineHeight: 1.05 }}>
        {list.title}
      </div>
      {list.items.map((it, i) => {
        const at = Math.round((it.at - list.from) * fps);
        const shown = interpolate(t, [at - 4, at + 2], [0.35, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const tick = spring({ frame: t - at, fps, config: { damping: 10, stiffness: 220, mass: 0.5 } });
        return (
          <div key={it.label} style={{ display: "flex", alignItems: "center", gap: 10, opacity: shown }}>
            <div
              style={{
                width: 28, height: 28, flexShrink: 0, borderRadius: 8, boxSizing: "border-box",
                border: `3px solid ${t >= at ? ACCENT : "rgba(255,255,255,0.5)"}`,
                backgroundColor: t >= at ? ACCENT : "transparent",
                display: "flex", alignItems: "center", justifyContent: "center",
              }}
            >
              {t >= at ? (
                <svg viewBox="0 0 24 24" width={20} height={20} style={{ transform: `scale(${tick})` }}>
                  <path d="M5 12.5 L10 17 L19 7" fill="none" stroke="#111" strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              ) : null}
            </div>
            <div style={{ fontFamily: CONDENSED_FONT, fontWeight: 800, fontSize: 25, color: "white", lineHeight: 1 }}>{it.label}</div>
          </div>
        );
      })}
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

export const StyledReel: React.FC<StyledReelProps> = ({ video, maskDir, beats, word, graph, cardTop, checklist }) => {
  const { fps } = useVideoConfig();
  const f = (s: number) => Math.round(s * fps);
  return (
    <AbsoluteFill style={{ backgroundColor: AUDIT ? undefined : "black" }}>
      {AUDIT ? null : <OffthreadVideo src={staticFile(video)} style={{ width: WIDTH, height: HEIGHT }} />}
      {beats.map((b) => (
        <Sequence key={`${b.from}`} from={f(b.from)} durationInFrames={f(b.to) - f(b.from)} layout="none">
          <Card beat={b} frames={f(b.to) - f(b.from)} top={cardTop ?? CARD.top} />
        </Sequence>
      ))}
      {checklist ? (
        <Sequence from={f(checklist.from)} durationInFrames={f(checklist.to) - f(checklist.from)} layout="none">
          <ChecklistCard list={checklist} frames={f(checklist.to) - f(checklist.from)} top={cardTop ?? CARD.top} />
        </Sequence>
      ) : null}
      {word ? (
        <Sequence from={f(word.at)} durationInFrames={TEXT_BEHIND_FRAMES} layout="none">
          <RisingWord word={word.text} centerY={word.centerY} />
        </Sequence>
      ) : null}
      <Person video={video} maskDir={maskDir} />
      {/* In front of him: it sits on his chest, below the face. */}
      {graph ? (
        <Sequence from={f(graph.at)} durationInFrames={90} layout="none">
          <GlassGraphCard title={graph.title} from={graph.from} to={graph.to} fullNumber={graph.fullNumber} top={graph.top}
            scale={graph.scale} />
        </Sequence>
      ) : null}
    </AbsoluteFill>
  );
};

// As long as the edit (from the mask's frame count).
export const styledReelMetadata: CalculateMetadataFunction<StyledReelProps> = async ({ props }) => {
  const meta = await fetch(staticFile(`${props.maskDir}/meta.json`)).then((r) => r.json());
  return { durationInFrames: meta.frameCount };
};
