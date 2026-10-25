// Builds the scene plan. Every on-screen claim is lifted from Eddie's own words (with timestamps) or an
// explicit instruction; nothing here invents numbers, quotes or rankings.
import { existsSync } from "node:fs";
import path from "node:path";
import type { HouseStyle } from "./config";
import type { Fit, Phrase, TWord } from "./captions";
import { displayText } from "./captions";
import { clamp, hashOf, rel, round } from "./util";
import { faceRect, intersects, speakerFrame } from "../shared/framing";
import { TIERS, type Graphic, type LayoutSpan, type Mode, type ScenePlan, type Segment, type Tier, type TierEvent, type ZoomKey } from "../shared/plan";
import { cutPoints, type TimelineSegment } from "../shared/timeline";

export type Direction = {
  mode: Mode | "auto";
  intensity: "light" | "medium" | "high";
  keepPauses: boolean;
  zooms: boolean;
  graphics: boolean;
  topic: string | null;
  rankings: { item: string; tier: Tier }[];
  notes: string[];
};

const lc = (s: string) => s.toLowerCase().replace(/[^a-z0-9'%$.-]/g, "").replace(/[.]$/, "");
const sentenceEnd = (s: string) => /[.!?]$/.test(s);
const STOP = new Set(["the", "a", "an", "and", "or", "but", "so", "to", "of", "in", "on", "for", "with", "is", "are", "was", "it", "it's", "that", "this", "i", "you", "your", "my", "we", "they", "just", "like", "really", "very", "then", "now", "be", "if", "at", "as", "do", "don't", "all", "some"]);

/** Plain-language direction -> structured options (also used for --direction on the CLI). */
export function parseDirection(text: string, base: Partial<Direction> = {}): Direction {
  const t = text.toLowerCase();
  const d: Direction = { mode: "auto", intensity: "medium", keepPauses: false, zooms: true, graphics: true, topic: null, rankings: [], notes: [], ...base };
  if (/\b(tier|ranking|rank)\b/.test(t)) d.mode = "RANKING";
  else if (/\b(explainer|explain|split[- ]screen|panel)\b/.test(t)) d.mode = "EXPLAINER";
  else if (/\b(talking[- ]head|simple|minimal|clean)\b/.test(t)) d.mode = "TALKING_HEAD";
  if (/\b(light|subtle|calm|less motion)\b/.test(t)) d.intensity = "light";
  if (/\b(high|aggressive|energetic|more motion|hype)\b/.test(t)) d.intensity = "high";
  if (/(keep (the )?pauses|don't cut|no cuts)/.test(t)) d.keepPauses = true;
  if (/no zoom/.test(t)) d.zooms = false;
  if (/no graphics/.test(t)) d.graphics = false;
  if (text.trim()) d.notes.push(`direction: "${text.trim()}"`);
  return d;
}

export function parseRankings(spec: string): { item: string; tier: Tier }[] {
  return spec.split(/[;,\n]/).map((s) => s.trim()).filter(Boolean).map((s) => {
    const m = s.match(/^(.+?)\s*[=:]\s*([SABCDF])$/i);
    if (!m) throw new Error(`Bad ranking "${s}". Use "Item=S" separated by commas.`);
    return { item: m[1].trim(), tier: m[2].toUpperCase() as Tier };
  });
}

// ---------- mode selection ----------
function tierMentions(words: TWord[]) {
  const out: { i: number; tier: Tier }[] = [];
  words.forEach((w, i) => {
    const a = lc(w.text);
    const one = a.match(/^([sabcdf])-?tier$/);
    if (one) return out.push({ i, tier: one[1].toUpperCase() as Tier });
    const nxt = words[i + 1] ? lc(words[i + 1].text) : "";
    if (/^[sabcdf]$/.test(a) && /^tier/.test(nxt)) {
      const after = words[i + 2] ? lc(words[i + 2].text) : "";
      if (a === "a" && (after === "list" || /^(the|my|this)$/.test(words[i - 1] ? lc(words[i - 1].text) : ""))) return;
      out.push({ i, tier: a.toUpperCase() as Tier });
    }
  });
  return out;
}

const UNITS = new Set(["calories", "calorie", "cals", "grams", "gram", "g", "pounds", "pound", "lbs", "lb", "kilos", "kg", "minutes", "minute", "hours", "hour",
  "seconds", "reps", "sets", "percent", "%", "miles", "mile", "steps", "days", "day", "weeks", "week", "months", "years", "glasses", "cups", "servings", "meals", "times"]);
const NUMWORDS: Record<string, number> = { zero: 0, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10, eleven: 11, twelve: 12,
  thirteen: 13, fourteen: 14, fifteen: 15, sixteen: 16, seventeen: 17, eighteen: 18, nineteen: 19, twenty: 20, thirty: 30, forty: 40, fifty: 50, sixty: 60, seventy: 70, eighty: 80, ninety: 90 };

/** Parse a spoken quantity starting at word i. Returns value, decimals, words consumed. */
export function parseNumber(words: TWord[], i: number): { value: number; decimals: number; n: number; text: string } | null {
  const t0 = lc(words[i].text).replace(/^\$/, "");
  const digits = t0.match(/^(\d{1,3}(,\d{3})+|\d+)(\.\d+)?(%|g|k)?$/);
  if (digits) {
    let v = Number(t0.replace(/[,%gk]/g, ""));
    if (t0.endsWith("k")) v *= 1000;
    const dec = (t0.split(".")[1] ?? "").replace(/\D/g, "").length;
    return { value: v, decimals: Math.min(2, dec), n: 1, text: words[i].text };
  }
  let v = 0;
  let cur = 0;
  let n = 0;
  for (let j = i; j < Math.min(words.length, i + 5); j++) {
    const w = lc(words[j].text).replace(/-/g, " ");
    const parts = w.split(" ");
    let ok = true;
    for (const p of parts) {
      if (p in NUMWORDS) cur += NUMWORDS[p];
      else if (p === "hundred") cur = (cur || 1) * 100;
      else if (p === "thousand") (v += (cur || 1) * 1000), (cur = 0);
      else if (p === "a" && j === i && words[j + 1] && /^(hundred|thousand)/.test(lc(words[j + 1].text))) cur = 0;
      else ok = false;
    }
    if (!ok) break;
    n++;
    if (sentenceEnd(words[j].text) || /,$/.test(words[j].text)) break;
  }
  if (!n || (v + cur === 0 && lc(words[i].text) !== "zero")) return null;
  return { value: v + cur, decimals: 0, n, text: words.slice(i, i + n).map((w) => w.text).join(" ") };
}

export function selectMode(words: TWord[], d: Direction): { mode: Mode; reason: string } {
  if (d.mode !== "auto") return { mode: d.mode, reason: "explicit override" };
  if (d.rankings.length) return { mode: "RANKING", reason: "ranking instructions supplied" };
  const tiers = tierMentions(words).length;
  const text = words.map((w) => lc(w.text)).join(" ");
  if (tiers >= 2 || (tiers >= 1 && /(tier list|ranking|rank)/.test(text))) return { mode: "RANKING", reason: `${tiers} spoken tier placements` };
  let qty = 0;
  words.forEach((w, i) => {
    const n = parseNumber(words, i);
    if (n && words[i + n.n] && UNITS.has(lc(words[i + n.n].text))) qty++;
  });
  const cmp = (text.match(/\b(versus|vs|instead of|compared to|rather than)\b/g) ?? []).length;
  if (qty >= 2 || qty + cmp >= 3) return { mode: "EXPLAINER", reason: `${qty} spoken quantities, ${cmp} comparisons` };
  return { mode: "TALKING_HEAD", reason: `few quantities (${qty}) or comparisons (${cmp}); speaker-led` };
}

// ---------- graphic candidates from speech ----------
type Candidate = { kind: Graphic["kind"]; at: number; end: number; priority: number; data: any; quote: string; confidence: number };
const quoteOf = (ws: TWord[]) => ws.map((w) => w.text).join(" ").replace(/[,.;:]$/, "");
const minConf = (ws: TWord[]) => Math.min(...ws.map((w) => w.p ?? 1));

function sentences(words: TWord[]) {
  const out: { i0: number; i1: number }[] = [];
  let s = 0;
  words.forEach((w, i) => {
    if (sentenceEnd(w.text) || i === words.length - 1 || (words[i + 1] && words[i + 1].start - w.end > 0.7)) {
      out.push({ i0: s, i1: i });
      s = i + 1;
    }
  });
  return out;
}

function findCandidates(words: TWord[]): { cands: Candidate[]; flagged: string[] } {
  const cands: Candidate[] = [];
  const flagged: string[] = [];
  // Quantities -> counters (value must be spoken; low-confidence numbers are flagged, not animated).
  for (let i = 0; i < words.length; i++) {
    const n = parseNumber(words, i);
    if (!n) continue;
    const unitW = words[i + n.n];
    const unitInline = /%$/.test(words[i].text) ? "%" : null;
    const unit = unitInline ?? (unitW && UNITS.has(lc(unitW.text)) ? lc(unitW.text) : null);
    if (!unit || n.value <= 0) continue;
    // Quote = the sentence around the number (no words from neighbouring sentences).
    let s0 = i;
    while (s0 > 0 && i - s0 < 4 && !sentenceEnd(words[s0 - 1].text)) s0--;
    let s1 = i + n.n;
    while (s1 < words.length - 1 && s1 - i < n.n + 3 && !sentenceEnd(words[s1].text)) s1++;
    const span = words.slice(s0, s1 + 1);
    const conf = minConf(words.slice(i, i + n.n + (unitInline ? 0 : 1)));
    if (conf < 0.85) {
      flagged.push(`"${quoteOf(words.slice(i, i + n.n + 1))}" at ${words[i].start.toFixed(2)}s: number confidence ${conf.toFixed(2)} — not animated, please confirm`);
      i += n.n;
      continue;
    }
    cands.push({ kind: "counter", at: words[i].start, end: words[i].start + 2.8, priority: 3, confidence: conf,
      data: { value: n.value, decimals: n.decimals, unit: unit === "%" ? "PERCENT" : unit.toUpperCase(), caption: quoteOf(span).toUpperCase(), estimate: false },
      quote: quoteOf(span) });
    i += n.n;
  }
  // Comparisons -> comparison panel with both sides quoted.
  for (let i = 1; i < words.length - 1; i++) {
    const a = lc(words[i].text);
    const two = a + " " + lc(words[i + 1]?.text ?? "");
    let j = -1;
    let joiner = "";
    if (a === "vs" || a === "versus") (j = i + 1), (joiner = "VS");
    else if (two === "instead of" || two === "compared to" || two === "rather than") (j = i + 2), (joiner = two.toUpperCase());
    if (j < 0) continue;
    const left: TWord[] = [];
    for (let k = i - 1; k >= 0 && left.length < 3 && !/[.!?,]$/.test(words[k].text); k--) left.unshift(words[k]);
    while (left.length && STOP.has(lc(left[0].text))) left.shift();
    const right: TWord[] = [];
    for (let k = j; k < words.length && right.length < 3; k++) {
      right.push(words[k]);
      if (/[.!?,]$/.test(words[k].text)) break;
    }
    while (right.length && STOP.has(lc(right[right.length - 1].text))) right.pop();
    if (!left.length || !right.length) continue;
    cands.push({ kind: "comparison", at: left[0].start - 0.1, end: right[right.length - 1].end + 2.2, priority: 2, confidence: minConf([...left, ...right]),
      data: { left: quoteOf(left).toUpperCase(), right: quoteOf(right).toUpperCase(), joiner }, quote: quoteOf(words.slice(left.length ? words.indexOf(left[0]) : i, j + right.length)) });
  }
  // Takeaways and list markers -> floating cards with Eddie's exact words.
  const CUE = /^(the key|the truth|the secret|the rule|remember|here's the thing|bottom line|the problem is|the point is|the goal is|the reason)/;
  for (const s of sentences(words)) {
    const ws = words.slice(s.i0, s.i1 + 1);
    const text = ws.map((w) => lc(w.text)).join(" ");
    const m = text.match(CUE);
    const first = lc(ws[0].text);
    const step = /^(first|second|third|fourth|fifth|firstly|secondly)$/.test(first) ? first : null;
    if ((m || step) && ws.length <= 10) {
      cands.push({ kind: "card", at: ws[0].start - 0.1, end: Math.max(ws[ws.length - 1].end + 1.2, ws[0].start + 2.6), priority: step ? 1 : 2,
        confidence: minConf(ws), quote: quoteOf(ws),
        data: { label: step ? step.toUpperCase().replace(/LY$/, "") : null, text: ws.map((w) => displayText(w.text, { captions: { uppercase: true } } as HouseStyle)).join(" "), icon: null, tilt: 0 } });
    }
  }
  return { cands, flagged };
}

// ---------- ranking events ----------
function slug(s: string) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

function objectImage(item: string): string | null {
  for (const ext of ["png", "webp"]) {
    const f = `licensed-media/objects/${slug(item)}.${ext}`;
    if (existsSync(rel(f))) return f;
  }
  return null;
}

function findPhrase(words: TWord[], phrase: string, from = 0) {
  const target = phrase.toLowerCase().split(/\s+/).map((x) => x.replace(/[^a-z0-9']/g, "")).filter(Boolean);
  for (let i = from; i < words.length; i++) {
    let ok = true;
    for (let k = 0; k < target.length; k++) {
      const w = words[i + k] ? lc(words[i + k].text).replace(/[^a-z0-9']/g, "") : "";
      if (!(w === target[k] || (w.endsWith("s") && w.slice(0, -1) === target[k]) || target[k] + "s" === w)) ok = false;
    }
    if (ok) return i;
  }
  return -1;
}

const LINK = new Set(["is", "are", "goes", "go", "gets", "get", "belongs", "lands", "sits", "'s", "that's", "it's", "those", "these", "they're"]);
const FILL = new Set(["straight", "to", "in", "into", "at", "right", "the", "an", "solid", "easy", "definitely", "probably", "a", "an", "gonna", "going", "be", "for", "me", "honestly", "low", "high", "mid"]);

function rankingEvents(words: TWord[], d: Direction, notes: string[], flagged: string[]): TierEvent[] {
  const events: TierEvent[] = [];
  const mentions = tierMentions(words);
  if (d.rankings.length) {
    let cursor = 0;
    for (const r of d.rankings) {
      const i = findPhrase(words, r.item, cursor);
      if (i < 0) {
        flagged.push(`ranking "${r.item}=${r.tier}" was supplied but "${r.item}" is never said; it is shown after the previous item without speech sync`);
        const prev = events[events.length - 1];
        const at = prev ? prev.placeAt + 1.5 : 1;
        events.push({ id: `tier-${events.length}`, item: r.item, tier: r.tier, introAt: at, placeAt: at + 1.2, image: objectImage(r.item), source: { kind: "instruction", quote: `${r.item}=${r.tier}` } });
        continue;
      }
      const m = mentions.find((x) => x.i > i && x.tier === r.tier && words[x.i].start - words[i].start < 20);
      const introAt = words[i].start - 0.1;
      const placeAt = m ? words[m.i].start : words[i].start + 1.4;
      events.push({ id: `tier-${events.length}`, item: r.item, tier: r.tier, introAt: Math.max(0, introAt), placeAt, image: objectImage(r.item),
        source: { kind: "instruction", quote: `${r.item}=${r.tier}`, at: words[i].start } });
      cursor = i + 1;
    }
    return events;
  }
  // Auto-parse "<item> is/goes (straight to) <X> tier" from speech; anything ambiguous is flagged, not drawn.
  let lastEnd = 0;
  for (const m of mentions) {
    let k = m.i - 1;
    while (k >= lastEnd && FILL.has(lc(words[k].text))) k--;
    let item: TWord[] = [];
    if (k >= lastEnd && LINK.has(lc(words[k].text))) {
      for (let j = k - 1; j >= lastEnd && item.length < 3; j--) {
        const w = lc(words[j].text);
        if (STOP.has(w) || /[.!?,]$/.test(words[j].text)) break;
        item.unshift(words[j]);
      }
    }
    lastEnd = m.i + 1;
    if (!item.length) {
      flagged.push(`tier "${m.tier}" spoken at ${words[m.i].start.toFixed(2)}s but the item was not clear — pass --rankings to place it`);
      continue;
    }
    const name = quoteOf(item).replace(/[^A-Za-z0-9' -]/g, "");
    const first = findPhrase(words, name);
    const introAt = Math.max(0, Math.min(item[0].start, first >= 0 ? words[first].start : item[0].start) - 0.1);
    if (events.some((e) => e.item.toLowerCase() === name.toLowerCase())) continue;
    events.push({ id: `tier-${events.length}`, item: name, tier: m.tier, introAt, placeAt: words[m.i].start, image: objectImage(name),
      source: { kind: "speech", quote: quoteOf(words.slice(words.indexOf(item[0]), m.i + 2)), at: words[m.i].start, confidence: minConf([...item, words[m.i]]) } });
  }
  if (events.length) notes.push(`rankings auto-parsed from speech: ${events.map((e) => `${e.item}=${e.tier}`).join(", ")} — verify`);
  // Keep active items from overlapping: an item's intro waits for the previous landing.
  events.sort((a, b) => a.placeAt - b.placeAt);
  for (let i = 1; i < events.length; i++) events[i].introAt = Math.max(events[i].introAt, events[i - 1].placeAt + 0.35);
  for (const e of events) e.introAt = Math.min(e.introAt, Math.max(0, e.placeAt - 0.3));
  return events;
}

// ---------- plan assembly ----------
export type PlanInput = {
  jobId: string;
  style: HouseStyle;
  direction: Direction;
  fps: number;
  proxy: { url: string; width: number; height: number };
  segments: (TimelineSegment & { focus: Segment["focus"] })[];
  words: TWord[]; // output timeline
  phrases: Phrase[];
  fits: Fit[];
  fonts: ScenePlan["fonts"];
};

export function buildPlan(inp: PlanInput): { plan: ScenePlan; flagged: string[] } {
  const { style, direction: d, fps, segments } = inp;
  const W = style.output.width;
  const H = style.output.height;
  const sa = style.safeArea;
  const lvl = style.motion.levels[d.intensity];
  const duration = segments[segments.length - 1].outEnd;
  const notes = [...d.notes];
  const flagged: string[] = [];
  const { mode, reason } = selectMode(inp.words, d);
  const panelH = style.layout.explainerPanelHeight;
  const boardH = style.layout.rankingSpeakerHeight;

  // Zoom headroom: never enlarge past the proxy's native pixels by more than ~6%.
  const coverFull = Math.max(W / inp.proxy.width, H / inp.proxy.height);
  const maxZoom = round(clamp(Math.max(1 / coverFull, 1.06), 1, lvl.zoomMax), 3);
  if (1 / coverFull < lvl.zoomMax) notes.push(`zoom capped at ${maxZoom}x by source resolution (${inp.proxy.width}x${inp.proxy.height})`);
  if (coverFull > 1.05) notes.push(`source is upscaled ${coverFull.toFixed(2)}x to fill 1080x1920; expect some softness`);

  const segAt = (t: number) => segments.find((s) => t >= s.outStart && t < s.outEnd) ?? segments[segments.length - 1];
  const phraseStarts = inp.phrases.map((p) => p.start);
  const snapToPhrase = (t: number) => phraseStarts.reduce((b, s) => (Math.abs(s - t) < Math.abs(b - t) ? s : b), t);

  // Graphic candidates
  const { cands, flagged: f1 } = d.graphics ? findCandidates(inp.words) : { cands: [], flagged: [] };
  flagged.push(...f1);
  const tierEvents = mode === "RANKING" ? rankingEvents(inp.words, d, notes, flagged) : [];
  if (mode === "RANKING" && !tierEvents.length) flagged.push("RANKING mode but no rankings could be placed; board is shown empty");

  // Hook from the opening words (exact), shown from frame 0.
  const graphics: Graphic[] = [];
  // Hook = his complete opening sentence (or first clause), never cut mid-thought; up to 10 words.
  let firstSentence: TWord[] = [];
  for (const w of inp.words) {
    if (firstSentence.length >= 10) break;
    firstSentence.push(w);
    if (sentenceEnd(w.text)) break;
  }
  if (firstSentence.length && !sentenceEnd(firstSentence[firstSentence.length - 1].text)) {
    const comma = firstSentence.map((w) => /,$/.test(w.text)).lastIndexOf(true);
    firstSentence = comma >= 2 ? firstSentence.slice(0, comma + 1) : [];
    if (!firstSentence.length) flagged.push("opening sentence is longer than 10 words; no hook title (captions carry the opening)");
  }
  const hookEnd = firstSentence.length ? Math.max(2.0, firstSentence[firstSentence.length - 1].end + 0.5) : 0;

  // Schedule candidates without overlap (higher priority first, then time).
  const chosen: Candidate[] = [];
  for (const c of [...cands].sort((a, b) => b.priority - a.priority || a.at - b.at)) {
    const at = Math.max(c.at, mode === "RANKING" ? 0 : hookEnd + 0.1);
    const end = Math.min(c.end, duration - 0.1);
    if (end - at < 1.4) continue;
    if (chosen.some((o) => at < o.end + 0.2 && o.at < end + 0.2)) continue;
    if (mode === "RANKING" && c.kind !== "counter") continue; // keep the board readable
    chosen.push({ ...c, at, end });
  }
  chosen.sort((a, b) => a.at - b.at);

  // Layout timeline
  let layout: LayoutSpan[] = [];
  const panelSpans: { start: number; end: number }[] = [];
  if (mode === "RANKING") layout = [{ start: 0, end: duration, kind: "board-bottom" }];
  else {
    if (mode === "EXPLAINER") {
      if (firstSentence.length) panelSpans.push({ start: 0, end: snapToPhrase(hookEnd) || hookEnd });
      for (const c of chosen) panelSpans.push({ start: snapToPhrase(c.at), end: snapToPhrase(c.end) });
    }
    const merged: { start: number; end: number }[] = [];
    for (const s of panelSpans.filter((s) => s.end - s.start >= 1).sort((a, b) => a.start - b.start)) {
      const last = merged[merged.length - 1];
      if (last && s.start - last.end < 1.2) last.end = Math.max(last.end, s.end);
      else merged.push({ ...s });
    }
    let t = 0;
    for (const s of merged) {
      if (s.start > t) layout.push({ start: t, end: s.start, kind: "full" });
      layout.push({ start: Math.max(t, s.start), end: Math.min(duration, s.end), kind: "panel-top" });
      t = Math.min(duration, s.end);
    }
    if (t < duration) layout.push({ start: t, end: duration, kind: "full" });
    layout = layout.filter((l) => l.end - l.start > 1e-6).map((l) => ({ ...l, start: round(l.start, 4), end: round(l.end, 4) }));
    layout[0].start = 0;
    layout[layout.length - 1].end = duration;
  }
  const kindAt = (t: number) => (layout.find((l) => t >= l.start && t < l.end) ?? layout[layout.length - 1]).kind;

  // Zooms: alternate framing on every cut (hides jump cuts), motivated pushes on emphasis, cadence fill.
  // Zooms: alternate framing on cuts (hides jump cuts), motivated pushes on emphasis, cadence fill.
  // Moments are collected first, then scales alternate 1 <-> zoomed so consecutive keys always change framing.
  const zooms: ZoomKey[] = [];
  if (d.zooms && maxZoom > 1.01) {
    const punch = round(Math.min(maxZoom, 1 + (lvl.zoomMax - 1) * 0.9), 3);
    const push = round(Math.min(maxZoom, 1 + (lvl.zoomMax - 1) * 0.6), 3);
    const moments: { at: number; frames: number; reason: string }[] = [];
    const events = [
      ...cutPoints(segments).map((t) => ({ t, type: "cut" as const })),
      ...inp.phrases.filter((p) => p.words.some((w) => w.emphasis)).map((p) => ({ t: p.start, type: "emph" as const })),
    ].sort((a, b) => a.t - b.t);
    let last = -10;
    for (const e of events) {
      if (e.t - last < 1.2) continue;
      const roll = parseInt(hashOf([inp.jobId, e.t]).slice(0, 4), 16) / 0xffff;
      if (e.type === "cut" && roll < lvl.punchChance) moments.push({ at: e.t, frames: 0, reason: "punch on cut" });
      else if (e.type === "emph" && e.t - last >= lvl.changeEverySeconds * 0.8) moments.push({ at: e.t, frames: lvl.entranceFrames + 2, reason: "emphasis push" });
      else continue;
      last = e.t;
    }
    // Cadence: no visual change for too long while speaking -> gentle push/pull at a phrase start.
    const others = [...chosen.map((c) => c.at), ...layout.map((l) => l.start), ...tierEvents.map((e) => e.introAt)];
    for (const p of inp.phrases) {
      const prior = [...others, ...moments.map((m) => m.at)].filter((t) => t <= p.start + 1e-6);
      const lastChange = prior.length ? Math.max(...prior) : 0;
      if (p.start - lastChange > lvl.changeEverySeconds * 1.25) moments.push({ at: p.start, frames: lvl.entranceFrames + 4, reason: "cadence" });
    }
    moments.sort((a, b) => a.at - b.at);
    let cur = 1;
    for (const m of moments) {
      cur = cur > 1 ? 1 : m.frames === 0 ? punch : push;
      zooms.push({ at: round(m.at, 4), scale: cur, frames: m.frames, reason: m.reason });
    }
  }
  zooms.sort((a, b) => a.at - b.at);
  const zoomOf = (t: number) => (zooms.filter((z) => z.at <= t).pop()?.scale ?? 1);

  // Regions
  const cx = (sa.x0 + sa.x1) / 2;
  const panelRegion = { x: sa.x0, y: sa.y0, w: sa.x1 - sa.x0, h: panelH - sa.y0 - 120 };
  const faceAt = (t: number, kind: LayoutSpan["kind"]) => {
    const seg = segAt(t);
    const fr = speakerFrame(kind, W, H, panelH, boardH);
    return faceRect(fr, inp.proxy.width, inp.proxy.height, seg.focus, zoomOf(t));
  };
  const topSlot = (t0: number, t1: number) => {
    let faceTop = H;
    for (let t = t0; t < t1; t += 0.5) {
      const f = faceAt(t, "full");
      if (f) faceTop = Math.min(faceTop, f.y);
    }
    const h = Math.min(340, faceTop - 40 - sa.y0);
    return h >= 200 ? { x: sa.x0 + 20, y: sa.y0, w: sa.x1 - sa.x0 - 40, h } : null;
  };

  const lowerSlot = (t0: number, t1: number) => {
    let faceBottom = sa.y0;
    for (let t = t0; t < t1; t += 0.5) {
      const f = faceAt(t, "full");
      if (f) faceBottom = Math.max(faceBottom, f.y + f.h);
    }
    const y = Math.min(faceBottom + 30, sa.y1 - 300);
    return { x: sa.x0 + 20, y, w: sa.x1 - sa.x0 - 40, h: Math.min(380, sa.y1 - y) };
  };

  if (firstSentence.length && mode !== "RANKING") {
    const kind = kindAt(0);
    // Above the head if there is room, otherwise on the chest below the chin, never across the face.
    const region = kind === "panel-top" ? panelRegion : topSlot(0, hookEnd) ?? lowerSlot(0, hookEnd);
    const title = firstSentence.map((w) => displayText(w.text, style)).join(" ");
    const emphIdx: number[] = [];
    firstSentence.forEach((w, i) => inp.phrases.some((p) => p.words.some((pw) => pw.start === w.start && pw.emphasis)) && emphIdx.push(i));
    graphics.push({ kind: "hook", id: "hook", start: 0, end: round(hookEnd, 3), region,
      data: { kicker: d.topic ? d.topic.toUpperCase() : null, title, highlight: emphIdx, times: firstSentence.map((w) => round(w.start, 3)) }, source: { kind: "speech", quote: quoteOf(firstSentence), at: firstSentence[0].start, confidence: minConf(firstSentence) } });
    if (kind !== "panel-top" && !topSlot(0, hookEnd)) notes.push("hook title placed below the face (no room above the head)");
  }

  chosen.forEach((c, i) => {
    let region = panelRegion;
    if (kindAt(c.at) !== "panel-top") {
      const slot = topSlot(c.at, c.end);
      if (!slot) {
        // No room above the face: show this beat as a panel (explainer layout) instead of covering the face.
        const s = snapToPhrase(c.at);
        const e = snapToPhrase(c.end);
        layout = splitLayout(layout, s, e > s + 1 ? e : c.end, "panel-top");
        notes.push(`${c.kind} at ${c.at.toFixed(1)}s moved to a top panel (no room above the face)`);
      } else region = slot;
    }
    const base = { id: `${c.kind}-${i}`, start: round(c.at, 3), end: round(c.end, 3), region,
      source: { kind: "speech" as const, quote: c.quote, at: round(c.at, 3), confidence: round(c.confidence, 3) } };
    graphics.push({ ...base, kind: c.kind, data: c.data } as Graphic);
  });

  // Captions whose words are all inside the hook title are not drawn twice (they stay in the SRT).
  const hook = graphics.find((g) => g.kind === "hook");
  const hookWords = new Set(firstSentence.map((w) => w.start));
  const hookCovers = (p: Phrase) => !!hook && p.start < hook.end && p.words.every((w) => hookWords.has(w.start));

  // Caption placement by layout and face position.
  const captions = inp.phrases.map((p, i) => {
    const fit = inp.fits[i];
    const kind = kindAt(p.start);
    let cy: number;
    if (kind === "panel-top") cy = panelH;
    else if (kind === "board-bottom") cy = boardH - fit.height / 2 - 24;
    else {
      const f = faceAt(p.start, "full");
      cy = f ? clamp(f.y + f.h + 150 + fit.height / 2, 1050, 1400) : 1240;
    }
    cy = clamp(cy, sa.y0 + fit.height / 2, sa.y1 - fit.height / 2);
    const box = { x: round(cx - fit.width / 2, 1), y: round(cy - fit.height / 2, 1), w: round(fit.width, 1), h: round(fit.height, 1) };
    // In full layout, a card in the top slot never shares space with the caption band.
    const suppressed = hookCovers(p);
    if (!suppressed)
      for (const g of graphics) if (p.start < g.end && g.start < p.end && intersects(box, g.region, 8) && kindAt(p.start) === "full") box.y = round(g.region.y + g.region.h + 30, 1);
    if (box.y + box.h > sa.y1) {
      // No room below the card: put the caption above it instead of leaving the safe area.
      const g = graphics.find((x) => p.start < x.end && x.start < p.end);
      if (g) box.y = round(g.region.y - box.h - 30, 1);
    }
    if (fit.tooLong) flagged.push(`caption "${p.words.map((w) => w.text).join(" ")}" needed a small font (${fit.fontSize}px)`);
    return { id: `c${i}`, start: round(p.start, 3), end: round(p.end, 3), words: p.words.map((w) => ({ text: displayText(w.text, style), start: round(w.start, 3), end: round(w.end, 3), emphasis: w.emphasis, uncertain: w.uncertain })),
      lines: fit.lines, fontSize: fit.fontSize, box, suppressed };
  });

  const assets: ScenePlan["assets"] = [
    ...(["heading", "caption", "body"] as const).map((k) => ({ path: inp.fonts[k].url, kind: `font:${k}`, license: inp.fonts[k].source })),
    ...tierEvents.filter((e) => e.image).map((e) => ({ path: e.image!, kind: "object-image", license: "see licensed-media/manifest.json" })),
  ];

  const plan: ScenePlan = {
    version: 1, jobId: inp.jobId, mode, modeReason: reason, intensity: d.intensity, fps, width: W, height: H, duration: round(duration, 4), preview: null,
    source: { url: inp.proxy.url, width: inp.proxy.width, height: inp.proxy.height, fps, maxZoom },
    segments: segments.map((s) => ({ srcStart: s.srcStart, srcEnd: s.srcEnd, outStart: s.outStart, outEnd: s.outEnd, focus: s.focus })),
    layout, zooms, captions, graphics,
    tierBoard: mode === "RANKING" ? { title: d.topic ? d.topic.toUpperCase() : null, events: tierEvents } : null,
    style: {
      colors: style.colors, captionStrokePx: style.captions.strokePx, captionHighlight: style.captions.highlight,
      entranceFrames: lvl.entranceFrames, captionEntranceFrames: style.captions.entranceFrames, panelHeight: panelH, boardSpeakerHeight: boardH, safeArea: sa,
    },
    fonts: inp.fonts, assets, notes,
  };
  return { plan, flagged };
}

function splitLayout(layout: LayoutSpan[], s: number, e: number, kind: LayoutSpan["kind"]): LayoutSpan[] {
  const out: LayoutSpan[] = [];
  for (const l of layout) {
    if (l.end <= s || l.start >= e) out.push(l);
    else {
      if (l.start < s) out.push({ ...l, end: s });
      if (l.end > e) out.push({ ...l, start: e });
    }
  }
  out.push({ start: s, end: e, kind });
  return out.sort((a, b) => a.start - b.start);
}

export const _test = { tierMentions, findCandidates, rankingEvents, sentences, path };
