import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame } from "remotion";
import { HEIGHT, WIDTH } from "./settings";

// A camera position. u and v slide the shot left/right and up/down as a share (-1 to 1) of how
// far it can go at this zoom without showing an edge, so the frame is always filled.
// u = 1 shows the left side of the shot, v = 1 shows the top.
export type Shot = { scale: number; u: number; v: number };
export type Key = { frame: number } & Shot;

const ease = Easing.inOut(Easing.cubic);
const HOLD_SPEED = 3;

export const shotAt = (keys: Key[], frame: number): Shot => {
  if (frame <= keys[0].frame) return keys[0];
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i];
    const b = keys[i + 1];
    if (frame <= b.frame) {
      const t = ease((frame - a.frame) / (b.frame - a.frame));
      return {
        scale: a.scale + (b.scale - a.scale) * t,
        u: a.u + (b.u - a.u) * t,
        v: a.v + (b.v - a.v) * t,
      };
    }
  }
  return keys[keys.length - 1];
};

// Where a point of the shot (x, y) lands on screen.
export const toScreen = (s: Shot, x: number, y: number) => {
  const scale = Math.max(1, s.scale);
  const tx = s.u * (scale - 1) * (WIDTH / 2);
  const ty = s.v * (scale - 1) * (HEIGHT / 2);
  return { x: WIDTH / 2 + scale * (x - WIDTH / 2) + tx, y: HEIGHT / 2 + scale * (y - HEIGHT / 2) + ty };
};

// Average on-screen movement per frame of the corners and centre, for motion blur.
const speedAt = (keys: Key[], frame: number) => {
  const a = shotAt(keys, frame - 0.5);
  const b = shotAt(keys, frame + 0.5);
  const pts = [
    [0, 0],
    [WIDTH, 0],
    [0, HEIGHT],
    [WIDTH, HEIGHT],
    [WIDTH / 2, HEIGHT / 2],
  ];
  let dx = 0;
  let dy = 0;
  for (const [x, y] of pts) {
    const p = toScreen(a, x, y);
    const q = toScreen(b, x, y);
    dx += Math.abs(q.x - p.x);
    dy += Math.abs(q.y - p.y);
  }
  return { dx: dx / pts.length, dy: dy / pts.length };
};

/**
 * Moves the whole shot (footage and anything attached to it) through `keys`, easing in and out
 * of every move. Motion blur follows the camera's speed and is off while it holds.
 */
export const Camera: React.FC<{ keys: Key[]; blur?: number; children: React.ReactNode }> = ({
  keys,
  blur = 0.14,
  children,
}) => {
  const frame = useCurrentFrame();
  const shot = shotAt(keys, frame);
  const scale = Math.max(1, shot.scale);
  const tx = shot.u * (scale - 1) * (WIDTH / 2);
  const ty = shot.v * (scale - 1) * (HEIGHT / 2);
  const { dx, dy } = speedAt(keys, frame);
  // Slow drifts (under HOLD_SPEED px per frame) stay sharp; blur fades in above that.
  const ramp = (d: number) => Math.max(0, d - HOLD_SPEED) * blur;
  const bx = ramp(dx);
  const by = ramp(dy);
  const id = `camera-blur-${frame}`;
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <filter id={id} x="0" y="0" width="100%" height="100%">
          <feGaussianBlur stdDeviation={`${bx} ${by}`} edgeMode="duplicate" />
        </filter>
      </svg>
      <AbsoluteFill
        style={{
          transform: `translate(${tx}px, ${ty}px) scale(${scale})`,
          filter: bx || by ? `url(#${id})` : undefined,
        }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// Quick springy pop from 0.8 to 1 with a fade, starting at frame `at`.
export const popIn = (frame: number, at: number, fps: number) => {
  const t = frame - at;
  const s = spring({ frame: t, fps, config: { damping: 11, stiffness: 220, mass: 0.6 } });
  const scale = interpolate(s, [0, 1], [0.8, 1]);
  const opacity = interpolate(t, [0, 0.15 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return { scale, opacity };
};
