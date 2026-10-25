// Deterministic motion helpers: everything is a pure function of the composition frame.
import { Easing, interpolate, spring } from "remotion";

export const easeOut = Easing.bezier(0.16, 1, 0.3, 1);
export const easeIn = Easing.bezier(0.55, 0, 0.75, 0.2);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);

/** 0 -> 1 entrance over n frames starting at frame `from`, clamped. */
export function enter(frame: number, from: number, n: number, ease = easeOut) {
  return interpolate(frame, [from, from + Math.max(1, n)], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
}

/** 1 -> 0 exit over n frames ending at frame `to`. */
export function exit(frame: number, to: number, n: number) {
  return interpolate(frame, [to - Math.max(1, n), to], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeIn });
}

/** Settle spring (no visible bounce), deterministic for a given fps. */
export function settle(frame: number, fps: number, from: number, frames: number) {
  return spring({ frame: frame - from, fps, durationInFrames: Math.max(2, frames), config: { damping: 200, mass: 0.6, stiffness: 180 } });
}

export const toFrame = (t: number, fps: number) => Math.round(t * fps);

export const shadow = {
  card: "0 2px 0 rgba(255,255,255,0.06) inset, 0 34px 70px rgba(0,0,0,0.45), 0 10px 22px rgba(0,0,0,0.35)",
  soft: "0 18px 40px rgba(0,0,0,0.38), 0 4px 10px rgba(0,0,0,0.3)",
};
