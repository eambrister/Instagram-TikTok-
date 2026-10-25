// Post-render quality gates. Each check reports PASS / WARN / FAIL / NOT CHECKED with evidence.
// Visual judgement (does it look good?) is NOT automated: contact sheets and motion strips are produced
// for a human or Claude to inspect, and the report says so.
import { closeSync, existsSync, openSync, readSync, statSync } from "node:fs";
import path from "node:path";
import type { ScenePlan } from "../shared/plan";
import { faceRect, intersects, layoutAt, speakerFrame, zoomAt } from "../shared/framing";
import { cutPoints, segmentIndexAtOut } from "../shared/timeline";
import { boardStateAt } from "../shared/tierboard";
import { measureLoudness, speechMasking } from "./audio";
import type { HouseStyle } from "./config";
import { probe } from "./ingest";
import { py, readJson, run } from "./util";

export type Check = { name: string; status: "PASS" | "WARN" | "FAIL" | "NOT CHECKED"; detail: string };

function atomOrder(file: string) {
  const fd = openSync(file, "r");
  const size = statSync(file).size;
  const order: string[] = [];
  let pos = 0;
  const buf = Buffer.alloc(16);
  while (pos < size && order.length < 20) {
    readSync(fd, buf, 0, 16, pos);
    let len = buf.readUInt32BE(0);
    const type = buf.toString("latin1", 4, 8);
    if (len === 1) len = Number(buf.readBigUInt64BE(8));
    if (len === 0) len = size - pos;
    order.push(type);
    pos += len;
  }
  closeSync(fd);
  return order;
}

const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, "");

/** Align re-transcribed output words to planned caption words by text, then compare start times. */
export function syncOffsets(planned: { text: string; start: number }[], heard: { text: string; start: number }[]) {
  const out: { text: string; planned: number; heard: number; delta: number }[] = [];
  let j = 0;
  for (const w of planned) {
    const key = norm(w.text);
    if (!key) continue;
    for (let k = j; k < Math.min(heard.length, j + 8); k++) {
      if (norm(heard[k].text) === key && Math.abs(heard[k].start - w.start) < 1.5) {
        out.push({ text: w.text, planned: w.start, heard: heard[k].start, delta: heard[k].start - w.start });
        j = k + 1;
        break;
      }
    }
  }
  return out;
}

