import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import type { Graphic, ScenePlan } from "../../shared/plan";
import { enter, exit, settle, shadow, toFrame } from "../anim";
import { wrapFit } from "../text";

type Props = { plan: ScenePlan; g: Extract<Graphic, { kind: "card" | "hook" }> };

/** 2.5D card: perspective settle-in, layered shadows, optional label pill. Hook titles reveal word-by-word as spoken. */
export const FloatingCard: React.FC<Props> = ({ plan, g }) => {
  const frame = useCurrentFrame();
  const fps = plan.fps;
  const c = plan.style.colors as Record<string, string>;
  const f0 = toFrame(g.start, fps);
  const f1 = toFrame(g.end, fps);
  const n = plan.style.entranceFrames;
  const s = settle(frame, fps, f0, n + 4);
  const out = exit(frame, f1, 6);
  const isHook = g.kind === "hook";
  const text = isHook ? g.data.title : g.data.text;
  const label = isHook ? g.data.kicker : g.data.label;
  const pad = 34;
  const inner = { w: g.region.w - pad * 2, h: g.region.h - pad * 2 - (label ? 56 : 0) };
  const fit = wrapFit(text, plan.fonts.heading.family, inner, isHook ? 116 : 92, 44, 3, 1.02);
  const words = text.split(/\s+/);
  const times = isHook ? g.data.times : [];
  const highlight = new Set(isHook ? g.data.highlight : []);
  let wi = 0;
  return (
    <div style={{ position: "absolute", left: g.region.x, top: g.region.y, width: g.region.w, height: g.region.h, perspective: 1400 }}>
      <div
        style={{
          width: "100%",
          height: "100%",
          boxSizing: "border-box",
          padding: pad,
          borderRadius: 30,
          background: isHook ? "transparent" : `linear-gradient(160deg, ${c.card} 0%, ${c.panelBottom} 100%)`,
          border: isHook ? "none" : `1.5px solid ${c.cardBorder}`,
          boxShadow: isHook ? "none" : shadow.card,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          gap: 14,
          opacity: Math.min(interpolate(s, [0, 0.5], [0, 1], { extrapolateRight: "clamp" }), out),
          transform: `translateY(${interpolate(s, [0, 1], [60, 0]) - (1 - out) * 24}px) rotateX(${interpolate(s, [0, 1], [22, 0])}deg) scale(${interpolate(s, [0, 1], [0.9, 1])})`,
          transformOrigin: "50% 100%",
        }}
      >
        {label ? (
          <div style={{ fontFamily: plan.fonts.body.family, fontSize: 30, letterSpacing: 2, color: "#111", background: c.accent, padding: "8px 18px", borderRadius: 999,
            opacity: enter(frame, f0 + 3, n) }}>
            {label}
          </div>
        ) : null}
        <div style={{ textAlign: "center" }}>
          {fit.lines.map((line, li) => (
            <div key={li} style={{ fontFamily: plan.fonts.heading.family, fontSize: fit.size, lineHeight: 1.02, color: c.text, whiteSpace: "nowrap",
              textShadow: isHook ? "0 6px 18px rgba(0,0,0,0.55)" : "none", WebkitTextStroke: isHook ? `10px ${c.captionOutline}` : undefined, paintOrder: "stroke fill" }}>
              {line.split(" ").map((w, k) => {
                const idx = wi++;
                const at = times[idx];
                const shown = at === undefined || frame >= toFrame(at, fps);
                if (!shown) return null;
                const color = highlight.has(idx) ? c.accent : c.text;
                return (
                  <span key={k} style={{ color, marginRight: k < line.split(" ").length - 1 ? "0.22em" : 0 }}>
                    {w}
                  </span>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
