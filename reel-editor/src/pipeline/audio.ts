// Voice-first audio: same frame-snapped segments as the picture, micro-fades at every join, gentle cleanup,
// optional licensed music ducked under speech, two-pass loudness normalisation, then measured.
import { writeFileSync } from "node:fs";
import path from "node:path";
import type { ScenePlan } from "../shared/plan";
import type { HouseStyle } from "./config";
import { log, run } from "./util";

export type AudioMeasure = { integratedLufs: number; truePeakDb: number; lra: number; maxVolumeDb: number };

export async function measureLoudness(file: string): Promise<AudioMeasure> {
  const r = await run("ffmpeg", ["-v", "info", "-nostats", "-i", file, "-af", "ebur128=peak=true,volumedetect", "-f", "null", "-"], { allowFail: true });
  const s = r.stderr;
  const summary = s.slice(s.lastIndexOf("Summary:"));
  const num = (re: RegExp, src = summary) => Number((src.match(re) ?? [])[1]);
  return {
    integratedLufs: num(/I:\s+(-?[\d.]+) LUFS/),
    truePeakDb: num(/Peak:\s+(-?[\d.]+|-inf) dBFS/),
    lra: num(/LRA:\s+(-?[\d.]+) LU/),
    maxVolumeDb: num(/max_volume: (-?[\d.]+) dB/, s),
  };
}

export async function buildAudio(plan: ScenePlan, srcWav: string, jobDir: string, style: HouseStyle, music: string | null) {
  const a = style.audio;
  const fade = a.fadeMs / 1000;
  const parts = plan.segments.map((sg, i) => {
    const d = sg.srcEnd - sg.srcStart;
    return `[0:a]atrim=start=${sg.srcStart.toFixed(6)}:end=${sg.srcEnd.toFixed(6)},asetpts=PTS-STARTPTS,afade=t=in:d=${fade},afade=t=out:st=${Math.max(0, d - fade).toFixed(6)}:d=${fade}[s${i}]`;
  });
  const clean = [`highpass=f=${a.highpassHz}`, a.denoise === "light" ? "afftdn=nr=6:nf=-50:tn=1" : null].filter(Boolean).join(",");
  const graph = [...parts, `${plan.segments.map((_, i) => `[s${i}]`).join("")}concat=n=${plan.segments.length}:v=0:a=1,${clean}[voice]`];
  const inputs = ["-i", srcWav];
  let outLabel = "voice";
  if (music) {
    inputs.push("-stream_loop", "-1", "-i", music);
    graph.push(
      `[voice]asplit=2[v1][vkey]`,
      `[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=${a.musicDuckDb}dB,atrim=0:${plan.duration}[m]`,
      `[m][vkey]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md]`,
      `[v1][md]amix=inputs=2:duration=first:normalize=0[mix]`,
    );
    outLabel = "mix";
  }
  const scriptFile = path.join(jobDir, "audio-graph.txt");
  writeFileSync(scriptFile, graph.join(";\n"));
  const edited = path.join(jobDir, "audio-edited.wav");
  await run("ffmpeg", ["-v", "error", "-y", ...inputs, "-filter_complex_script", scriptFile, "-map", `[${outLabel}]`, "-ar", "48000", "-t", String(plan.duration), edited]);

  // Two-pass loudnorm (linear mode keeps dynamics; it falls back to dynamic only if the target is unreachable).
  const ln = `loudnorm=I=${a.targetLufs}:TP=${a.truePeakDb}:LRA=${a.lra}`;
  const p1 = await run("ffmpeg", ["-v", "info", "-nostats", "-i", edited, "-af", `${ln}:print_format=json`, "-f", "null", "-"]);
  const j = JSON.parse(p1.stderr.slice(p1.stderr.lastIndexOf("{"), p1.stderr.lastIndexOf("}") + 1));
  const final = path.join(jobDir, "audio-final.wav");
  await run("ffmpeg", ["-v", "error", "-y", "-i", edited, "-af",
    `${ln}:measured_I=${j.input_i}:measured_TP=${j.input_tp}:measured_LRA=${j.input_lra}:measured_thresh=${j.input_thresh}:offset=${j.target_offset}:linear=true,aresample=48000`,
    "-ar", "48000", final]);
  const m = await measureLoudness(final);
  log("audio", `voice ${j.input_i} LUFS -> ${m.integratedLufs} LUFS, true peak ${m.truePeakDb} dBTP${music ? " (music ducked)" : ""}`);
  return { final, measure: m, normalizationType: j.normalization_type as string };
}

export async function mux(video: string, audio: string, out: string) {
  await run("ffmpeg", ["-v", "error", "-y", "-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
    "-ar", "48000", "-movflags", "+faststart", out]);
}
