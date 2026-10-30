import assert from "node:assert/strict";
import { test } from "node:test";
import { buildSegments, outToSrc, remapSpan, srcToOut, subtract, timelineProblems } from "../src/shared/timeline";

test("cuts shift later material earlier and keep frame alignment", () => {
  const keep = subtract([{ start: 0, end: 10 }], [{ start: 2, end: 3.5 }, { start: 6, end: 7 }]);
  const segs = buildSegments(keep, 30);
  assert.equal(segs.length, 3);
  assert.deepEqual(timelineProblems(segs, 30), []);
  assert.equal(segs[2].outEnd, 7.5);
  assert.ok(Math.abs(srcToOut(segs, 4)! - 2.5) < 1e-9);
  assert.equal(srcToOut(segs, 2.5), null); // removed material has no output time
  assert.ok(Math.abs(outToSrc(segs, 2.5) - 4) < 1e-9);
});

test("words inside a cut are dropped; survivors never straddle a join", () => {
  const segs = buildSegments([{ start: 0, end: 2 }, { start: 3, end: 5 }], 30);
  assert.equal(remapSpan(segs, { start: 2.2, end: 2.6 }), null);
  const w = remapSpan(segs, { start: 2.9, end: 3.4 })!; // midpoint 3.15 is kept, start clamped to the join
  assert.ok(Math.abs(w.start - 2) < 1e-9 && Math.abs(w.end - 2.4) < 1e-9);
});

test("validator reports gaps and misalignment", () => {
  const bad = [{ srcStart: 0, srcEnd: 1, outStart: 0, outEnd: 1 }, { srcStart: 2, srcEnd: 3, outStart: 1.5, outEnd: 2.5 }];
  assert.ok(timelineProblems(bad, 30).some((p) => p.includes("gap")));
});
