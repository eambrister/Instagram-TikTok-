// Speaker framing shared by planner (collision checks) and renderer, so both agree on where the face is.
import type { ScenePlan, Segment, ZoomKey } from "./plan";

// widthFraction: show this share of the source width across the frame (backed-out framing), clip at the bottom.
export type Frame = { x: number; y: number; w: number; h: number; targetY: number; widthFraction?: number | null };

export function speakerFrame(kind: "full" | "panel-top" | "board-bottom", W: number, H: number, panelH: number, boardSpeakerH: number,
  fullWidthFraction: number | null = null): Frame {
  if (kind === "panel-top") return { x: 0, y: panelH, w: W, h: H - panelH, targetY: 0.4 };
  if (kind === "board-bottom") return { x: 0, y: 0, w: W, h: boardSpeakerH, targetY: 0.42 };
  return { x: 0, y: 0, w: W, h: H, targetY: 0.34, widthFraction: fullWidthFraction };
}

export const DEFAULT_FOCUS = { cx: 0.5, cy: 0.38, w: 0.3 };

/**
 * Cover-fit the proxy into the frame, zoomed, with the face placed at targetY and edges clamped.
 * With a widthFraction the shot is backed out instead: it sits on the bottom edge, zooms about the face,
 * and the space above it is left for the wall plate.
 */
export function speakerTransform(f: Frame, pw: number, ph: number, focus: Segment["focus"], zoom: number) {
  const fc = focus ?? DEFAULT_FOCUS;
  const cover = Math.max(f.w / pw, f.h / ph);
  if (f.widthFraction && f.w / (pw * f.widthFraction) < cover) {
    const s0 = f.w / (pw * f.widthFraction);
    const s = s0 * zoom;
    const w = pw * s;
    const h = ph * s;
    const tx = Math.min(0, Math.max(f.w - w, f.w / 2 - fc.cx * w));
    // Bottom-aligned at zoom 1; zooming keeps the face where it was, so the bottom edge stays covered.
    const faceY = f.h - ph * s0 + fc.cy * ph * s0;
    const ty = faceY - fc.cy * h;
    return { s, tx, ty, w, h };
  }
  const s = cover * zoom;
  const w = pw * s;
  const h = ph * s;
  let tx = f.w / 2 - fc.cx * w;
  let ty = f.h * f.targetY - fc.cy * h;
  tx = Math.min(0, Math.max(f.w - w, tx));
  ty = Math.min(0, Math.max(f.h - h, ty));
  return { s, tx, ty, w, h };
}

/** Face rectangle in output pixels (approximate: Haar box padded to head size). */
export function faceRect(f: Frame, pw: number, ph: number, focus: Segment["focus"], zoom: number) {
  if (!focus) return null;
  const t = speakerTransform(f, pw, ph, focus, zoom);
  const fw = focus.w * t.w * 1.15;
  const fh = fw * 1.35;
  const cx = f.x + t.tx + focus.cx * t.w;
  const cy = f.y + t.ty + focus.cy * t.h;
  return { x: cx - fw / 2, y: cy - fh * 0.55, w: fw, h: fh };
}

const easeInOut = (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);

/** Deterministic zoom at an output time from the sorted zoom keys. */
export function zoomAt(zooms: ZoomKey[], t: number, fps: number, cap: number) {
  let prev = 1;
  let cur = 1;
  let key: ZoomKey | null = null;
  for (const z of zooms) {
    if (z.at > t + 1e-9) break;
    prev = cur;
    cur = z.scale;
    key = z;
  }
  let v = cur;
  if (key && key.frames > 0) {
    const p = Math.min(1, (t - key.at) / (key.frames / fps));
    v = prev + (cur - prev) * easeInOut(p);
  }
  return Math.min(cap, Math.max(1, v));
}

export function layoutAt(plan: Pick<ScenePlan, "layout">, t: number) {
  for (const l of plan.layout) if (t >= l.start - 1e-9 && t < l.end - 1e-9) return l.kind;
  return plan.layout[plan.layout.length - 1].kind;
}

export function intersects(a: { x: number; y: number; w: number; h: number }, b: { x: number; y: number; w: number; h: number }, pad = 0) {
  return a.x < b.x + b.w + pad && b.x < a.x + a.w + pad && a.y < b.y + b.h + pad && b.y < a.y + a.h + pad;
}
