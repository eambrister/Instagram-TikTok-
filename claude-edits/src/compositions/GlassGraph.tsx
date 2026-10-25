import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { Footage } from "../Footage";
import { UI_FONT } from "../fonts";
import { formatCount } from "../lib/format";

export type GlassGraphProps = {
  title: string;
  from: number;
  to: number;
  // Shape of the graph from 0 (bottom) to 1 (top), left to right.
  points?: number[];
  startFrom?: number;
};

export const glassGraphDefaults: GlassGraphProps = {
  // Placeholder metric and numbers: replace with your real ones.
  title: "Views this month",
  from: 1204,
  to: 412000,
  points: [0.04, 0.1, 0.08, 0.2, 0.26, 0.22, 0.38, 0.47, 0.4, 0.58, 0.7, 0.66, 0.84, 1],
  startFrom: 1440,
};

const ORANGE = "#D97757";
const CARD = { w: 760, h: 520, top: 1300 };
const GRAPH = { w: 680, h: 230 };
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Smooth curve through the points (Catmull-Rom), sampled densely so the line can draw partially.
const samplePath = (points: number[], steps = 240) => {
  const pts = points.map((p, i) => ({ x: (i / (points.length - 1)) * GRAPH.w, y: (1 - p) * GRAPH.h }));
  const out: { x: number; y: number }[] = [];
  for (let s = 0; s <= steps; s++) {
    const t = (s / steps) * (pts.length - 1);
    const i = Math.min(pts.length - 2, Math.floor(t));
    const u = t - i;
    const p0 = pts[Math.max(0, i - 1)];
    const p1 = pts[i];
    const p2 = pts[i + 1];
    const p3 = pts[Math.min(pts.length - 1, i + 2)];
    const cr = (a: number, b: number, c: number, d: number) =>
      0.5 * (2 * b + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (-a + 3 * b - 3 * c + d) * u * u * u);
    out.push({ x: cr(p0.x, p1.x, p2.x, p3.x), y: Math.min(GRAPH.h, Math.max(0, cr(p0.y, p1.y, p2.y, p3.y))) });
  }
  return out;
};

export const GlassGraph: React.FC<GlassGraphProps> = ({
  title,
  from,
  to,
  points = glassGraphDefaults.points!,
  startFrom = glassGraphDefaults.startFrom!,
}) => {
  const frame = useCurrentFrame();

  // Card in and out.
  const enter = interpolate(frame, [0, 8], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const exit = interpolate(frame, [80, 90], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const opacity = enter * (1 - exit);
  const y = (1 - enter) * 60 + exit * 30;

  // Number and line share one eased progress, slowing down at the end.
  const progress = interpolate(frame, [8, 60], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const value = from + (to - from) * progress;

  const samples = samplePath(points);
  const shown = samples.filter((p) => p.x <= progress * GRAPH.w + 0.01);
  const tip = shown[shown.length - 1];
  const line = shown.map((p, i) => `${i ? "L" : "M"}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");
  const area = `${line} L${tip.x.toFixed(1)},${GRAPH.h} L0,${GRAPH.h} Z`;

  // Dot pulses once when the line reaches the end.
  const pulse = interpolate(frame, [60, 76], [0, 1], { ...clamp, easing: Easing.out(Easing.quad) });
  const pulseOn = frame >= 60;
  const dotScale = pulseOn ? 1 + 0.35 * Math.sin(Math.min(1, (frame - 60) / 10) * Math.PI) : 1;

  return (
    <AbsoluteFill>
      <Footage framing={{ startFrom, centerX: 0.58 }} />
      <div
        style={{
          position: "absolute",
          left: (1080 - CARD.w) / 2,
          top: CARD.top,
          width: CARD.w,
          height: CARD.h,
          boxSizing: "border-box",
          padding: "40px 40px 36px",
          borderRadius: 36,
          backgroundColor: "rgba(255, 255, 255, 0.10)",
          backdropFilter: "blur(40px) saturate(1.3)",
          border: "2px solid rgba(255, 255, 255, 0.35)",
          boxShadow: "0 30px 70px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.25)",
          fontFamily: UI_FONT,
          opacity,
          transform: `translateY(${y}px)`,
        }}
      >
        <div style={{ color: "rgba(235, 235, 240, 0.8)", fontSize: 30, fontWeight: 500 }}>{title}</div>
        <div
          style={{
            color: "white",
            fontSize: 104,
            fontWeight: 700,
            lineHeight: 1.05,
            marginTop: 6,
            fontVariantNumeric: "tabular-nums",
            textShadow: "0 2px 16px rgba(0, 0, 0, 0.25)",
          }}
        >
          {formatCount(value)}
        </div>
        <svg
          width={GRAPH.w}
          height={GRAPH.h + 20}
          viewBox={`0 -10 ${GRAPH.w} ${GRAPH.h + 20}`}
          style={{ position: "absolute", left: 40, bottom: 34, overflow: "visible" }}
        >
          <defs>
            <linearGradient id="gg-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={ORANGE} stopOpacity={0.6} />
              <stop offset="100%" stopColor={ORANGE} stopOpacity={0} />
            </linearGradient>
            <filter id="gg-glow" x="-20%" y="-50%" width="140%" height="200%">
              <feGaussianBlur stdDeviation="6" result="b" />
              <feMerge>
                <feMergeNode in="b" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          {progress > 0 ? (
            <>
              <path d={area} fill="url(#gg-fill)" />
              <path
                d={line}
                fill="none"
                stroke={ORANGE}
                strokeWidth={6}
                strokeLinecap="round"
                strokeLinejoin="round"
                filter="url(#gg-glow)"
              />
              {pulseOn ? (
                <circle
                  cx={tip.x}
                  cy={tip.y}
                  r={12 + pulse * 30}
                  fill="none"
                  stroke={ORANGE}
                  strokeWidth={4}
                  opacity={0.8 * (1 - pulse)}
                />
              ) : null}
              <circle cx={tip.x} cy={tip.y} r={16 * dotScale} fill={ORANGE} opacity={0.35} filter="url(#gg-glow)" />
              <circle cx={tip.x} cy={tip.y} r={9 * dotScale} fill="#FFE3D6" stroke={ORANGE} strokeWidth={4} />
            </>
          ) : null}
        </svg>
      </div>
    </AbsoluteFill>
  );
};
