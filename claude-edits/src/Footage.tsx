import React from "react";
import { AbsoluteFill, Img, OffthreadVideo, staticFile } from "remotion";
import {
  CLIP_HEIGHT,
  CLIP_WIDTH,
  FRAME_CENTER_X,
  FRAME_SOURCE_WIDTH,
  AUDIT,
  HEIGHT,
  SOURCE_CLIP,
  WIDTH,
} from "./settings";

export type Framing = {
  // First frame of talking.mp4 to use (30 fps). A wall plate must exist for it: tools/make_plate.py.
  startFrom: number;
  // Use the wall plate made for this frame instead (so one section shares one plate).
  plateFrom?: number;
  centerX?: number;
  sourceWidth?: number;
};

export type Box = { x: number; y: number; w: number; h: number };

const SEAM = 16; // px where the top of the clip blends into the wall plate

// Where the clip sits in the vertical frame.
export const clipBox = ({ centerX = FRAME_CENTER_X, sourceWidth = FRAME_SOURCE_WIDTH }: Framing): Box => {
  const s = WIDTH / sourceWidth;
  const w = CLIP_WIDTH * s;
  const h = CLIP_HEIGHT * s;
  const x = Math.min(0, Math.max(WIDTH - w, WIDTH / 2 - centerX * w));
  return { x, y: HEIGHT - h, w, h };
};

export const boxStyle = (b: Box): React.CSSProperties => ({
  position: "absolute",
  left: b.x,
  top: b.y,
  width: b.w,
  height: b.h,
});

// Plate for the wall above the clip.
const WallPlate: React.FC<{ framing: Framing; box: Box }> = ({ framing, box }) => (
  <Img
    src={staticFile(`plates/plate_${framing.plateFrom ?? framing.startFrom}.png`)}
    style={{ position: "absolute", left: box.x, top: 0, width: box.w, height: box.y + SEAM * 2 }}
  />
);

// The clip framed for vertical video, with wall filling the space above it.
export const Footage: React.FC<{ framing: Framing; muted?: boolean; style?: React.CSSProperties }> = ({
  framing,
  muted = true,
  style,
}) => {
  const box = clipBox(framing);
  if (AUDIT) return null;
  return (
    <AbsoluteFill style={{ backgroundColor: "#ccc", ...style }}>
      <WallPlate framing={framing} box={box} />
      <OffthreadVideo
        src={staticFile(SOURCE_CLIP)}
        startFrom={framing.startFrom}
        muted={muted}
        style={{
          ...boxStyle(box),
          maskImage: `linear-gradient(to bottom, transparent 0px, black ${SEAM}px)`,
        }}
      />
    </AbsoluteFill>
  );
};

