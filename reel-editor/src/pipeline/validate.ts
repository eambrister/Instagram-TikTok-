// Pre-render gate: schema, timeline integrity, asset existence and claim support.
import { existsSync } from "node:fs";
import path from "node:path";
import { scenePlanSchema, type ScenePlan } from "../shared/plan";
import { timelineProblems } from "../shared/timeline";
import { tierEventProblems } from "../shared/tierboard";
import { rel } from "./util";

const words = (s: string) => s.toUpperCase().replace(/[^A-Z0-9'%$. ]/g, " ").split(/\s+/).filter(Boolean);
const SPOKEN_NUMBER = /\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand)\b/;

function supports(quote: string, text: string) {
  const q = new Set(words(quote).map((w) => w.replace(/[.]$/, "")));
  return words(text).every((w) => q.has(w.replace(/[.]$/, "")));
}

export function validatePlan(raw: unknown, jobDir: string): { plan: ScenePlan | null; errors: string[]; warnings: string[] } {
  const errors: string[] = [];
  const warnings: string[] = [];
  const parsed = scenePlanSchema.safeParse(raw);
  if (!parsed.success) return { plan: null, errors: parsed.error.issues.map((i) => `schema: ${i.path.join(".")}: ${i.message}`), warnings };
  const p = parsed.data;
  const eps = 0.5 / p.fps;

  errors.push(...timelineProblems(p.segments, p.fps));
  if (Math.abs(p.segments[p.segments.length - 1].outEnd - p.duration) > eps) errors.push("plan duration does not match the edited timeline");

  // Layout must tile [0, duration] with no gaps.
  p.layout.forEach((l, i) => {
    if (l.end <= l.start) errors.push(`layout ${i} has no duration`);
    if (i === 0 && l.start !== 0) errors.push("layout does not start at 0");
    if (i > 0 && Math.abs(l.start - p.layout[i - 1].end) > 1e-3) errors.push(`layout gap/overlap at ${l.start}s`);
  });
  if (Math.abs(p.layout[p.layout.length - 1].end - p.duration) > 1e-3) errors.push("layout does not reach the end of the video");

  p.captions.forEach((c, i) => {
    if (c.end <= c.start) errors.push(`caption ${c.id} has non-positive duration`);
    if (c.end > p.duration + eps) errors.push(`caption ${c.id} extends past the end`);
    if (i > 0 && c.start < p.captions[i - 1].end - 1e-3) errors.push(`caption ${c.id} overlaps the previous caption`);
    c.words.forEach((w) => {
      if (w.start < c.start - 1e-3 || w.end > c.end + 1e-3) errors.push(`caption ${c.id} word "${w.text}" falls outside its caption window`);
    });
    const flat = c.lines.flat();
    if (flat.length !== c.words.length || flat.some((v, k) => v !== k)) errors.push(`caption ${c.id} line indices do not cover its words`);
    const sa = p.style.safeArea;
    if (c.box.x < sa.x0 - 1 || c.box.x + c.box.w > sa.x1 + 1 || c.box.y < sa.y0 - 1 || c.box.y + c.box.h > sa.y1 + 1)
      warnings.push(`caption ${c.id} box ${JSON.stringify(c.box)} leaves the content-safe area`);
    if (c.end - c.start < 0.25) warnings.push(`caption ${c.id} is on screen for only ${(c.end - c.start).toFixed(2)}s`);
  });

  for (const g of p.graphics) {
    if (g.end <= g.start || g.end > p.duration + eps) errors.push(`graphic ${g.id} has invalid timing ${g.start}-${g.end}`);
    if (!g.source.quote.trim()) errors.push(`graphic ${g.id} has no supporting quote or instruction`);
    if (g.kind === "counter") {
      const q = g.source.quote.toLowerCase().replace(/,(?=\d{3})/g, "");
      const spoken = q.includes(String(g.data.value)) || SPOKEN_NUMBER.test(q);
      if (g.source.kind === "speech" && !spoken) errors.push(`counter ${g.id} value ${g.data.value} is not in its quote`);
      if (g.source.kind === "speech" && (g.source.confidence ?? 1) < 0.85) errors.push(`counter ${g.id} is animated from a low-confidence number`);
    }
    if (g.kind === "comparison" && !(supports(g.source.quote, g.data.left) && supports(g.source.quote, g.data.right)))
      errors.push(`comparison ${g.id} text is not supported by its quote`);
    if ((g.kind === "card" || g.kind === "hook") && g.source.kind === "speech") {
      const text = g.kind === "card" ? g.data.text : g.data.title;
      if (!supports(g.source.quote, text)) errors.push(`${g.kind} ${g.id} text "${text}" is not Eddie's spoken words`);
    }
    if (g.kind === "object" && g.data.image && !existsSync(rel(g.data.image))) errors.push(`missing asset ${g.data.image}`);
  }

  if (p.tierBoard) {
    errors.push(...tierEventProblems(p.tierBoard.events, p.duration));
    for (const e of p.tierBoard.events) if (e.image && !existsSync(rel(e.image))) errors.push(`missing tier image ${e.image}`);
  }
  if (p.mode === "RANKING" && !p.tierBoard) errors.push("RANKING mode without a tier board");

  for (const k of ["heading", "caption", "body"] as const) {
    const f = rel("public", p.fonts[k].url);
    if (!existsSync(f)) errors.push(`missing font file ${f}`);
  }
  if (!existsSync(path.join(jobDir, path.basename(p.source.url)))) errors.push(`missing source proxy ${p.source.url}`);
  for (const z of p.zooms) if (z.scale > p.source.maxZoom + 1e-6) errors.push(`zoom ${z.scale} at ${z.at}s exceeds source headroom ${p.source.maxZoom}`);
  return { plan: errors.length ? null : p, errors, warnings };
}
