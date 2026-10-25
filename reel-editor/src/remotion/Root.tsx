import React from "react";
import { Composition } from "remotion";
import { Reel, type ReelProps } from "./Reel";

// Studio placeholder; real renders always pass a validated plan via inputProps.
const placeholder = {
  plan: {
    version: 1, jobId: "placeholder", mode: "TALKING_HEAD", modeReason: "", intensity: "medium", fps: 30, width: 1080, height: 1920, duration: 2, preview: null,
    source: { url: "", width: 1080, height: 1920, fps: 30, maxZoom: 1 }, segments: [{ srcStart: 0, srcEnd: 2, outStart: 0, outEnd: 2, focus: null }],
    layout: [{ start: 0, end: 2, kind: "full" }], zooms: [], captions: [], graphics: [], tierBoard: null,
    style: { colors: {}, captionStrokePx: 12, captionHighlight: "active+emphasis", entranceFrames: 8, captionEntranceFrames: 5, panelHeight: 900, boardSpeakerHeight: 900,
      safeArea: { x0: 80, x1: 900, y0: 180, y1: 1500 } },
    fonts: { heading: { url: "fonts/Heading.ttf", family: "EddieHeading", source: "" }, caption: { url: "fonts/Caption.ttf", family: "EddieCaption", source: "" },
      body: { url: "fonts/Body.ttf", family: "EddieBody", source: "" } },
    assets: [], notes: [],
  },
  mediaBase: "",
} as unknown as ReelProps;

export const Root: React.FC = () => (
  <Composition
    id="Reel"
    component={Reel}
    defaultProps={placeholder}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={60}
    calculateMetadata={({ props }) => ({
      fps: props.plan.fps,
      width: props.plan.width,
      height: props.plan.height,
      durationInFrames: Math.max(1, Math.round(props.plan.duration * props.plan.fps)),
    })}
  />
);
