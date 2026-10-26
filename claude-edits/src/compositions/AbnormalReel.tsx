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

// The saved-style edit of talking.mp4 (from reel-editor, title pinned at the top), with an illustration for
// each phrase beside his head and ABNORMAL rising behind it. Illustrations and the word sit behind him,
// using a person mask made from the edit, so they never cover his face.
export type AbnormalReelProps = { video: string; maskDir: string };
export const abnormalReelDefaults: AbnormalReelProps = { video: "reel/final.mp4", maskDir: "reel-mask" };

type Side = "left" | "right";
// label can change over the beat (t = frames since the card appeared).
type Beat = { from: number; to: number; side: Side; label: string | ((t: number) => string); art: (t: number) => React.ReactNode };

// Times are seconds in the edit, matched to his captions. Labels are his own words.
const BEATS: Beat[] = [
  { from: 0.2, to: 3.5, side: "left", label: "KEEPING YOUR WORD", art: (t) => <Art.PromiseKept t={t} /> },
  { from: 3.6, to: 9.2, side: "right", label: (t) => (t < 112 ? "START IN JANUARY" : "ALMOST NOVEMBER"), art: (t) => <Art.CalendarFlip t={t} flipAt={105} flipFrames={33} /> },
  { from: 9.2, to: 11.8, side: "left", label: "UP EARLY TRAINING", art: (t) => <Art.AlarmClock t={t} /> },
  { from: 10.6, to: 12.4, side: "right", label: "EVERYBODY'S SLEEPING", art: (t) => <Art.MoonSleep t={t} /> },
  { from: 11.9, to: 15.4, side: "left", label: "TRACKING YOUR FOOD", art: (t) => <Art.FoodLog t={t} /> },
  { from: 13.25, to: 15.5, side: "right", label: "WHATEVER THEY WANT", art: (t) => <Art.PizzaSlice t={t} /> },
  { from: 15.6, to: 18.9, side: "left", label: "SHOWING UP", art: (t) => <Art.BatteryLow t={t} /> },
  { from: 18.9, to: 20.8, side: "right", label: "NOT NORMAL", art: (t) => <Art.StandOut t={t} /> },
  { from: 20.75, to: 22.4, side: "left", label: "RARE", art: (t) => <Art.Diamond t={t} /> },
  { from: 25.5, to: 27.0, side: "right", label: "EVERY MONDAY", art: (t) => <Art.MondayLoop t={t} /> },
  { from: 27.0, to: 29.5, side: "left", label: "TOMORROW", art: (t) => <Art.Tomorrow t={t} /> },
  { from: 29.6, to: 31.6, side: "right", label: "FIT IN", art: (t) => <Art.SquarePeg t={t} /> },
  { from: 31.6, to: 34.4, side: "left", label: "KEEP PROMISES", art: (t) => <Art.BrokenLink t={t} /> },
  { from: 34.9, to: 37.0, side: "right", label: "BEING CRAZY", art: (t) => <Art.Lightning t={t} /> },
  { from: 37.0, to: 39.2, side: "left", label: "BEING ABNORMAL", art: (t) => <Art.OddOneOut t={t} /> },
  { from: 39.3, to: 42.4, side: "right", label: "COMMENT", art: (t) => <Art.CommentTyping t={t} word="ABNORMAL" /> },
];

// ABNORMAL behind his head as he says it (22.87s); his head top is at about y = 606 there.
const WORD = { text: "ABNORMAL", at: 22.67, centerY: 610 };

// Beside his head (about x = 330-760 at this height), so nothing on the card is hidden behind him.
const CARD = { w: 210, h: 318, top: 560 };
const EXIT_FRAMES = 6;

const Card: React.FC<{ beat: Beat; frames: number }> = ({ beat, frames }) => {
  const t = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame: t, fps, config: { damping: 12, stiffness: 190, mass: 0.6 } });
  const out = interpolate(t, [frames - EXIT_FRAMES, frames], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const dir = beat.side === "left" ? -1 : 1;
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
        transform: `translateY(${(1 - pop) * 40 + float}px) rotate(${(1 - pop) * 10 * dir}deg) scale(${(0.6 + 0.4 * pop) * (0.9 + 0.1 * out)})`,
        transformOrigin: beat.side === "left" ? "100% 100%" : "0% 100%",
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
        {typeof beat.label === "string" ? beat.label : beat.label(t)}
      </div>
      <div style={{ width: 186, height: 186 }}>{beat.art(t)}</div>
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

export const AbnormalReel: React.FC<AbnormalReelProps> = ({ video, maskDir }) => {
  const { fps } = useVideoConfig();
  const f = (s: number) => Math.round(s * fps);
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {AUDIT ? null : <OffthreadVideo src={staticFile(video)} style={{ width: WIDTH, height: HEIGHT }} />}
      {BEATS.map((b) => (
        <Sequence key={`${b.from}`} from={f(b.from)} durationInFrames={f(b.to) - f(b.from)} layout="none">
          <Card beat={b} frames={f(b.to) - f(b.from)} />
        </Sequence>
      ))}
      <Sequence from={f(WORD.at)} durationInFrames={TEXT_BEHIND_FRAMES} layout="none">
        <RisingWord word={WORD.text} centerY={WORD.centerY} />
      </Sequence>
      <Person video={video} maskDir={maskDir} />
    </AbsoluteFill>
  );
};

export const abnormalReelMetadata: CalculateMetadataFunction<AbnormalReelProps> = async ({ props }) => {
  const meta = await fetch(staticFile(`${props.maskDir}/meta.json`)).then((r) => r.json());
  return { durationInFrames: meta.frameCount };
};