export async function runQa(o: {
  plan: ScenePlan; style: HouseStyle; final: string; jobDir: string; outDir: string; modelDir: string;
  warnings: string[]; flagged: string[]; uncertain: { text: string; at: number; reasons: string[] }[]; cuts: { start: number; end: number; reason: string }[];
  sourceFaceRate: number | null;
}): Promise<Check[]> {
  const { plan, style, final } = o;
  const checks: Check[] = [];
  const add = (name: string, status: Check["status"], detail: string) => checks.push({ name, status, detail });
  const fps = plan.fps;

  // 1. Container / streams
  const p = await probe(final);
  const vOk = p.displayWidth === style.output.width && p.displayHeight === style.output.height && p.codec === "h264" && p.pixFmt === "yuv420p" && Math.abs(p.avgFps - fps) < 0.01;
  add("Dimensions, codec, pixel format, frame rate", vOk ? "PASS" : "FAIL", `${p.displayWidth}x${p.displayHeight} ${p.codec} ${p.pixFmt} ${p.avgFps.toFixed(3)}fps`);
  const a = JSON.parse((await run("ffprobe", ["-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name,sample_rate,duration", "-of", "json", final])).stdout).streams[0];
  const vDur = Number(JSON.parse((await run("ffprobe", ["-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration,nb_frames", "-of", "json", final])).stdout).streams[0].duration);
  add("Audio stream", a?.codec_name === "aac" && a.sample_rate === "48000" ? "PASS" : "FAIL", a ? `${a.codec_name} ${a.sample_rate} Hz` : "missing");
  const dOk = Math.abs(vDur - plan.duration) <= 1.5 / fps && Math.abs(Number(a?.duration) - plan.duration) < 0.06;
  add("Duration matches plan (video and audio)", dOk ? "PASS" : "FAIL", `plan ${plan.duration.toFixed(3)}s, video ${vDur.toFixed(3)}s, audio ${Number(a?.duration).toFixed(3)}s`);
  const atoms = atomOrder(final);
  add("Fast-start (moov before mdat)", atoms.indexOf("moov") > -1 && atoms.indexOf("moov") < atoms.indexOf("mdat") ? "PASS" : "FAIL", atoms.join(" > "));

  // 2. Black frames and audio level
  const bd = await run("ffmpeg", ["-v", "info", "-i", final, "-vf", "blackdetect=d=0.1:pix_th=0.06", "-an", "-f", "null", "-"], { allowFail: true });
  const blacks = [...bd.stderr.matchAll(/black_start:([\d.]+) black_end:([\d.]+)/g)].map((m) => `${m[1]}-${m[2]}s`);
  add("No unexpected black frames", blacks.length ? "FAIL" : "PASS", blacks.length ? blacks.join(", ") : "blackdetect found none (>=0.1s)");
  const m = await measureLoudness(final);
  const loudOk = Math.abs(m.integratedLufs - style.audio.targetLufs) <= 1 && m.truePeakDb <= -1.0;
  add("Loudness and true peak (measured on the AAC export)", loudOk ? "PASS" : "WARN", `${m.integratedLufs} LUFS integrated (target ${style.audio.targetLufs}), true peak ${m.truePeakDb} dBTP, sample peak ${m.maxVolumeDb} dB, LRA ${m.lra} LU`);
  const musicStem = path.join(o.jobDir, "stem-music.wav");
  if (plan.notes.some((n) => n.startsWith("music:")) && existsSync(musicStem)) {
    const mk = await speechMasking(path.join(o.jobDir, "stem-voice.wav"), musicStem);
    add("Music stays under the voice while speaking", mk.median >= style.audio.musicUnderVoiceDb - 1 && mk.p10 >= 10 ? "PASS" : "WARN",
      `median ${mk.median} dB under the voice, 10th percentile ${mk.p10} dB, closest ${mk.min} dB (0.4 s windows with speech)`);
  }
  add("No audio clipping", m.maxVolumeDb < -0.1 ? "PASS" : "FAIL", `max sample ${m.maxVolumeDb} dBFS`);

  // 3. First/last frames, contact sheet, motion strips (for visual review)
  const qa = path.join(o.outDir, "qa");
  await run("ffmpeg", ["-v", "error", "-y", "-i", final, "-frames:v", "1", path.join(qa, "first-frame.jpg")]);
  await run("ffmpeg", ["-v", "error", "-y", "-sseof", "-0.05", "-i", final, "-frames:v", "1", path.join(qa, "last-frame.jpg")]);
  const step = Math.max(0.5, plan.duration / 16);
  await run("ffmpeg", ["-v", "error", "-y", "-i", final, "-vf", `fps=1/${step.toFixed(3)},scale=270:-1,tile=8x2`, "-frames:v", "1", path.join(qa, "contact-sheet.jpg")]);
  const firstGraphic = plan.graphics.find((g) => g.kind !== "hook") ?? plan.graphics[0];
  const stripAt = (t: number, name: string) =>
    run("ffmpeg", ["-v", "error", "-y", "-ss", Math.max(0, t - 0.1).toFixed(3), "-i", final, "-vf", "scale=216:-1,tile=8x2", "-frames:v", "1", path.join(qa, name)]);
  if (firstGraphic) await stripAt(firstGraphic.start, "motion-strip-graphic.jpg");
  const cuts = cutPoints(plan.segments);
  if (cuts.length) await stripAt(cuts[Math.floor(cuts.length / 2)], "motion-strip-cut.jpg");
  add("Visual review material", "NOT CHECKED", "first/last frames, contact sheet and 16-frame motion strips saved in qa/. Automated checks cannot judge aesthetics; review them (Claude does this in-session when asked).");

  // 4. Caption geometry vs safe area, graphics and face (from the plan's shared framing math)
  const sa = plan.style.safeArea;
  const outOfSafe = plan.captions.filter((c) => !c.suppressed).filter((c) => c.box.x < sa.x0 - 1 || c.box.x + c.box.w > sa.x1 + 1 || c.box.y < sa.y0 - 1 || c.box.y + c.box.h > sa.y1 + 1);
  add("Captions inside content-safe area", outOfSafe.length ? "FAIL" : "PASS", outOfSafe.length ? outOfSafe.map((c) => c.id).join(", ") : `${plan.captions.length} captions within x ${sa.x0}-${sa.x1}, y ${sa.y0}-${sa.y1}`);
  const overlaps: string[] = [];
  const faceHits: string[] = [];
  for (const c of plan.captions.filter((x) => !x.suppressed)) {
    for (const g of plan.graphics) if (c.start < g.end && g.start < c.end && intersects(c.box, g.region)) overlaps.push(`${c.id}/${g.id}`);
    const t = c.start + 0.05;
    const kind = layoutAt(plan, t);
    const seg = plan.segments[segmentIndexAtOut(plan.segments, t)];
    const f = faceRect(speakerFrame(kind, plan.width, plan.height, plan.style.panelHeight, plan.style.boardSpeakerHeight, plan.style.fullWidthFraction), plan.source.width, plan.source.height, seg.focus, zoomAt(plan.zooms, t, fps, plan.source.maxZoom));
    if (f && intersects(c.box, { x: f.x, y: f.y + f.h * 0.15, w: f.w, h: f.h * 0.85 })) faceHits.push(`${c.id}@${c.start.toFixed(1)}s`);
  }
  add("Captions clear of graphics", overlaps.length ? "FAIL" : "PASS", overlaps.length ? overlaps.join(", ") : "no time-overlapping caption/graphic boxes intersect");
  const faceKnown = plan.segments.some((s) => s.focus);
  add("Captions clear of eyes/mouth (planned face boxes)", !faceKnown ? "NOT CHECKED" : faceHits.length ? "WARN" : "PASS",
    !faceKnown ? "no face was detected in the source, so face-aware placement could not be verified" : faceHits.length ? faceHits.join(", ") : "no caption box intersects the estimated face box");
  const gOverlap: string[] = [];
  plan.graphics.forEach((g, i) => plan.graphics.slice(i + 1).forEach((h) => g.start < h.end && h.start < g.end && intersects(g.region, h.region) && gOverlap.push(`${g.id}/${h.id}`)));
  add("Graphics do not collide", gOverlap.length ? "FAIL" : "PASS", gOverlap.length ? gOverlap.join(", ") : `${plan.graphics.length} graphics`);
  const small = plan.captions.filter((c) => c.fontSize < style.captions.fontSizeMin);
  add("Caption text fits without clipping (PIL-measured with the render font)", small.length ? "WARN" : "PASS",
    small.length ? `${small.length} captions needed < ${style.captions.fontSizeMin}px` : `all captions fit at ${Math.min(...plan.captions.map((c) => c.fontSize))}-${Math.max(...plan.captions.map((c) => c.fontSize))}px`);

  // 5. Face presence in the export (detects bad crops)
  const fj = path.join(o.jobDir, "faces-final.json");
  await py("faces.py", [final, fj, "--fps", "2"]);
  const ff = readJson(fj);
  const rate = ff.samples ? ff.faces.length / ff.samples : 0;
  const cropped = ff.faces.filter((f: any) => f.cx - f.w / 2 < 0.01 || f.cx + f.w / 2 > 0.99 || f.cy - f.h / 2 < 0.005);
  if (o.sourceFaceRate === null || o.sourceFaceRate < 0.2) add("Face framing in export", "NOT CHECKED", `source face detection rate ${o.sourceFaceRate === null ? "n/a" : (o.sourceFaceRate * 100).toFixed(0) + "%"}; too low to compare`);
  else add("Face framing in export", rate >= o.sourceFaceRate * 0.75 && !cropped.length ? "PASS" : "WARN", `face found in ${(rate * 100).toFixed(0)}% of sampled export frames (source ${(o.sourceFaceRate * 100).toFixed(0)}%), ${cropped.length} touching frame edge`);

  // 6. Speech/caption sync: re-transcribe the export and compare to caption word times
  const heardFile = path.join(o.jobDir, "transcript-final.json");
  const asr = path.join(o.jobDir, "final-asr.wav");
  await run("ffmpeg", ["-v", "error", "-y", "-i", final, "-ac", "1", "-ar", "16000", asr]);
  await py("transcribe.py", [asr, o.modelDir, heardFile, "--language", style.transcription.language]);
  const heard = readJson(heardFile).words as { text: string; start: number }[];
  const planned = plan.captions.flatMap((c) => c.words);
  const offs = syncOffsets(planned, heard);
  const abs = offs.map((x) => Math.abs(x.delta)).sort((x, y) => x - y);
  const med = abs[Math.floor(abs.length / 2)] ?? NaN;
  const p90 = abs[Math.floor(abs.length * 0.9)] ?? NaN;
  const nearCut = offs.filter((x) => cuts.some((c) => Math.abs(c - x.planned) < 0.6));
  const nearAbs = nearCut.map((x) => Math.abs(x.delta)).sort((x, y) => x - y);
  const samples = [0.1, 0.3, 0.5, 0.7, 0.9].map((q) => offs[Math.floor(offs.length * q)]).filter(Boolean)
    .map((x) => `"${x.text}" ${x.planned.toFixed(2)}s vs heard ${x.heard.toFixed(2)}s`);
  const syncOk = offs.length >= planned.length * 0.6 && med <= 0.08 && p90 <= 0.2;
  add("Speech/caption sync (export re-transcribed)", syncOk ? "PASS" : "WARN",
    `${offs.length}/${planned.length} words matched; median |Δ| ${(med * 1000).toFixed(0)} ms, p90 ${(p90 * 1000).toFixed(0)} ms. Samples: ${samples.join("; ")}`);
  add("Captions near cuts vs remapped audio", !cuts.length ? "NOT CHECKED" : nearAbs.length && nearAbs[Math.floor(nearAbs.length * 0.9)] <= 0.25 ? "PASS" : nearAbs.length ? "WARN" : "NOT CHECKED",
    cuts.length ? `${nearCut.length} words within 0.6s of ${cuts.length} cuts; max |Δ| ${nearAbs.length ? (nearAbs[nearAbs.length - 1] * 1000).toFixed(0) : "n/a"} ms` : "no cuts in this edit");

  // 7. Tier board state sanity at the end of the video
  if (plan.tierBoard) {
    const end = boardStateAt(plan.tierBoard.events, plan.duration);
    const placed = Object.values(end.rows).flat().length;
    add("Tier board final state", placed === plan.tierBoard.events.length && !end.active ? "PASS" : "FAIL",
      `${placed}/${plan.tierBoard.events.length} items placed: ${Object.entries(end.rows).map(([k, v]) => `${k}[${v.map((x) => x.item).join(", ")}]`).join(" ")}`);
  }

  // 8. Visual cadence
  const changes = [...plan.zooms.map((z) => z.at), ...plan.graphics.map((g) => g.start), ...plan.layout.map((l) => l.start), ...cuts,
    ...(plan.tierBoard?.events.flatMap((e) => [e.introAt, e.placeAt]) ?? [])].sort((x, y) => x - y);
  let maxGap = 0;
  changes.concat([plan.duration]).reduce((prev, t) => ((maxGap = Math.max(maxGap, t - prev)), t), 0);
  add("Visual change cadence", maxGap <= 6 ? "PASS" : "WARN", `${changes.length} visual changes; longest hold ${maxGap.toFixed(1)}s`);
  return checks;
}

