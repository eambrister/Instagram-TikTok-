// Voice-first audio: same frame-snapped segments as the picture, micro-fades at every join, gentle cleanup,
// optional licensed music ducked under speech, two-pass loudness normalisation, then measured.
import { spawn } from "node:child_process";
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

/** Music level relative to the voice in 0.4 s windows where the voice is active (what a listener hears). */
export async function speechMasking(voice: string, music: string) {
  const load = async (f: string) => {
    const r = await new Promise<Buffer>((res, rej) => {
      const chunks: Buffer[] = [];
      const p = spawn("ffmpeg", ["-v", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"]);
      p.stdout.on("data", (d) => chunks.push(d));
      p.on("close", () => res(Buffer.concat(chunks)));
      p.on("error", rej);
    });
    return new Int16Array(r.buffer, r.byteOffset, Math.floor(r.length / 2));
  };
  const [v, m] = await Promise.all([load(voice), load(music)]);
  const w = 6400;
  const db = (x: Int16Array, i: number) => {
    let s = 0;
    for (let k = i; k < i + w; k++) s += (x[k] / 32768) ** 2;
    return 10 * Math.log10(s / w + 1e-12);
  };
  const diffs: number[] = [];
  for (let i = 0; i + w < Math.min(v.length, m.length); i += w) {
    const vd = db(v, i);
    if (vd > -35) diffs.push(vd - db(m, i));
  }
  diffs.sort((x, y) => x - y);
  const r1 = (x: number) => Math.round(x * 10) / 10;
  return { median: r1(diffs[Math.floor(diffs.length / 2)] ?? NaN), min: r1(diffs[0] ?? NaN), p10: r1(diffs[Math.floor(diffs.length * 0.1)] ?? NaN) };
}

export async function buildAudio(plan: ScenePlan, srcWav: string, jobDir: string, style: HouseStyle, music: string | null) {
  const a = style.audio;
  const fade = a.fadeMs / 1000;
  const parts = plan.segments.map((sg, i) => {
    const d = sg.srcEnd - sg.srcStart;
    return `[0:a]atrim=start=${sg.srcStart.toFixed(6)}:end=${sg.srcEnd.toFixed(6)},asetpts=PTS-STARTPTS,afade=t=in:d=${fade},afade=t=out:st=${Math.max(0, d - fade).toFixed(6)}:d=${fade}[s${i}]`;
  });
  const clean = [`highpass=f=${a.highpassHz}`, a.denoise === "light" ? "afftdn=nr=6:nf=-50:tn=1" : null].filter(Boolean).join(",");
  const voiceGraph = [...parts, `${plan.segments.map((_, i) => `[s${i}]`).join("")}concat=n=${plan.segments.length}:v=0:a=1,${clean}[voice]`];
  const scriptFile = path.join(jobDir, "audio-graph.txt");
  writeFileSync(scriptFile, voiceGraph.join(";\n"));
  const voice = path.join(jobDir, "stem-voice.wav");
  await run("ffmpeg", ["-v", "error", "-y", "-i", srcWav, "-filter_complex_script", scriptFile, "-map", "[voice]", "-ar", "48000", "-t", String(plan.duration), voice]);
  let edited = voice;
  let musicUnderVoiceDb: number | null = null;
  if (music) {
    // Levels are set relative to THIS voice: music starts musicUnderVoiceDb below it, and the sidechain
    // threshold sits 12 dB under the voice so ducking engages on every phrase, however quiet the recording.
    const v = await measureLoudness(voice);
    const mu = await measureLoudness(music);
    const gain = v.integratedLufs - a.musicUnderVoiceDb - mu.integratedLufs;
    const threshold = Math.pow(10, (v.integratedLufs - 12) / 20);
    const mixGraph = [
      `[0:a]asplit=2[v1][vkey]`,
      `[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=${gain.toFixed(2)}dB,atrim=0:${plan.duration},afade=t=out:st=${Math.max(0, plan.duration - 2).toFixed(2)}:d=2[m]`,
      `[m][vkey]sidechaincompress=threshold=${threshold.toFixed(5)}:ratio=4:attack=30:release=500:makeup=1,asplit=2[md][mstem]`,
      `[v1][md]amix=inputs=2:duration=first:normalize=0[mix]`,
    ];
    const mixFile = path.join(jobDir, "audio-mix-graph.txt");
    writeFileSync(mixFile, mixGraph.join(";\n"));
    edited = path.join(jobDir, "audio-edited.wav");
    const stem = path.join(jobDir, "stem-music.wav");
    await run("ffmpeg", ["-v", "error", "-y", "-i", voice, "-stream_loop", "-1", "-i", music, "-filter_complex_script", mixFile,
      "-map", "[mix]", "-ar", "48000", "-t", String(plan.duration), edited, "-map", "[mstem]", "-ar", "48000", "-t", String(plan.duration), stem]);
    const sp = await speechMasking(voice, stem);
    musicUnderVoiceDb = sp.median;
    log("audio", `music under voice while speaking: median ${sp.median} dB, closest ${sp.min} dB (target >= ${a.musicUnderVoiceDb})`);
  }

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
  return { final, measure: m, normalizationType: j.normalization_type as string, musicUnderVoiceDb };
}

export async function mux(video: string, audio: string, out: string) {
  await run("ffmpeg", ["-v", "error", "-y", "-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
    "-ar", "48000", "-movflags", "+faststart", out]);
}
