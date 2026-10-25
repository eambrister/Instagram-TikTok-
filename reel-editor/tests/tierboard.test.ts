import assert from "node:assert/strict";
import { test } from "node:test";
import type { TierEvent } from "../src/shared/plan";
import { boardStateAt, FLY_SECONDS, tierEventProblems } from "../src/shared/tierboard";

const ev = (id: string, item: string, tier: TierEvent["tier"], introAt: number, placeAt: number): TierEvent =>
  ({ id, item, tier, introAt, placeAt, image: null, source: { kind: "speech", quote: `${item} is ${tier} tier` } });
const events = [ev("a", "Guessing", "F", 1, 2), ev("b", "Notebook", "B", 3, 4), ev("c", "Photos", "F", 5, 6)];

test("board accumulates and keeps placed items", () => {
  assert.equal(boardStateAt(events, 0.5).active, null);
  assert.equal(boardStateAt(events, 1.5).active?.phase, "intro");
  assert.equal(boardStateAt(events, 2.1).active?.phase, "flying");
  const end = boardStateAt(events, 10);
  assert.deepEqual(end.rows.F.map((p) => [p.item, p.slot]), [["Guessing", 0], ["Photos", 1]]);
  assert.deepEqual(end.rows.B.map((p) => p.item), ["Notebook"]);
  assert.equal(end.active, null);
  assert.equal(boardStateAt(events, 2 + FLY_SECONDS + 0.01).rows.F.length, 1);
});

test("problems: duplicates, ordering, overlap", () => {
  assert.deepEqual(tierEventProblems(events, 10), []);
  const p = tierEventProblems([ev("a", "Eggs", "S", 1, 2), ev("b", "eggs", "A", 1.5, 3), ev("c", "X", "C", 5, 4)], 10);
  assert.ok(p.some((x) => x.includes("ranked twice")));
  assert.ok(p.some((x) => x.includes("same time")));
  assert.ok(p.some((x) => x.includes("placed before")));
});
