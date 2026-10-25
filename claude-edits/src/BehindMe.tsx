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
import { SOURCE_CLIP } from "./settings";

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
 * Draws `children` behind the person and in front of the background.
 *
 * Layers, bottom to top: the clip, the graphic, then the person cut out of the clip
 * with the mask in public/mask (person white, background black).
 *
 * startFrom: skip this many frames of the clip (in this composition's fps), like OffthreadVideo.
 * position: which part of the clip to show when it's cropped to fill the frame, as CSS
 *   object-position, e.g. "70% 50%" to frame someone right of centre in a horizontal clip.
 */
export const BehindMe: React.FC<{
  children?: React.ReactNode;
  src?: string;
  maskDir?: string;
  startFrom?: number;
  muted?: boolean;
  position?: string;
}> = ({
  children,
  src = staticFile(SOURCE_CLIP),
  maskDir = "mask",
  startFrom = 0,
  muted = false,
  position = "50% 50%",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const meta = useMaskMeta(maskDir);

  // Pick the mask frame showing the same moment of the clip as the video layer.
  const index = meta ? maskIndexAt(meta, (frame + startFrom) / fps) : null;
  const maskUrl = index === null ? null : maskFrameUrl(maskDir, index);
  useLoadedImage(maskUrl);

  const videoStyle: React.CSSProperties = {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    objectPosition: position,
  };
  const maskStyle: React.CSSProperties = maskUrl
    ? {
        maskImage: `url("${maskUrl}")`,
        maskMode: "luminance",
        maskSize: "cover",
        maskPosition: position,
        maskRepeat: "no-repeat",
      }
    : { visibility: "hidden" };

  return (
    <AbsoluteFill>
      <OffthreadVideo src={src} startFrom={startFrom} muted={muted} style={videoStyle} />
      <AbsoluteFill>{children}</AbsoluteFill>
      <AbsoluteFill style={maskStyle}>
        <OffthreadVideo src={src} startFrom={startFrom} muted style={videoStyle} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
