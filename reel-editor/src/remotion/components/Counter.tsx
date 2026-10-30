import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import type { Graphic, ScenePlan } from "../../shared/plan";
import { easeOut, enter, exit, settle, shadow, toFrame } from "../anim";

/** Counts up to a value Eddie actually said (or a sourced value); estimates are labelled.
 * Starts when the number is spoken and shows no surrounding text, so nothing is revealed before he says it. */
export const Counter: React.FC<{ plan: ScenePlan; g: Extract<Graphic, { kind: "counter" }> }> = ({ plan, g }) => {
  const frame = useCurrentFrame();
  const fps = plan.fps;
  const c = plan.style.colors as Record<string, string>;
  const f0 = toFrame(g.start, fps);
  const f1 = toFrame(g.end, fps);
  const s = settle(frame, fps, f0, plan.style.entranceFrames + 4);
  const out = exit(frame, f1, 6);
  const countFrames = Math.round(fps * 0.9);
  const p = interpolate(frame, [f0 + 4, f0 + 4 + countFrames], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeOut });
  const value = (g.data.value * p).toLocaleString("en-US", { minimumFractionDigits: g.data.decimals, maximumFractionDigits: g.data.decimals });
  const numSize = Math.min(220, g.region.h * 0.42);
  return (
    <div style={{ position: "absolute", left: g.region.x, top: g.region.y, width: g.region.w, height: g.region.h, perspective: 1400 }}>
      <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 10,
        opacity: Math.min(s, out), transform: `translateY(${interpolate(s, [0, 1], [40, 0])}px) rotateX(${interpolate(s, [0, 1], [16, 0])}deg)` }}>
        <div style={{ fontFamily: plan.fonts.heading.family, fontSize: numSize, lineHeight: 0.95, color: c.accent, fontVariantNumeric: "tabular-nums",
          textShadow: "0 10px 30px rgba(0,0,0,0.5)" }}>{value}</div>
        <div style={{ fontFamily: plan.fonts.heading.family, fontSize: 64, color: c.text, letterSpacing: 2 }}>{g.data.unit}</div>
        <div style={{ width: g.region.w * 0.62, height: 14, borderRadius: 7, background: "rgba(255,255,255,0.12)", overflow: "hidden", boxShadow: shadow.soft }}>
          <div style={{ width: `${p * 100}%`, height: "100%", background: c.accent, borderRadius: 7 }} />
        </div>
        {g.data.estimate ? (
          <div style={{ fontFamily: plan.fonts.body.family, fontSize: 24, color: c.muted, opacity: enter(frame, f0 + 10, 6) }}>ESTIMATE</div>
        ) : null}
      </div>
    </div>
  );
};
