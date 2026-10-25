// Tier-board state machine. Deterministic: the board at time t depends only on the event list.
import { TIERS, type Tier, type TierEvent } from "./plan";

export const FLY_SECONDS = 0.3; // ~9 frames at 30fps; reference measured ~6-8 frames for the shrink-fly
export const MAX_PER_ROW = 6;

export type Placed = { id: string; item: string; tier: Tier; slot: number; image: string | null; placeAt: number };
export type BoardState = {
  rows: Record<Tier, Placed[]>;
  active: { event: TierEvent; phase: "intro" | "flying"; progress: number; slot: number } | null;
};

export function boardStateAt(events: TierEvent[], t: number): BoardState {
  const rows = Object.fromEntries(TIERS.map((k) => [k, [] as Placed[]])) as Record<Tier, Placed[]>;
  const ordered = [...events].sort((a, b) => a.placeAt - b.placeAt);
  let active: BoardState["active"] = null;
  for (const e of ordered) {
    const slot = rows[e.tier].length;
    if (t >= e.placeAt + FLY_SECONDS) {
      rows[e.tier].push({ id: e.id, item: e.item, tier: e.tier, slot, image: e.image, placeAt: e.placeAt });
    } else if (t >= e.placeAt) {
      active = { event: e, phase: "flying", progress: (t - e.placeAt) / FLY_SECONDS, slot };
      rows[e.tier].push({ id: e.id, item: e.item, tier: e.tier, slot, image: e.image, placeAt: e.placeAt });
    } else if (t >= e.introAt && !active) {
      active = { event: e, phase: "intro", progress: (t - e.introAt) / Math.max(1e-3, e.placeAt - e.introAt), slot };
    }
  }
  return { rows, active };
}

export function tierEventProblems(events: TierEvent[], duration: number): string[] {
  const p: string[] = [];
  const seen = new Set<string>();
  const counts: Record<string, number> = {};
  const ordered = [...events].sort((a, b) => a.introAt - b.introAt);
  ordered.forEach((e, i) => {
    const key = e.item.trim().toLowerCase();
    if (seen.has(key)) p.push(`tier item "${e.item}" is ranked twice`);
    seen.add(key);
    if (!TIERS.includes(e.tier)) p.push(`tier item "${e.item}" has invalid tier ${e.tier}`);
    if (e.introAt > e.placeAt) p.push(`tier item "${e.item}" is placed before it is introduced`);
    if (e.placeAt + FLY_SECONDS > duration + 1e-6) p.push(`tier item "${e.item}" lands after the video ends`);
    const next = ordered[i + 1];
    if (next && next.introAt < e.placeAt) p.push(`tier items "${e.item}" and "${next.item}" are on screen as active items at the same time`);
    counts[e.tier] = (counts[e.tier] ?? 0) + 1;
    if (counts[e.tier] > MAX_PER_ROW) p.push(`tier row ${e.tier} exceeds ${MAX_PER_ROW} items`);
    if (!e.source.quote.trim()) p.push(`tier item "${e.item}" has no supporting quote/instruction`);
  });
  return p;
}
