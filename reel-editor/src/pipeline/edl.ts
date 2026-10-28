// Conservative edit decisions. Silence is only a candidate: a transcript gap is shortened when the
// audio confirms it is quiet, and a natural breath (keepPauseSeconds) is always left in place.
import type { HouseStyle } from "./config";
import type { Word } from "./transcribe";
import { normalizeIntervals, subtract, type Interval } from "../shared/timeline";

export type Cut = Interval & { reason: string };
export type Edl = { keep: Interval[]; cuts: Cut[] };

const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9']/g, "");
const FILLER = /^(u+m+|u+h+|e+r+m+|h+m+|mm+)$/;
const STUTTER_OK = new Set(["the", "a", "an", "i", "to", "and", "it's", "it", "we", "you", "so", "my", "is", "that"]);

function overlap(a: Interval, b: Interval) {
  return Math.max(0, Math.min(a.end, b.end) - Math.max(a.start, b.start));
}

export function findRestarts(words: Word[]): Cut[] {
  const t = words.map((w) => norm(w.text));
  const cuts: Cut[] = [];
  for (let i = 0; i < words.length; i++) {
    let found = false;
    for (let k = 4; k >= 2 && !found; k--) {
      for (let gap = 0; gap <= 2 && !found; gap++) {
        const j = i + k + gap;
        if (j + k > words.length) continue;
        let same = true;
        for (let m = 0; m < k; m++) if (!t[i + m] || t[i + m] !== t[j + m]) same = false;
        // A complete sentence said again ("You are not normal. You are rare.") is deliberate, not a restart.
        const abandonedComplete = /[.!?]$/.test(words[j - 1].text);
        // Only fillers may sit between an attempt and its repeat; real words there mean a parallel phrase
        // ("do you like to walk or do you like to run"), which must be kept.
        const gapIsFiller = words.slice(i + k, j).every((w) => FILLER.test(norm(w.text)));
        // Restarts follow quickly, or after he stops and gathers himself (a clear pause before the repeat).
        const pauseBefore = words[j].start - words[j - 1].end;
        const span = words[j].start - words[i].start;
        const soon = span < 4 || (pauseBefore >= 1 && span < 20);
        // A chain of repeats ("over and over and over again") is rhetorical, not a restart: the phrase
        // carries on repeating after the match, or was already repeating before it.
        const chain = gap === 0 && ((j + k < t.length && t[j + k] === t[i]) || (i > 0 && t[i - 1] === t[j - 1]));
        if (same && soon && gapIsFiller && !abandonedComplete && !chain) {
          cuts.push({ start: words[i].start, end: words[j].start, reason: `restart: "${words.slice(i, j).map((w) => w.text).join(" ")}"` });
          i = j - 1;
          found = true;
        }
      }
    }
    if (!found && i + 1 < words.length && t[i] && t[i] === t[i + 1] && STUTTER_OK.has(t[i]) && words[i + 1].start - words[i].end < 0.6) {
      cuts.push({ start: words[i].start, end: words[i + 1].start, reason: `stutter: "${words[i].text}"` });
    }
  }
  return cuts;
}

/**
 * Retakes: the same run of >= 5 words said again within 30 s means an earlier take was abandoned.
 * Everything from the earlier take's first word up to the later take is removed, so the last take is kept.
 */
export function findRetakes(words: Word[], minWords = 5, window = 30): Cut[] {
  const t = words.map((w) => norm(w.text));
  const cuts: Cut[] = [];
  for (let i = 0; i + minWords <= words.length; i++) {
    for (let j = i + minWords; j + minWords <= words.length && words[j].start - words[i].start <= window; j++) {
      let k = 0;
      while (j + k < words.length && i + k < j && t[i + k] && t[i + k] === t[j + k]) k++;
      if (k >= minWords) {
        cuts.push({ start: words[i].start, end: words[j].start,
          reason: `retake: "${words.slice(i, Math.min(j, i + 8)).map((w) => w.text).join(" ")}…" said again at ${words[j].start.toFixed(1)}s, kept the later take` });
        i = j - 1;
        break;
      }
    }
  }
  return cuts;
}

/**
 * Whisper stretches a word over preceding silence (its start can be ~1 s early after a pause) and sometimes
 * over following silence. Clip word edges to the audio's measured silence so captions and cuts follow the voice.
 */
export function snapToSpeech<T extends Word>(words: T[], silences: Interval[]): T[] {
  return words.map((w) => {
    let { start, end } = w;
    for (const s of silences) {
      if (s.start <= start + 0.02 && s.end > start && s.end < end - 0.08) start = s.end;
      if (s.start > start + 0.08 && s.start < end && s.end >= end - 0.02) end = s.start;
    }
    return { ...w, start, end };
  });
}

export function buildEdl(words: Word[], silences: Interval[], duration: number, style: HouseStyle, opts: { keepPauses?: boolean } = {}): Edl {
  const e = style.edit;
  if (!words.length) return { keep: [{ start: 0, end: duration }], cuts: [] };
  const cuts: Cut[] = [];

  const head = Math.max(0, words[0].start - e.headPadSeconds);
  const tail = Math.min(duration, words[words.length - 1].end + e.tailPadSeconds);
  if (head > 0.05) cuts.push({ start: 0, end: head, reason: "lead-in before first word" });
  if (duration - tail > 0.05) cuts.push({ start: tail, end: duration, reason: "tail after last word" });

  if (e.removeFillers)
    words.forEach((w, i) => {
      if (!FILLER.test(norm(w.text))) return;
      const prevEnd = i > 0 ? words[i - 1].end : w.start;
      const nextStart = i + 1 < words.length ? words[i + 1].start : w.end;
      cuts.push({ start: Math.max(prevEnd, w.start - 0.03), end: Math.min(nextStart, w.end + 0.03), reason: `filler "${w.text}"` });
    });

  if (e.removeRestarts) cuts.push(...findRetakes(words), ...findRestarts(words));

  if (!opts.keepPauses)
    for (let i = 0; i + 1 < words.length; i++) {
      const a = words[i];
      const b = words[i + 1];
      const gap = b.start - a.end;
      if (gap <= e.maxPauseSeconds) continue;
      const g = { start: a.end, end: b.start };
      const quiet = silences.reduce((s, x) => s + overlap(g, x), 0);
      // ASR gap but audible sound: leave it alone. Long gaps only need to be mostly quiet: room noise and small
      // clicks break the silence detector into pieces, and seconds without words are dead air.
      if (quiet < gap * (gap > 2 ? 0.6 : 0.8)) continue;
      const keepAfter = e.keepPauseSeconds * 0.6;
      const keepBefore = e.keepPauseSeconds * 0.4;
      if (gap - keepAfter - keepBefore > 0.1)
        cuts.push({ start: a.end + keepAfter, end: b.start - keepBefore, reason: `pause ${gap.toFixed(2)}s shortened to ${e.keepPauseSeconds}s` });
    }

  // Cuts closer than 0.25 s merge: a sliver of a few frames between two cuts is never usable speech.
  const merged = normalizeIntervals(cuts, 0.25);
  const keep = subtract([{ start: 0, end: duration }], merged);
  return { keep, cuts: cuts.sort((x, y) => x.start - y.start) };
}
