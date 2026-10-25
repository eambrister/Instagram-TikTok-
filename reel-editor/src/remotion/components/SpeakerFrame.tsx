import React from "react";
import { Img, OffthreadVideo, Sequence, useCurrentFrame } from "remotion";
import type { ScenePlan } from "../../shared/plan";
import { layoutAt, speakerFrame, speakerTransform, zoomAt } from "../../shared/framing";
import { segmentIndexAtOut } from "../../shared/timeline";
import { toFrame } from "../anim";

const SEAM = 16; // px over which the top of a backed-out clip blends into the wall plate

/** Eddie's real footage: one Sequence per kept segment, framed on the face, zoomed by the plan. */
export const SpeakerFrame: React.FC<{ plan: ScenePlan; mediaBase: string }> = ({ plan, mediaBase }) => {
  const frame = useCurrentFrame();
  const t = frame / plan.fps;
  const kind = layoutAt(plan, t);
  const f = speakerFrame(kind, plan.width, plan.height, plan.style.panelHeight, plan.style.boardSpeakerHeight, plan.style.fullWidthFraction);
  const seg = plan.segments[segmentIndexAtOut(plan.segments, t)];
  const zoom = zoomAt(plan.zooms, t, plan.fps, plan.source.maxZoom);
  const tr = speakerTransform(f, plan.source.width, plan.source.height, seg.focus, zoom);
  const src = mediaBase + plan.source.url;
  // Backed out: the clip doesn't reach the top, so matched wall fills above it and the clip's top edge blends in.
  const plate = tr.ty > 0 && plan.source.plateUrl ? mediaBase + plan.source.plateUrl : null;
  return (
    <div style={{ position: "absolute", left: f.x, top: f.y, width: f.w, height: f.h, overflow: "hidden", background: "#000" }}>
      {plate ? (
        <Img src={plate} style={{ position: "absolute", left: tr.tx, top: 0, width: tr.w, height: tr.ty + SEAM * 2, maxWidth: "none" }} />
      ) : null}
      {plan.segments.map((s, i) => {
        const from = toFrame(s.outStart, plan.fps);
        const dur = toFrame(s.outEnd, plan.fps) - from;
        return (
          <Sequence key={i} from={from} durationInFrames={dur} layout="none">
            <OffthreadVideo
              src={src}
              muted
              trimBefore={toFrame(s.srcStart, plan.fps)}
              style={{
                position: "absolute", left: tr.tx, top: tr.ty, width: tr.w, height: tr.h, maxWidth: "none",
                maskImage: plate ? `linear-gradient(to bottom, transparent 0px, black ${SEAM}px)` : undefined,
              }}
            />
          </Sequence>
        );
      })}
    </div>
  );
};
