// One isolated job per recording: jobs/<id>/ holds working files, outputs/<id>/ the deliverables.
// Stages record an input hash in stages.json, so an interrupted job resumes from the last completed stage.
import { copyFileSync, existsSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";
import { buildAudio, mux } from "./audio";
import { fitPhrases, segment, toSrt } from "./captions";
import { loadStyle, type HouseStyle } from "./config";
import { buildEdl, snapToSpeech } from "./edl";
import { chooseFps, detectSilence, makeProxy, probe, type Probe } from "./ingest";
import { buildPlan, type Direction } from "./planner";
import { reportMarkdown, runQa } from "./qa";
import { renderVideo } from "./render";
import { applyCorrections, transcribe, uncertainWords, type Correction } from "./transcribe";
import { ensureDir, exists, hashOf, log, py, readJson, rel, round, run, sha256File, writeJson } from "./util";
import { validatePlan } from "./validate";
import type { Segment } from "../shared/plan";
import { buildSegments, remapSpan } from "../shared/timeline";

export type JobOptions = {
  input: string;
  direction: Direction;
  music: string | null;
  previewOnly: boolean;
  force: boolean;
  concurrency?: number;
  styleFile?: string;
};

type Stages = Record<string, { key: string; at: string }>;

function rendererCodeHash() {
  const files: string[] = [];
  const walk = (d: string) => readdirSync(d, { withFileTypes: true }).forEach((e) => (e.isDirectory() ? walk(path.join(d, e.name)) : files.push(path.join(d, e.name))));
  walk(rel("src/remotion"));
  walk(rel("src/shared"));
  return hashOf(files.sort().map((f) => readFileSync(f, "utf8")));
}

export async function runJob(o: JobOptions) {
  const input = path.resolve(o.input);
  if (!existsSync(input)) throw new Error(`Input not found: ${input}`);
  const style: HouseStyle = loadStyle(o.styleFile);
  const timings: Record<string, number> = {};
  const timed = async <T>(name: string, fn: () => Promise<T>) => {
    const t0 = Date.now();
    const r = await fn();
    timings[name] = (timings[name] ?? 0) + (Date.now() - t0) / 1000;
    return r;
  };

  const sourceSha = await timed("hash", () => sha256File(input));
  const base = path.basename(input).replace(/\.[^.]+$/, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || "video";
  const jobId = `${base}-${sourceSha.slice(0, 8)}`;
  const jobDir = ensureDir(rel("jobs", jobId));
  const outDir = ensureDir(rel("outputs", jobId));
  ensureDir(path.join(outDir, "qa"));
  const stagesFile = path.join(jobDir, "stages.json");
  if (o.force && existsSync(stagesFile)) rmSync(stagesFile);
  const stages: Stages = existsSync(stagesFile) ? readJson(stagesFile) : {};
  const done = (name: string, key: string) => stages[name]?.key === key;
  const mark = (name: string, key: string) => {
    stages[name] = { key, at: new Date().toISOString() };
    writeJson(stagesFile, stages);
  };
  log("job", `${jobId} (${o.direction.mode}, ${o.direction.intensity})`);

  // 1. Ingest
  const pr: Probe = await probe(input);
  const fps = chooseFps(pr, style.output.fps, style.output.match60fpsSource);
  const ingestKey = hashOf({ sourceSha, fps, v: 2 });
  if (!done("ingest", ingestKey)) {
    for (const f of ["proxy.mp4", "audio.wav", "asr.wav"]) if (exists(path.join(jobDir, f))) rmSync(path.join(jobDir, f));
  }
  const media = await timed("ingest", () => makeProxy(pr, jobDir, fps));
  writeJson(path.join(jobDir, "probe.json"), pr);
  mark("ingest", ingestKey);

  // 2. Transcribe (content-keyed global cache; corrections are applied per job)
  const tr = await timed("transcribe", () => transcribe(media.asr, sourceSha, style));
  const corrFile = path.join(jobDir, "corrections.json");
  const corrections: Correction[] = existsSync(corrFile) ? readJson(corrFile) : [];
  const { words: srcWords, applied, notSpeech } = applyCorrections(tr.words, corrections);
  writeFileSync(path.join(jobDir, "transcript.txt"), srcWords.map((w) => `${w.start.toFixed(2)}\t${w.p ?? ""}\t${w.text}`).join("\n"));
  if (!srcWords.length) throw new Error("No speech was transcribed. Check that the recording has audible speech.");

  // 3. Faces (framing + caption avoidance)
  const facesFile = path.join(jobDir, "faces.json");
  const facesKey = hashOf({ ingestKey, v: 1 });
  if (!done("faces", facesKey) || !existsSync(facesFile)) {
    await timed("faces", () => py("faces.py", [media.proxy, facesFile, "--fps", "3"]));
    mark("faces", facesKey);
  }
  const faces = readJson(facesFile);
  const sourceFaceRate = faces.samples ? faces.faces.length / faces.samples : null;

  // 4. Edit decisions -> output timeline
  // Words Eddie confirmed he did not say count as silence when deciding pause trims.
  const silences = [...(await detectSilence(media.audio, style.edit.silenceDb, 0.3)), ...notSpeech].sort((a, b) => a.start - b.start);
  const timedWords = snapToSpeech(srcWords, silences);
  const edl = buildEdl(timedWords, silences, pr.duration, style, { keepPauses: o.direction.keepPauses });
  const segs = buildSegments(edl.keep, fps);
  writeJson(path.join(jobDir, "edl.json"), { cuts: edl.cuts, keep: edl.keep, segments: segs });
  const focusFor = (s0: number, s1: number): Segment["focus"] => {
    const inSeg = faces.faces.filter((f: any) => f.t >= s0 && f.t <= s1);
    const pool = inSeg.length ? inSeg : faces.faces.filter((f: any) => f.t >= s0 - 2 && f.t <= s1 + 2);
    if (!pool.length) return null;
    const med = (k: string) => pool.map((f: any) => f[k]).sort((a: number, b: number) => a - b)[Math.floor(pool.length / 2)];
    return { cx: round(med("cx"), 4), cy: round(med("cy"), 4), w: round(med("w"), 4) };
  };
  const segments = segs.map((s) => ({ ...s, focus: focusFor(s.srcStart, s.srcEnd) }));
  const outWords = timedWords.map((w) => remapSpan(segs, w)).filter((w): w is NonNullable<typeof w> => w !== null);

  // 5. Captions + plan
  const fonts = readJson(rel("cache/fonts.json"));
  const phrases = segment(outWords, style);
  const fits = await fitPhrases(phrases, fonts.caption.file, style.safeArea.x1 - style.safeArea.x0 - 20, style);
  const { plan: rawPlan, flagged } = buildPlan({
    jobId, style, direction: o.direction, fps,
    proxy: { url: `jobs/${jobId}/proxy.mp4`, width: media.width, height: media.height },
    segments, words: outWords, phrases, fits,
    fonts: { heading: { url: fonts.heading.url, family: fonts.heading.family, source: fonts.heading.source },
      caption: { url: fonts.caption.url, family: fonts.caption.family, source: fonts.caption.source },
      body: { url: fonts.body.url, family: fonts.body.family, source: fonts.body.source } },
  });
  if (pr.hdr) rawPlan.notes.push(`source is ${pr.hdr.toUpperCase()} HDR; tone-mapped to SDR BT.709 (mobius) — check skin tones on a phone`);
  if (pr.vfr) rawPlan.notes.push(`source is variable frame rate (avg ${pr.avgFps.toFixed(2)}fps); normalised to constant ${fps}fps`);
  if (pr.rotation) rawPlan.notes.push(`source orientation metadata ${pr.rotation}° applied`);
  if (sourceFaceRate !== null && sourceFaceRate < 0.2) rawPlan.notes.push(`face detected in only ${(sourceFaceRate * 100).toFixed(0)}% of source samples; framing used safe defaults`);
  const planFile = path.join(jobDir, "scene-plan.json");
  writeJson(planFile, rawPlan);

  // 6. Validate before any render
  const v = validatePlan(rawPlan, jobDir);
  if (!v.plan) {
    writeJson(path.join(outDir, "validation-errors.json"), v.errors);
    throw new Error(`Scene plan rejected (${v.errors.length} problems):\n- ${v.errors.slice(0, 15).join("\n- ")}`);
  }
  const plan = v.plan;
  // Render stages also depend on the renderer code, so editing a component invalidates old renders.
  const planKey = hashOf({ plan, code: rendererCodeHash() });
  log("plan", `${plan.mode} — ${plan.modeReason}; ${plan.duration.toFixed(1)}s from ${pr.duration.toFixed(1)}s, ${plan.segments.length} segments, ${plan.captions.length} captions, ${plan.graphics.length} graphics${plan.tierBoard ? `, ${plan.tierBoard.events.length} tier items` : ""}`);
  for (const f of flagged) log("flag", f);

  // 7. Audio (shared by preview and final)
  // "--music original": compose an original bed (scripts/make_music.py) matched to this video's length.
  let music = o.music;
  if (music === "original") {
    music = path.join(jobDir, "music-original.wav");
    const musicKey = hashOf({ d: plan.duration, seed: sourceSha.slice(0, 6), v: readFileSync(rel("scripts/make_music.py"), "utf8") });
    if (!done("music", musicKey) || !existsSync(music)) {
      await timed("music", () => py("make_music.py", [music!, String(plan.duration + 0.1), "--seed", String(parseInt(sourceSha.slice(0, 6), 16))]));
      mark("music", musicKey);
    }
    plan.notes.push("music: original instrumental composed by scripts/make_music.py for this video (no third-party audio)");
  } else if (music) plan.notes.push(`music: ${music} (must be licensed; record it in licensed-media/manifest.json)`);
  const audioKey = hashOf({ segs: plan.segments.map((s) => [s.srcStart, s.srcEnd]), a: style.audio, music, musicV: music ? readFileSync(music).length : 0, ingestKey });
  const audioFinal = path.join(jobDir, "audio-final.wav");
  if (!done("audio", audioKey) || !existsSync(audioFinal)) {
    const r = await timed("audio", () => buildAudio(plan, media.audio, jobDir, style, music));
    writeJson(path.join(jobDir, "audio-measure.json"), { ...r.measure, musicUnderVoiceDb: r.musicUnderVoiceDb });
    mark("audio", audioKey);
  }

  // 8. Representative preview first (hook + first graphic or tier landing)
  const anchor = plan.tierBoard?.events[0]?.placeAt ?? plan.graphics.find((g) => g.kind !== "hook")?.start ?? 0;
  const pStart = anchor > style.output.previewSeconds - 2 ? Math.max(0, anchor - 3) : 0;
  const pEnd = Math.min(plan.duration, pStart + style.output.previewSeconds);
  const previewVideo = path.join(jobDir, "preview-video.mp4");
  const preview = path.join(outDir, "preview.mp4");
  const previewKey = hashOf({ planKey, pStart, pEnd });
  if (!done("preview", previewKey) || !existsSync(preview)) {
    log("preview", `rendering ${pStart.toFixed(1)}-${pEnd.toFixed(1)}s`);
    await timed("preview", () => renderVideo(plan, style, previewVideo, { frameRange: [Math.round(pStart * fps), Math.round(pEnd * fps) - 1], concurrency: o.concurrency }));
    await run("ffmpeg", ["-v", "error", "-y", "-i", previewVideo, "-ss", pStart.toFixed(3), "-t", (pEnd - pStart).toFixed(3), "-i", audioFinal,
      "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", preview]);
    mark("preview", previewKey);
  }
  copyFileSync(planFile, path.join(outDir, "scene-plan.json"));
  writeFileSync(path.join(outDir, "captions.srt"), toSrt(plan.captions.map((c) => ({ ...c, words: phrases[Number(c.id.slice(1))].words }))));
  if (o.previewOnly) {
    log("job", `preview ready: ${preview}`);
    return { jobId, outDir, preview, final: null as string | null, plan };
  }

  // 9. Full render + mux
  const videoFile = path.join(jobDir, "video.mp4");
  const final = path.join(outDir, "final.mp4");
  if (!done("render", planKey) || !existsSync(videoFile)) {
    await timed("render", () => renderVideo(plan, style, videoFile, { concurrency: o.concurrency }));
    mark("render", planKey);
  }
  const muxKey = hashOf({ planKey, audioKey });
  if (!done("mux", muxKey) || !existsSync(final)) {
    await mux(videoFile, audioFinal, final);
    mark("mux", muxKey);
  }

  // 10. Cover: frame where the hook title is complete (or the first tier landing)
  const hook = plan.graphics.find((g) => g.kind === "hook");
  const coverAt = hook ? Math.min(hook.end - 0.25, (hook.kind === "hook" ? hook.data.times[hook.data.times.length - 1] : 0) + 0.3) : plan.tierBoard?.events[0] ? plan.tierBoard.events[0].placeAt + 0.5 : 0.5;
  await run("ffmpeg", ["-v", "error", "-y", "-ss", Math.max(0, coverAt).toFixed(3), "-i", final, "-frames:v", "1", "-q:v", "2", path.join(outDir, "cover.jpg")]);

  // 11. QA
  const checks = await timed("qa", () => runQa({ plan, style, final, jobDir, outDir, modelDir: rel(style.transcription.local.modelDir), warnings: v.warnings, flagged,
    uncertain: uncertainWords(srcWords, style), cuts: edl.cuts, sourceFaceRate }));
  const report = reportMarkdown(plan, checks, { flagged, warnings: v.warnings, uncertain: uncertainWords(srcWords, style), cuts: edl.cuts,
    fonts: (["heading", "caption", "body"] as const).map((k) => `${k}: ${fonts[k].source}`), source: input, timings, corrections: applied });
  writeFileSync(path.join(outDir, "qa-report.md"), report);
  const failed = checks.filter((c) => c.status === "FAIL");
  log("qa", `${checks.filter((c) => c.status === "PASS").length} pass, ${checks.filter((c) => c.status === "WARN").length} warn, ${failed.length} fail, ${checks.filter((c) => c.status === "NOT CHECKED").length} not checked`);
  for (const f of failed) log("qa", `FAIL ${f.name}: ${f.detail}`);
  return { jobId, outDir, preview, final, plan, checks };
}
