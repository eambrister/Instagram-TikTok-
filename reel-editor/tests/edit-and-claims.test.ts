import assert from "node:assert/strict";
import { test } from "node:test";
import { buildEdl, findRestarts, findRetakes, snapToSpeech } from "../src/pipeline/edl";
import { loadStyle } from "../src/pipeline/config";
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

test("direction can pin the hook title for the whole video", () => {
  assert.equal(parseDirection("pin the title at the top").pinHook, true);
  assert.equal(parseDirection("keep the hook").pinHook, true);
  assert.equal(parseDirection("less motion").pinHook, false);
});

test("a parallel phrase is not a restart", () => {
  assert.equal(findRestarts(words("do you like to walk or do you like to run")).length, 0);
});

test("a restart after a long pause is still removed", () => {
  const w = [...words("people think walking"), ...words("people think walking is too easy", 9)];
  const cuts = findRestarts(w);
  assert.equal(cuts.length, 1);
  assert.equal(cuts[0].start, w[0].start);
  assert.equal(cuts[0].end, w[3].start);
});

test("a long wordless gap broken up by room noise is still shortened", () => {
  const w = [...words("here is what i learned"), ...words("people think walking", 9)];
  const lastEnd = w[4].end;
  // 7.65 s gap, 68% detected as silent in three pieces (clicks in between).
  const silences = [
    { start: lastEnd + 0.1, end: lastEnd + 2.0 },
    { start: lastEnd + 2.6, end: lastEnd + 4.5 },
    { start: lastEnd + 5.6, end: lastEnd + 7.0 },
  ];
  const edl = buildEdl(w, silences, 12, loadStyle());
  assert.ok(edl.cuts.some((c) => c.reason.startsWith("pause") && c.end - c.start > 6));
});

test("a short gap with audible sound is kept", () => {
  const w = [...words("here is what"), ...words("i learned", 2.0)];
  const gapStart = w[2].end;
  const edl = buildEdl(w, [{ start: gapStart, end: gapStart + 0.4 }], 4, loadStyle());
  assert.ok(!edl.cuts.some((c) => c.reason.startsWith("pause")));
});

test("a chain of repeats is rhetorical, not a restart", () => {
  assert.equal(findRestarts(words("I ate the same meals over and over and over again")).length, 0);
  assert.equal(findRestarts(words("I was going to, I was going to tell you")).length, 1);
});

test("a correction can retime a word stretched over a pause", () => {
  const w = [{ text: "lot", start: 51.26, end: 51.4, p: 0.9 }, { text: "4.", start: 51.5, end: 56.5, p: 0.5 }];
  const r = applyCorrections(w as never, [{ at: 51.5, from: "4.", to: "4.", start: 56.25, end: 56.55 }]);
  assert.equal(r.words[1].start, 56.25);
  assert.equal(r.words[1].text, "4.");
});

test("a parallel list is not a retake", () => {
  const w = words("you lose it in your face, you lose it in your arms, you lose it in your legs, but not your stomach.");
  assert.equal(findRetakes(w).length, 0);
  const r = words("for a lot of people, fat is where, for a lot of people, the stomach is where fat shows up first.");
  assert.equal(findRetakes(r).length, 1);
});
