import assert from "node:assert/strict";
import { test } from "node:test";
import { findRestarts, findRetakes, snapToSpeech } from "../src/pipeline/edl";
import { parseNumber, parseRankings, selectMode, parseDirection } from "../src/pipeline/planner";
import { applyCorrections } from "../src/pipeline/transcribe";

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

test("deliberate repetition of complete sentences is kept", () => {
  assert.equal(findRestarts(words("You are not normal. You are rare. You are abnormal.")).length, 0);
});

test("retakes keep only the last full take", () => {
  const w = [...words("If you're up early training when everybody's sleeping, if you wash,", 0),
    ...words("If you're up early training when everybody's sleeping, if", 10),
    ...words("If you're up early training when everybody's sleeping. Stay ready.", 20)];
  const cuts = findRetakes(w);
  assert.equal(cuts.length, 2);
  assert.equal(cuts[0].start, 0);
  assert.equal(cuts[1].end, 20);
  assert.equal(findRetakes(words("Normal is starting over every Monday. Normal is saying tomorrow.")).length, 0);
});

test("word edges snap to measured speech after a long pause", () => {
  const [w] = snapToSpeech([{ text: "If", start: 56.96, end: 58.0, p: 0.9 }], [{ start: 50, end: 57.9 }]);
  assert.equal(w.start, 57.9);
  assert.equal(w.end, 58.0);
});

test("a joined correction keeps the audio of a split word but drops its caption", () => {
  const w = [
    { text: "abnormal.", start: 71.64, end: 72.4, p: 0.97 },
    { text: "normal.", start: 72.44, end: 73.1, p: 0.14 },
  ];
  const joined = applyCorrections(w, [{ at: 72.44, from: "normal.", to: "", join: true }]);
  assert.deepEqual(joined.words.map((x) => x.text), ["abnormal."]);
  assert.equal(joined.words[0].end, 73.1);
  assert.equal(joined.notSpeech.length, 0);
  const removed = applyCorrections(w, [{ at: 72.44, from: "normal.", to: "" }]);
  assert.equal(removed.words[0].end, 72.4);
  assert.equal(removed.notSpeech.length, 1);
});
