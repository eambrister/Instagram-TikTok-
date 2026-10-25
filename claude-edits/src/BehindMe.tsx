import React, { useEffect, useState } from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  cancelRender,
  continueRender,
  delayRender,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Footage, Framing, boxStyle, clipBox } from "./Footage";
import { AUDIT, SOURCE_CLIP } from "./settings";

type MaskMeta = { fps: number; frameCount: number; frameTimes?: number[] };

// Index of the last mask frame shown at or before time t (seconds), matching what the video shows.
const maskIndexAt = (meta: MaskMeta, t: number) => {
  const times = meta.frameTimes;
  if (!times || times.length === 0) {
    return Math.min(meta.frameCount - 1, Math.max(0, Math.floor(t * meta.fps + 1e-3)));
  }
  let lo = 0;
  let hi = times.length - 1;
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1;
    if (times[mid] <= t + 1e-4) lo = mid;
    else hi = mid - 1;
  }
  return lo;
};

const maskFrameUrl = (maskDir: string, index: number) =>
  staticFile(`${maskDir}/frames/mask_${String(index).padStart(5, "0")}.png`);

// Loads the mask's meta.json once.
const useMaskMeta = (maskDir: string) => {
  const [meta, setMeta] = useState<MaskMeta | null>(null);
  const [handle] = useState(() => delayRender(`Loading ${maskDir}/meta.json`));
  useEffect(() => {
    fetch(staticFile(`${maskDir}/meta.json`))
      .then((r) => {
        if (!r.ok) throw new Error(`No mask found in public/${maskDir}. Run tools/make_mask.py first.`);
        return r.json();
      })
      .then((m: MaskMeta) => {
        setMeta(m);
        continueRender(handle);
      })
      .catch((err) => cancelRender(err));
  }, [handle, maskDir]);
  return meta;
};

// Holds the frame until this frame's mask image is loaded, so the cutout is never missing.
const useLoadedImage = (url: string | null) => {
  useEffect(() => {
    if (!url) return;
    const handle = delayRender(`Loading mask ${url}`);
    let done = false;
    const finish = () => {
      if (!done) {
        done = true;
        continueRender(handle);
      }
    };
    const img = new Image();
    img.src = url;
    img
      .decode()
      .then(finish)
      .catch((err) => cancelRender(err));
    return finish;
  }, [url]);
};

/**
 * The person mask for the current frame of a framed clip: where the clip sits, and a CSS mask
 * style that keeps only the person when applied to an element covering `box`.
 */
export const usePersonMask = (framing: Framing, maskDir = "mask") => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const meta = useMaskMeta(maskDir);
  const box = clipBox(framing);

  // Pick the mask frame showing the same moment of the clip as the video layer.
  const index = meta ? maskIndexAt(meta, (frame + framing.startFrom) / fps) : null;
  const maskUrl = index === null ? null : maskFrameUrl(maskDir, index);
  useLoadedImage(maskUrl);

  const maskStyle: React.CSSProperties = maskUrl
    ? {
        maskImage: `url("${maskUrl}")`,
        maskMode: "luminance",
        maskSize: "100% 100%",
        maskRepeat: "no-repeat",
      }
    : { visibility: "hidden" };
  return { box, maskStyle };
};

/**
 * Draws `children` behind the person and in front of the background.
 *
 * Layers, bottom to top: the framed clip (with wall above it), the graphic, then the person
 * cut out of the clip with the mask in public/mask (person white, background black).
 * The clip's frames and the mask's frames are matched by timestamp.
 */
export const BehindMe: React.FC<{
  children?: React.ReactNode;
  framing: Framing;
  maskDir?: string;
  muted?: boolean;
}> = ({ children, framing, maskDir = "mask", muted = true }) => {
  const { box, maskStyle } = usePersonMask(framing, maskDir);

  return (
    <AbsoluteFill>
      <Footage framing={framing} muted={muted} />
      <AbsoluteFill>{children}</AbsoluteFill>
      {AUDIT ? null : (
        <OffthreadVideo
          src={staticFile(SOURCE_CLIP)}
          startFrom={framing.startFrom}
          muted
          style={{ ...boxStyle(box), ...maskStyle }}
        />
      )}
    </AbsoluteFill>
  );
};
