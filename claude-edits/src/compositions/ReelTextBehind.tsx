import React from "react";
import { AbsoluteFill, CalculateMetadataFunction, OffthreadVideo, Sequence, staticFile, useVideoConfig } from "remotion";
import { usePersonMask } from "../BehindMe";
import { boxStyle } from "../Footage";
import { AUDIT, HEIGHT, WIDTH } from "../settings";
import { RisingWord, TEXT_BEHIND_FRAMES } from "./TextBehind";

// TextBehind on a finished vertical edit (from reel-editor): the edit plays with its own sound, and for
// three seconds a word sits behind the speaker's head, using a person mask made from the edit itself.
export type ReelTextBehindProps = {
  video: string; // in public/
  maskDir: string; // in public/, made by tools/make_mask.py from the same video
  word: string;
  at: number; // seconds into the edit
  centerY: number; // middle of the letters, px
};

export const reelTextBehindDefaults: ReelTextBehindProps = {
  video: "reel/final.mp4",
  maskDir: "reel-mask",
  word: "WORD",
  at: 1,
  centerY: 760,
};

const FULL = { x: 0, y: 0, w: WIDTH, h: HEIGHT };

const Person: React.FC<{ video: string; maskDir: string; startFrom: number }> = ({ video, maskDir, startFrom }) => {
  const { box, maskStyle } = usePersonMask({ startFrom }, maskDir, FULL);
  if (AUDIT) return null;
  return <OffthreadVideo src={staticFile(video)} startFrom={startFrom} muted style={{ ...boxStyle(box), ...maskStyle }} />;
};

export const ReelTextBehind: React.FC<ReelTextBehindProps> = ({ video, maskDir, word, at, centerY }) => {
  const { fps } = useVideoConfig();
  const from = Math.round(at * fps);
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {AUDIT ? null : <OffthreadVideo src={staticFile(video)} style={{ width: WIDTH, height: HEIGHT }} />}
      <Sequence from={from} durationInFrames={TEXT_BEHIND_FRAMES} layout="none">
        <RisingWord word={word} centerY={centerY} />
        <Person video={video} maskDir={maskDir} startFrom={from} />
      </Sequence>
    </AbsoluteFill>
  );
};

// As long as the edit itself (from the mask's frame count).
export const reelTextBehindMetadata: CalculateMetadataFunction<ReelTextBehindProps> = async ({ props }) => {
  const meta = await fetch(staticFile(`${props.maskDir}/meta.json`)).then((r) => r.json());
  return { durationInFrames: meta.frameCount };
};
