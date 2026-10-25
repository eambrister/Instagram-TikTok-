// Phrase segmentation (2-5 words, max two lines), emphasis selection, font fitting and SRT export.
import { writeFileSync } from "node:fs";
import type { HouseStyle } from "./config";
import { py, rel, round } from "./util";

export type TWord = { text: string; start: number; end: number; p: number | null };
export type Phrase = { words: (TWord & { emphasis: boolean; uncertain: boolean })[]; start: number; end: number };

const WEAK = new Set(["the", "a", "an", "to", "of", "and", "in", "on", "for", "with", "my", "your", "is", "are", "at", "or", "but", "if", "that", "this", "it", "be", "as", "so"]);
const EMPHASIS = new Set(["never", "always", "stop", "protein", "fiber", "calories", "calorie", "sugar", "fat", "muscle", "discipline",
  "consistency", "consistent", "every", "only", "best", "worst", "mistake", "truth", "no", "not", "don't", "can't", "won't", "exactly",
  "grams", "minutes", "pounds", "lose", "lost", "gain", "results", "habit", "habits", "accountability", "excuse", "excuses", "today",
  "tomorrow", "monday", "garbage", "scam", "lie", "myth", "important", "biggest", "first", "simple", "hard", "easy"]);
const bare = (s: string) => s.toLowerCase().replace(/[^a-z0-9'$%]/g, "");
const isNumber = (s: string) => /\d/.test(s);

function emphasisScore(w: TWord) {
  const b = bare(w.text);
  if (!b || WEAK.has(b)) return 0;
  if (isNumber(b)) return 3;
  if (EMPHASIS.has(b)) return 2;
  if (b.length >= 8) return 1;
  return 0;
}

export function segment(words: TWord[], style: HouseStyle): Phrase[] {
  const c = style.captions;
  const phrases: TWord[][] = [];
  let cur: TWord[] = [];
  const flush = () => cur.length && (phrases.push(cur), (cur = []));
  words.forEach((w, i) => {
    const prev = words[i - 1];
    if (cur.length) {
      const breakBefore =
        cur.length >= c.maxWordsPerPhrase ||
        /[.!?;:,]$/.test(prev.text) ||
        w.start - prev.end >= c.pauseBreakSeconds ||
        w.end - cur[0].start > c.maxPhraseSeconds;
      if (breakBefore) {
        // Don't strand a weak word at the end of a full phrase; carry it forward.
        if (cur.length >= c.maxWordsPerPhrase && cur.length > 1 && WEAK.has(bare(cur[cur.length - 1].text)) && !/[.!?,;:]$/.test(cur[cur.length - 1].text)) {
          const carry = cur.pop()!;
          flush();
          cur.push(carry);
        } else flush();
      }
    }
    cur.push(w);
  });
  flush();

  // Merge flash phrases (single short weak word) into a neighbour when it keeps phrase length sane.
  for (let i = 0; i < phrases.length; i++) {
    const p = phrases[i];
    const dur = p[p.length - 1].end - p[0].start;
    if (p.length === 1 && dur < 0.3 && emphasisScore(p[0]) === 0) {
      const next = phrases[i + 1];
      const prev = phrases[i - 1];
      if (next && next.length < c.maxWordsPerPhrase + 1 && next[0].start - p[0].end < c.pauseBreakSeconds && !/[.!?]$/.test(p[0].text)) {
        next.unshift(p[0]);
        phrases.splice(i--, 1);
      } else if (prev && prev.length < c.maxWordsPerPhrase + 1 && p[0].start - prev[prev.length - 1].end < c.pauseBreakSeconds) {
        prev.push(p[0]);
        phrases.splice(i--, 1);
      }
    }
  }

  const out: Phrase[] = phrases.map((p) => {
    const scores: number[] = p.map(emphasisScore);
    const best = Math.max(...scores);
    const bi = best >= 2 || (best === 1 && p.length >= 3) ? scores.indexOf(best) : -1;
    return {
      start: p[0].start,
      end: p[p.length - 1].end,
      words: p.map((w, i) => ({ ...w, emphasis: i === bi, uncertain: w.p !== null && w.p < style.transcription.uncertainBelow })),
    };
  });
  // Display window: hold after the last word (reading time) but never overlap the next phrase.
  out.forEach((p, i) => {
    const next = out[i + 1];
    const minEnd = p.start + c.minPhraseSeconds;
    let end = Math.max(p.end + 0.35, minEnd);
    if (next) end = Math.min(end, next.start);
    p.end = round(Math.max(end, p.end), 3);
  });
  return out;
}

export const displayText = (w: string, style: HouseStyle) => {
  const t = w.replace(/^[,"“]+|[,"”]+$/g, "").replace(/[.;:]$/, "");
  return style.captions.uppercase ? t.toUpperCase() : t;
};

/** Word gap in em; CaptionTrack uses the same value so measured and rendered widths agree. */
export const WORD_GAP_EM = 0.26;

export type Fit = { fontSize: number; lines: number[][]; width: number; height: number; tooLong: boolean };

/** Measure with the actual caption font file (PIL) and choose the largest size that fits on 1-2 lines. */
export async function fitPhrases(phrases: Phrase[], fontFile: string, maxWidth: number, style: HouseStyle): Promise<Fit[]> {
  const c = style.captions;
  const tokens = new Set<string>([" "]);
  phrases.forEach((p) => p.words.forEach((w) => tokens.add(displayText(w.text, style))));
  const list = [...tokens];
  const req = rel("cache", `measure-${process.pid}.json`);
  writeFileSync(req, JSON.stringify({ font: fontFile, items: list.map((text) => ({ text, size: 100 })) }));
  const widths: number[] = JSON.parse((await py("fonts.py", ["measure", req])).stdout);
  const w100 = new Map(list.map((t, i) => [t, widths[i]]));
  const lineWidth = (ws: string[], size: number) =>
    ((ws.reduce((s, t) => s + (w100.get(t) ?? 60), 0) + (ws.length - 1) * WORD_GAP_EM * 100) * size) / 100 + c.strokePx;

  return phrases.map((p) => {
    const ws = p.words.map((w) => displayText(w.text, style));
    const idx = ws.map((_, i) => i);
    for (let size = c.fontSizeMax; size >= c.fontSizeMin; size -= 2) {
      const w = lineWidth(ws, size);
      if (w <= maxWidth) return { fontSize: size, lines: [idx], width: w, height: size * 1.12, tooLong: false };
    }
    if (c.maxLines >= 2 && ws.length > 1) {
      for (let size = c.fontSizeMax; size >= 40; size -= 2) {
        let best: { k: number; w: number } | null = null;
        for (let k = 1; k < ws.length; k++) {
          const w = Math.max(lineWidth(ws.slice(0, k), size), lineWidth(ws.slice(k), size));
          if (w <= maxWidth && (!best || w < best.w)) best = { k, w };
        }
        if (best) return { fontSize: size, lines: [idx.slice(0, best.k), idx.slice(best.k)], width: best.w, height: size * 2.2, tooLong: size < c.fontSizeMin };
      }
    }
    const size = 40;
    return { fontSize: size, lines: [idx], width: lineWidth(ws, size), height: size * 1.12, tooLong: true };
  });
}

const srtTime = (t: number) => {
  const ms = Math.round(t * 1000);
  const h = Math.floor(ms / 3600000);
  const m = Math.floor((ms % 3600000) / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")},${String(ms % 1000).padStart(3, "0")}`;
};

export function toSrt(caps: { start: number; end: number; words: { text: string }[] }[]) {
  return caps.map((c, i) => `${i + 1}\n${srtTime(c.start)} --> ${srtTime(c.end)}\n${c.words.map((w) => w.text).join(" ")}\n`).join("\n");
}
