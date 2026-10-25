import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import type { ScenePlan } from "../../shared/plan";
import { enter, toFrame } from "../anim";

/** Phrase captions: words appear as spoken (layout stays fixed), active/emphasis word in highlight colour. */
export const CaptionTrack: React.FC<{ plan: ScenePlan }> = ({ plan }) => {
  const frame = useCurrentFrame();
  const fps = plan.fps;
  const t = frame / fps;
  const cap = plan.captions.find((c) => !c.suppressed && t >= c.start && t < c.end);
  if (!cap) return null;
  const c = plan.style.colors as Record<string, string>;
  const mode = plan.style.captionHighlight;
  const f0 = toFrame(cap.start, fps);
  const p = enter(frame, f0, plan.style.captionEntranceFrames);
  const scale = interpolate(p, [0, 1], [0.93, 1]);
  const dy = interpolate(p, [0, 1], [12, 0]);
  let active = -1;
  cap.words.forEach((w, i) => {
    if (w.start <= t + 1e-6) active = i;
  });
  const lineH = cap.fontSize * 1.1;
  return (
    <div
      style={{
        position: "absolute",
        left: cap.box.x - 40,
        top: cap.box.y,
        width: cap.box.w + 80,
        height: cap.box.h,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        transform: `translateY(${dy}px) scale(${scale})`,
        opacity: interpolate(p, [0, 0.4], [0, 1], { extrapolateRight: "clamp" }),
      }}
    >
      {cap.lines.map((line, li) => (
        <div key={li} style={{ display: "flex", gap: cap.fontSize * 0.26, height: lineH, alignItems: "center", whiteSpace: "nowrap" }}>
          {line.filter((wi) => frame >= toFrame(cap.words[wi].start, fps)).map((wi) => {
            const w = cap.words[wi];
            const wf = toFrame(w.start, fps);
            const shown = frame >= wf;
            const isActive = wi === active && mode.includes("active");
            const isEmph = w.emphasis && mode.includes("emphasis") && shown;
            return (
              <span
                key={wi}
                style={{
                  fontFamily: plan.fonts.caption.family,
                  fontSize: cap.fontSize,
                  lineHeight: 1,
                  letterSpacing: 0,
                  color: isActive || isEmph ? c.captionHighlight : c.captionText,
                  WebkitTextStroke: `${plan.style.captionStrokePx}px ${c.captionOutline}`,
                  paintOrder: "stroke fill",
                  textShadow: "0 5px 14px rgba(0,0,0,0.45)",
                  opacity: shown ? interpolate(frame, [wf, wf + 2], [0.35, 1], { extrapolateRight: "clamp" }) : 0,
                  transform: `scale(${interpolate(frame, [wf, wf + 3], [0.9, 1], { extrapolateRight: "clamp" })})`,
                }}
              >
                {w.text}
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};
