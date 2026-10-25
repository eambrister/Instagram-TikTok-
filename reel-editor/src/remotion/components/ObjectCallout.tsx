import React from "react";
import { Img, interpolate } from "remotion";
import type { ScenePlan } from "../../shared/plan";
import { shadow } from "../anim";

/** A supplied (licensed) object photo with a soft drop shadow, or an original typographic chip when none is supplied. */
export const ObjectCallout: React.FC<{
  plan: ScenePlan;
  mediaBase: string;
  label: string;
  image: string | null;
  size: number; // px, longest side
  progress?: number; // 0..1 entrance
  maxWidth?: number;
}> = ({ plan, mediaBase, label, image, size, progress = 1, maxWidth }) => {
  const c = plan.style.colors as Record<string, string>;
  const scale = interpolate(progress, [0, 1], [0.7, 1]);
  if (image) {
    return (
      <Img src={mediaBase + image} style={{ width: Math.min(size, maxWidth ?? size), height: Math.min(size, maxWidth ?? size), objectFit: "contain", transform: `scale(${scale})`, opacity: progress,
        filter: "drop-shadow(0 16px 24px rgba(0,0,0,0.45))" }} />
    );
  }
  const fs = Math.max(18, size * 0.2);
  return (
    <div style={{ maxWidth: maxWidth ?? size * 2.6, boxSizing: "border-box", padding: `${fs * 0.45}px ${fs * 0.8}px`, borderRadius: fs * 0.6, background: `linear-gradient(160deg, ${c.card}, ${c.panelBottom})`,
      border: `2px solid ${c.cardBorder}`, boxShadow: shadow.soft, fontFamily: plan.fonts.heading.family, fontSize: fs, color: c.text, whiteSpace: "nowrap",
      overflow: "hidden", textOverflow: "ellipsis", transform: `scale(${scale})`, opacity: progress, textTransform: "uppercase" }}>
      {label}
    </div>
  );
};
