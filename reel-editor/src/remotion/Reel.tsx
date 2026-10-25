import { loadFont } from "@remotion/fonts";
import React, { useEffect, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, useCurrentFrame } from "remotion";
import type { Graphic, ScenePlan } from "../shared/plan";
import { layoutAt } from "../shared/framing";
import { toFrame } from "./anim";
import { CaptionTrack } from "./components/CaptionTrack";
import { ComparisonPanel } from "./components/ComparisonPanel";
import { Counter } from "./components/Counter";
import { FloatingCard } from "./components/FloatingCard";
import { ObjectCallout } from "./components/ObjectCallout";
import { SpeakerFrame } from "./components/SpeakerFrame";
import { TierBoard } from "./components/TierBoard";

export type ReelProps = { plan: ScenePlan; mediaBase: string };

const Panels: React.FC<{ plan: ScenePlan }> = ({ plan }) => {
  const frame = useCurrentFrame();
  const kind = layoutAt(plan, frame / plan.fps);
  const c = plan.style.colors as Record<string, string>;
  if (kind === "full") return null;
  const top = kind === "panel-top" ? 0 : plan.style.boardSpeakerHeight;
  const height = kind === "panel-top" ? plan.style.panelHeight : plan.height - plan.style.boardSpeakerHeight;
  const seam = kind === "panel-top" ? plan.style.panelHeight : plan.style.boardSpeakerHeight;
  return (
    <>
      <div style={{ position: "absolute", left: 0, top, width: plan.width, height,
        background: `radial-gradient(120% 70% at 50% 0%, rgba(255,216,77,0.07) 0%, rgba(255,216,77,0) 60%), linear-gradient(180deg, ${c.panelTop} 0%, ${c.panelBottom} 100%)` }} />
      <div style={{ position: "absolute", left: 0, top: seam - 1, width: plan.width, height: 2, background: c.accent, opacity: 0.55 }} />
    </>
  );
};

/** Graphics use absolute composition frames (no Sequence offset), so visibility is checked here. */
const GraphicsLayer: React.FC<{ plan: ScenePlan; mediaBase: string }> = ({ plan, mediaBase }) => {
  const frame = useCurrentFrame();
  return (
    <>
      {plan.graphics
        .filter((g) => frame >= toFrame(g.start, plan.fps) && frame < toFrame(g.end, plan.fps))
        .map((g) => (
          <GraphicView key={g.id} plan={plan} g={g} mediaBase={mediaBase} />
        ))}
    </>
  );
};

const GraphicView: React.FC<{ plan: ScenePlan; g: Graphic; mediaBase: string }> = ({ plan, g, mediaBase }) => {
  switch (g.kind) {
    case "hook":
    case "card":
      return <FloatingCard plan={plan} g={g} />;
    case "counter":
      return <Counter plan={plan} g={g} />;
    case "comparison":
      return <ComparisonPanel plan={plan} g={g} />;
    case "object":
      return (
        <div style={{ position: "absolute", left: g.region.x, top: g.region.y, width: g.region.w, height: g.region.h, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <ObjectCallout plan={plan} mediaBase={mediaBase} label={g.data.label} image={g.data.image} size={Math.min(g.region.w, g.region.h) * 0.8} />
        </div>
      );
    default:
      return null;
  }
};

export const Reel: React.FC<ReelProps> = ({ plan, mediaBase }) => {
  const [handle] = useState(() => delayRender("Loading fonts"));
  const [ready, setReady] = useState(false);
  useEffect(() => {
    Promise.all(
      (["heading", "caption", "body"] as const).map((k) => loadFont({ family: plan.fonts[k].family, url: mediaBase + "public/" + plan.fonts[k].url })),
    )
      .then(() => {
        setReady(true);
        continueRender(handle);
      })
      .catch((e) => {
        console.error(e);
        throw e; // a missing font must fail the render, never silently fall back
      });
  }, [handle, mediaBase, plan.fonts]);
  if (!ready) return null;
  return (
    <AbsoluteFill style={{ background: (plan.style.colors as Record<string, string>).panelBottom }}>
      <SpeakerFrame plan={plan} mediaBase={mediaBase} />
      <Panels plan={plan} />
      {plan.tierBoard ? <TierBoard plan={plan} mediaBase={mediaBase} /> : null}
      <GraphicsLayer plan={plan} mediaBase={mediaBase} />
      <CaptionTrack plan={plan} />
    </AbsoluteFill>
  );
};

