import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { TIERS, type ScenePlan, type Tier } from "../../shared/plan";
import { boardStateAt, FLY_SECONDS } from "../../shared/tierboard";
import { easeIn, enter, settle, shadow, toFrame } from "../anim";
import { ObjectCallout } from "./ObjectCallout";

export function boardGeometry(plan: ScenePlan) {
  const sa = plan.style.safeArea;
  const top = plan.style.boardSpeakerHeight + 28;
  const rowH = (sa.y1 - top) / TIERS.length;
  const label = rowH - 10;
  const x0 = sa.x0;
  const itemX0 = x0 + label + 16;
  const itemSize = label - 8;
  return { top, rowH, label, x0, itemX0, itemSize, right: sa.x1, stage: { x: (itemX0 + sa.x1) / 2, y: top + rowH * 3 } };
}

/** S-F board under the speaker. The active item is introduced large, then flies to its row and stays. */
export const TierBoard: React.FC<{ plan: ScenePlan; mediaBase: string }> = ({ plan, mediaBase }) => {
  const frame = useCurrentFrame();
  const fps = plan.fps;
  const t = frame / fps;
  const c = plan.style.colors as Record<string, string>;
  const tiers = c.tiers as unknown as Record<string, string>;
  const board = plan.tierBoard!;
  const st = boardStateAt(board.events, t);
  const g = boardGeometry(plan);
  const spacing = (tier: string) => Math.min(g.itemSize * 1.9 + 10, (g.right - g.itemX0) / Math.max(1, st.rows[tier as Tier].length));
  const slotX = (tier: string, slot: number) => g.itemX0 + slot * spacing(tier);
  const rowY = (tier: string) => g.top + TIERS.indexOf(tier as never) * g.rowH;
  const firstIntro = board.events.length ? Math.min(...board.events.map((e) => e.introAt)) : Infinity;
  const titleOpacity = board.title ? 1 - enter(frame, toFrame(firstIntro, fps) - 6, 6) : 0;

  return (
    <div style={{ position: "absolute", inset: 0 }}>
      {TIERS.map((tier) => {
        const y = rowY(tier);
        const landing = st.active && st.active.event.tier === tier && st.active.phase === "flying";
        const recent = board.events.find((e) => e.tier === tier && t >= e.placeAt && t < e.placeAt + FLY_SECONDS + 0.25);
        const flash = landing || recent ? 1 : 0;
        return (
          <React.Fragment key={tier}>
            <div style={{ position: "absolute", left: g.x0, top: y, width: g.right - g.x0, height: g.label, borderRadius: 14, background: "rgba(255,255,255,0.035)",
              border: "1px solid rgba(255,255,255,0.05)" }} />
            <div style={{ position: "absolute", left: g.x0, top: y, width: g.label, height: g.label, borderRadius: 14, background: tiers[tier],
              border: tier === "F" ? `2px solid ${c.accent}` : "none", display: "flex", alignItems: "center", justifyContent: "center",
              fontFamily: plan.fonts.heading.family, fontSize: g.label * 0.62, color: tier === "F" ? c.accent : ["S", "A", "B"].includes(tier) ? "#141414" : "#fff",
              boxShadow: flash ? `0 0 0 4px ${c.accent}, ${shadow.soft}` : shadow.soft, filter: flash ? "brightness(1.25)" : "none" }}>
              {tier}
            </div>
            {st.rows[tier].filter((p) => !(st.active && st.active.phase === "flying" && st.active.event.id === p.id)).map((p) => (
              <div key={p.id} style={{ position: "absolute", left: slotX(tier, p.slot), top: y + (g.label - g.itemSize) / 2, height: g.itemSize, display: "flex", alignItems: "center" }}>
                <ObjectCallout plan={plan} mediaBase={mediaBase} label={p.item} image={p.image} size={g.itemSize} maxWidth={spacing(tier) - 10} />
              </div>
            ))}
          </React.Fragment>
        );
      })}
      {board.title ? (
        <div style={{ position: "absolute", left: g.itemX0, width: g.right - g.itemX0, top: g.top + g.rowH * 1.6, textAlign: "center", opacity: titleOpacity,
          fontFamily: plan.fonts.heading.family, fontSize: 64, color: c.text, lineHeight: 1 }}>
          {board.title}
        </div>
      ) : null}
      {st.active
        ? (() => {
            const a = st.active!;
            const e = a.event;
            const bigSize = g.rowH * 2.4;
            const introP = settle(frame, fps, toFrame(e.introAt, fps), plan.style.entranceFrames + 2);
            const fly = a.phase === "flying" ? interpolate(a.progress, [0, 1], [0, 1], { easing: easeIn, extrapolateRight: "clamp" }) : 0;
            const tx = slotX(e.tier, a.slot) + (spacing(e.tier) - 10) / 2;
            const ty = rowY(e.tier) + g.label / 2;
            const x = interpolate(fly, [0, 1], [g.stage.x, tx]);
            const y = interpolate(fly, [0, 1], [g.stage.y, ty]);
            const size = interpolate(fly, [0, 1], [bigSize, g.itemSize]);
            return (
              <div style={{ position: "absolute", left: x, top: y, transform: "translate(-50%, -50%)", zIndex: 3 }}>
                <ObjectCallout plan={plan} mediaBase={mediaBase} label={e.item} image={e.image} size={size} progress={introP} maxWidth={interpolate(fly, [0, 1], [g.right - g.itemX0, spacing(e.tier) - 10])} />
              </div>
            );
          })()
        : null}
    </div>
  );
};
