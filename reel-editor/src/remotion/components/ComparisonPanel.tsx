import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import type { Graphic, ScenePlan } from "../../shared/plan";
import { exit, settle, shadow, toFrame } from "../anim";
import { wrapFit } from "../text";

/** Two overlapping 2.5D cards (Eddie's own words on each side) with a joiner pill. */
export const ComparisonPanel: React.FC<{ plan: ScenePlan; g: Extract<Graphic, { kind: "comparison" }> }> = ({ plan, g }) => {
  const frame = useCurrentFrame();
  const fps = plan.fps;
  const c = plan.style.colors as Record<string, string>;
  const f0 = toFrame(g.start, fps);
  const f1 = toFrame(g.end, fps);
  const n = plan.style.entranceFrames;
  const out = exit(frame, f1, 6);
  const cardW = g.region.w * 0.47;
  const cardH = Math.min(g.region.h * 0.8, 420);
  const side = (text: string, i: number) => {
    const s = settle(frame, fps, f0 + i * 5, n + 4);
    const fit = wrapFit(text, plan.fonts.heading.family, { w: cardW - 50, h: cardH - 60 }, 84, 38, 3);
    const dir = i === 0 ? -1 : 1;
    return (
      <div key={i} style={{ position: "absolute", top: (g.region.h - cardH) / 2 + (i ? 26 : 0), left: i === 0 ? 0 : g.region.w - cardW, width: cardW, height: cardH,
        borderRadius: 28, boxSizing: "border-box", padding: 25, display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center",
        background: `linear-gradient(160deg, ${c.card}, ${c.panelBottom})`, border: `2px solid ${i ? c.accent : c.cardBorder}`, boxShadow: shadow.card,
        opacity: Math.min(s, out), transform: `translateX(${dir * interpolate(s, [0, 1], [70, 0])}px) rotateY(${dir * -interpolate(s, [0, 1], [24, 9])}deg)` }}>
        <div>
          {fit.lines.map((l, k) => (
            <div key={k} style={{ fontFamily: plan.fonts.heading.family, fontSize: fit.size, lineHeight: 1.02, color: i ? c.accent : c.text, whiteSpace: "nowrap" }}>{l}</div>
          ))}
        </div>
      </div>
    );
  };
  const pill = settle(frame, fps, f0 + 9, n);
  return (
    <div style={{ position: "absolute", left: g.region.x, top: g.region.y, width: g.region.w, height: g.region.h, perspective: 1300 }}>
      {side(g.data.left, 0)}
      {side(g.data.right, 1)}
      <div style={{ position: "absolute", left: g.region.w / 2, top: g.region.h / 2 + 13, transform: `translate(-50%, -50%) scale(${interpolate(pill, [0, 1], [0.6, 1])})`,
        opacity: Math.min(pill, out), background: c.accent, color: "#111", fontFamily: plan.fonts.heading.family, fontSize: 40, padding: "10px 22px", borderRadius: 999,
        boxShadow: shadow.soft, whiteSpace: "nowrap", zIndex: 2 }}>
        {g.data.joiner}
      </div>
    </div>
  );
};
