import assert from "node:assert/strict";
import { test } from "node:test";
import { findRestarts } from "../src/pipeline/edl";
import { parseNumber, parseRankings, selectMode, parseDirection } from "../src/pipeline/planner";

const words = (s: string, t0 = 0) => s.split(" ").map((text, i) => ({ text, start: t0 + i * 0.3, end: t0 + i * 0.3 + 0.25, p: 0.99 }));

test("restart removes the abandoned first attempt only", () => {
  const w = words("I was going to, I was going to tell you");
  const cuts = findRestarts(w);
  assert.equal(cuts.length, 1);
  assert.equal(cuts[0].start, w[0].start);
  assert.equal(cuts[0].end, w[4].start);
});

test("spoken numbers parse; nothing is invented", () => {
  assert.equal(parseNumber(words("150 minutes"), 0)?.value, 150);
  assert.equal(parseNumber(words("two hundred calories"), 0)?.value, 200);
  assert.equal(parseNumber(words("some calories"), 0), null);
});

test("mode selection and overrides", () => {
  const d = parseDirection("");
  assert.equal(selectMode(words("Granola is F tier. Eggs are S tier."), d).mode, "RANKING");
  assert.equal(selectMode(words("Walk 30 minutes. Do it 5 days. That is 150 minutes."), d).mode, "EXPLAINER");
  assert.equal(selectMode(words("Just show up today."), d).mode, "TALKING_HEAD");
  assert.equal(selectMode(words("Just show up today."), parseDirection("make it a tier list")).mode, "RANKING");
  assert.deepEqual(parseRankings("Eggs=S, Granola = f"), [{ item: "Eggs", tier: "S" }, { item: "Granola", tier: "F" }]);
});