export function reportMarkdown(plan: ScenePlan, checks: Check[], extra: { flagged: string[]; warnings: string[]; uncertain: { text: string; at: number; reasons: string[] }[];
  cuts: { start: number; end: number; reason: string }[]; fonts: string[]; source: string; timings: Record<string, number>; corrections: string[] }) {
  const icon = { PASS: "PASS", WARN: "WARN", FAIL: "FAIL", "NOT CHECKED": "NOT CHECKED" } as const;
  const lines = [
    `# QA report: ${plan.jobId}`,
    "",
    `- Source: \`${extra.source}\``,
    `- Mode: **${plan.mode}** (${plan.modeReason}); motion: ${plan.intensity}`,
    `- Output: ${plan.width}x${plan.height} @ ${plan.fps}fps, ${plan.duration.toFixed(2)}s, ${plan.segments.length} segments, ${plan.captions.length} captions, ${plan.graphics.length} graphics`,
    `- Fonts: ${extra.fonts.join("; ")}`,
    `- Stage timings: ${Object.entries(extra.timings).map(([k, v]) => `${k} ${v.toFixed(0)}s`).join(", ")}`,
    "",
    "## Checks performed",
    "",
    "| Check | Result | Evidence |",
    "|---|---|---|",
    ...checks.map((c) => `| ${c.name} | ${icon[c.status]} | ${c.detail.replace(/\|/g, "/")} |`),
    "",
    "## Needs your review",
    "",
    ...(extra.flagged.length ? extra.flagged.map((f) => `- ${f}`) : ["- Nothing flagged by the planner."]),
    ...(extra.uncertain.length ? ["", "Uncertain transcript words (not guessed; correct them in `corrections.json` if wrong):", "",
      ...extra.uncertain.slice(0, 40).map((u) => `- "${u.text}" at ${u.at.toFixed(2)}s: ${u.reasons.join(", ")}`)] : []),
    ...(extra.corrections.length ? ["", "Applied transcript corrections:", "", ...extra.corrections.map((c) => `- ${c}`)] : []),
    ...(extra.warnings.length ? ["", "Plan warnings:", "", ...extra.warnings.map((w) => `- ${w}`)] : []),
    "",
    "## Edit decisions",
    "",
    ...(extra.cuts.length ? extra.cuts.map((c) => `- ${c.start.toFixed(2)}-${c.end.toFixed(2)}s (source): ${c.reason}`) : ["- No cuts."]),
    "",
    "## Notes",
    "",
    ...plan.notes.map((n) => `- ${n}`),
    "",
  ];
  return lines.join("\n");
}
