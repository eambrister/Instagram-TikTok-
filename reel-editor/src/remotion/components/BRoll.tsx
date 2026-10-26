import React from "react";
import { AbsoluteFill, OffthreadVideo, Sequence } from "remotion";
import type { ScenePlan } from "../../shared/plan";
import { toFrame } from "../anim";

const GAP = 24; // px between the pinned title and the clip
const MAX_W = 840; // inside x = 120 to 960

/**
 * His own B-roll as a cutaway: the clip sits below the pinned title (so the title never covers it) over a blurred,
 * darkened fill of itself. Muted; the voice and music carry on. Titles and captions draw on top.
 */
export const BRoll: React.FC<{ plan: ScenePlan; mediaBase: string }> = ({ plan, mediaBase }) => {
  const hook = plan.graphics.find((g) => g.kind === "hook");
  return (
    <>
      {plan.broll.map((b, i) => {
        const from = toFrame(b.start, plan.fps);
        const top = hook && hook.end >= b.end ? hook.region.y + hook.region.h + GAP : 0;
        const room = { w: MAX_W, h: plan.height - top - GAP };
        const s = Math.min(room.w / b.width, room.h / b.height);
        const w = b.width * s;
        const h = b.height * s;
        const src = mediaBase + b.url;
        return (
          <Sequence key={i} from={from} durationInFrames={toFrame(b.end, plan.fps) - from} layout="none">
            <AbsoluteFill style={{ overflow: "hidden", background: "#0E0F12" }}>
              <OffthreadVideo src={src} muted playbackRate={b.rate}
                style={{ position: "absolute", inset: -60, width: plan.width + 120, height: plan.height + 120, objectFit: "cover",
                  filter: "blur(40px) brightness(0.55)" }} />
              <OffthreadVideo src={src} muted playbackRate={b.rate}
                style={{ position: "absolute", left: (plan.width - w) / 2, top, width: w, height: h, borderRadius: 28,
                  boxShadow: "0 24px 60px rgba(0,0,0,0.45)" }} />
            </AbsoluteFill>
          </Sequence>
        );
      })}
    </>
  );
};
