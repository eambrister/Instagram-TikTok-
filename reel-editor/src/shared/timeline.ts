// Edit decision list -> output timeline. Pure functions; audio, video, captions and graphics
// all use the same frame-snapped segments so nothing keeps source timestamps after a cut.

export type Interval = { start: number; end: number };
export type TimelineSegment = { srcStart: number; srcEnd: number; outStart: number; outEnd: number };

const EPS = 1e-6;

/** Merge overlapping/adjacent intervals and drop empties. */
export function normalizeIntervals(iv: Interval[], minGap = 0): Interval[] {
  const s = iv.filter((i) => i.end - i.start > EPS).sort((a, b) => a.start - b.start);
  const out: Interval[] = [];
  for (const i of s) {
    const last = out[out.length - 1];
    if (last && i.start <= last.end + minGap) last.end = Math.max(last.end, i.end);
    else out.push({ ...i });
  }
  return out;
}

/** Subtract `cuts` from `keep`. */
export function subtract(keep: Interval[], cuts: Interval[]): Interval[] {
  let cur = normalizeIntervals(keep);
  for (const c of normalizeIntervals(cuts)) {
    const next: Interval[] = [];
    for (const k of cur) {
      if (c.end <= k.start || c.start >= k.end) next.push(k);
      else {
        if (c.start > k.start) next.push({ start: k.start, end: c.start });
        if (c.end < k.end) next.push({ start: c.end, end: k.end });
      }
    }
    cur = next;
  }
  return cur.filter((i) => i.end - i.start > EPS);
}

/** Snap kept source intervals to whole frames and lay them end to end on the output timeline. */
export function buildSegments(keep: Interval[], fps: number, minFrames = 3): TimelineSegment[] {
  const segs: TimelineSegment[] = [];
  let outFrame = 0;
  for (const k of normalizeIntervals(keep)) {
    const f0 = Math.round(k.start * fps);
    const f1 = Math.round(k.end * fps);
    if (f1 - f0 < minFrames) continue;
    segs.push({ srcStart: f0 / fps, srcEnd: f1 / fps, outStart: outFrame / fps, outEnd: (outFrame + f1 - f0) / fps });
    outFrame += f1 - f0;
  }
  return segs;
}

export function outputDuration(segs: TimelineSegment[]): number {
  return segs.length ? segs[segs.length - 1].outEnd : 0;
}

/** Source time -> output time, or null when the moment was cut. */
export function srcToOut(segs: TimelineSegment[], t: number): number | null {
  for (const s of segs) if (t >= s.srcStart - EPS && t <= s.srcEnd + EPS) return s.outStart + (t - s.srcStart);
  return null;
}

/** Output time -> source time (always defined inside the output range). */
export function outToSrc(segs: TimelineSegment[], t: number): number {
  for (const s of segs) if (t >= s.outStart - EPS && t < s.outEnd - EPS) return s.srcStart + (t - s.outStart);
  const last = segs[segs.length - 1];
  return last.srcEnd;
}

export function segmentIndexAtOut(segs: TimelineSegment[], t: number): number {
  for (let i = 0; i < segs.length; i++) if (t >= segs[i].outStart - EPS && t < segs[i].outEnd - EPS) return i;
  return segs.length - 1;
}

/**
 * Remap a timed item (word, cue) onto the output timeline. Items whose midpoint was cut are dropped;
 * survivors are clamped to the segment that contains their midpoint so they never straddle a cut.
 */
export function remapSpan<T extends { start: number; end: number }>(segs: TimelineSegment[], item: T): T | null {
  const mid = (item.start + item.end) / 2;
  const seg = segs.find((s) => mid >= s.srcStart - EPS && mid <= s.srcEnd + EPS);
  if (!seg) return null;
  const a = Math.max(item.start, seg.srcStart);
  const b = Math.min(item.end, seg.srcEnd);
  return { ...item, start: seg.outStart + (a - seg.srcStart), end: seg.outStart + (b - seg.srcStart) };
}

/** Output-time positions of every cut (segment joins). */
export function cutPoints(segs: TimelineSegment[]): number[] {
  return segs.slice(1).map((s) => s.outStart);
}

/** Validation helper: contiguous output, monotonic source, positive durations. */
export function timelineProblems(segs: TimelineSegment[], fps: number): string[] {
  const p: string[] = [];
  if (!segs.length) p.push("timeline has no segments");
  segs.forEach((s, i) => {
    if (s.srcEnd <= s.srcStart) p.push(`segment ${i} has non-positive source duration`);
    if (Math.abs(s.srcEnd - s.srcStart - (s.outEnd - s.outStart)) > 0.5 / fps) p.push(`segment ${i} source/output durations differ`);
    if (i === 0 && Math.abs(s.outStart) > EPS) p.push("timeline does not start at 0");
    if (i > 0) {
      const prev = segs[i - 1];
      if (Math.abs(s.outStart - prev.outEnd) > EPS) p.push(`gap/overlap between output segments ${i - 1} and ${i}`);
      if (s.srcStart < prev.srcEnd - EPS) p.push(`segment ${i} source overlaps previous segment`);
    }
    for (const v of [s.srcStart, s.srcEnd, s.outStart, s.outEnd])
      if (Math.abs(v * fps - Math.round(v * fps)) > 1e-4) p.push(`segment ${i} is not frame-aligned`);
  });
  return p;
}
