// Probe and normalise a recording without touching the original:
// orientation applied, VFR -> CFR, HDR (HLG/PQ) tone-mapped to SDR BT.709, HEVC decoded.
import path from "node:path";
import { exists, log, run } from "./util";

export type Probe = {
  file: string;
  codec: string;
  codedWidth: number;
  codedHeight: number;
  rotation: number;
  displayWidth: number;
  displayHeight: number;
  fps: number;
  avgFps: number;
  vfr: boolean;
  duration: number;
  pixFmt: string;
  transfer: string | null;
  primaries: string | null;
  matrix: string | null;
  hdr: "hlg" | "pq" | null;
  hasAudio: boolean;
  audioRate: number | null;
  audioChannels: number | null;
};

const ratio = (s?: string) => {
  if (!s || !s.includes("/")) return Number(s) || 0;
  const [a, b] = s.split("/").map(Number);
  return b ? a / b : 0;
};

export async function probe(file: string): Promise<Probe> {
  const r = await run("ffprobe", ["-v", "error", "-show_streams", "-show_format", "-of", "json", file]);
  const j = JSON.parse(r.stdout);
  const v = j.streams.find((s: any) => s.codec_type === "video" && s.disposition?.attached_pic !== 1);
  const a = j.streams.find((s: any) => s.codec_type === "audio");
  if (!v) throw new Error(`No video stream in ${file}`);
  let rotation = 0;
  for (const sd of v.side_data_list ?? []) if (typeof sd.rotation === "number") rotation = sd.rotation;
  if (!rotation && v.tags?.rotate) rotation = -Number(v.tags.rotate);
  rotation = ((Math.round(rotation) % 360) + 360) % 360;
  const swap = rotation === 90 || rotation === 270;
  const fps = ratio(v.r_frame_rate);
  const avgFps = ratio(v.avg_frame_rate);
  const transfer = v.color_transfer ?? null;
  const hdr = transfer === "arib-std-b67" ? "hlg" : transfer === "smpte2084" ? "pq" : null;
  return {
    file,
    codec: v.codec_name,
    codedWidth: v.width,
    codedHeight: v.height,
    rotation,
    displayWidth: swap ? v.height : v.width,
    displayHeight: swap ? v.width : v.height,
    fps,
    avgFps,
    vfr: Math.abs(fps - avgFps) > 0.05 || v.r_frame_rate !== v.avg_frame_rate,
    duration: Number(j.format.duration ?? v.duration),
    pixFmt: v.pix_fmt,
    transfer,
    primaries: v.color_primaries ?? null,
    matrix: v.color_space ?? null,
    hdr,
    hasAudio: !!a,
    audioRate: a ? Number(a.sample_rate) : null,
    audioChannels: a ? Number(a.channels) : null,
  };
}

export function chooseFps(p: Probe, base: number, match60: boolean) {
  return match60 && p.avgFps > 50 ? 60 : base;
}

/**
 * Proxy keeps enough pixels for a 1080x1920 crop with ~12% zoom headroom (1210x2150) and never upscales.
 * A landscape 4K source therefore keeps its full height, so the vertical crop stays native resolution.
 */
export function proxySize(p: Probe) {
  const s = Math.min(1, Math.max(1210 / p.displayWidth, 2150 / p.displayHeight));
  const even = (n: number) => Math.max(2, Math.round((n * s) / 2) * 2);
  return { width: even(p.displayWidth), height: even(p.displayHeight) };
}

export function toneMapFilter(p: Probe): string[] {
  if (!p.hdr) return [];
  const tin = p.hdr === "hlg" ? "arib-std-b67" : "smpte2084";
  // Linearise, convert BT.2020 -> BT.709 primaries, compress highlights with mobius (keeps mid-tones and
  // skin largely linear instead of crushing them), then encode BT.709 SDR.
  return [
    `zscale=tin=${tin}:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=203`,
    "format=gbrpf32le",
    "zscale=p=bt709",
    "tonemap=tonemap=mobius:param=0.35:desat=0",
    "zscale=t=bt709:m=bt709:r=tv",
  ];
}

export async function makeProxy(p: Probe, outDir: string, fps: number) {
  const proxy = path.join(outDir, "proxy.mp4");
  const audio = path.join(outDir, "audio.wav");
  const asr = path.join(outDir, "asr.wav");
  const { width, height } = proxySize(p);
  if (!exists(proxy)) {
    const vf = [...toneMapFilter(p), `scale=${width}:${height}:flags=lanczos`, "format=yuv420p", `fps=${fps}`].join(",");
    log("ingest", `proxy ${p.displayWidth}x${p.displayHeight}${p.hdr ? ` ${p.hdr.toUpperCase()}->SDR` : ""}${p.vfr ? " VFR->CFR" : ""} -> ${width}x${height}@${fps}`);
    await run("ffmpeg", ["-v", "error", "-y", "-i", p.file, "-map", "0:v:0", "-an", "-vf", vf, "-fps_mode", "cfr",
      "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-g", String(fps / 2), "-bf", "0",
      "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart", proxy]);
  }
  if (!exists(audio)) {
    if (p.hasAudio) {
      await run("ffmpeg", ["-v", "error", "-y", "-i", p.file, "-map", "0:a:0", "-vn", "-af", "aresample=async=1:first_pts=0",
        "-ac", String(Math.min(2, p.audioChannels ?? 1)), "-ar", "48000", "-c:a", "pcm_s16le", audio]);
    } else {
      await run("ffmpeg", ["-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", String(p.duration), audio]);
    }
  }
  if (!exists(asr)) await run("ffmpeg", ["-v", "error", "-y", "-i", audio, "-ac", "1", "-ar", "16000", asr]);
  return { proxy, audio, asr, width, height };
}

/** Silence candidates from the audio (used to confirm transcript gaps before cutting). */
export async function detectSilence(audio: string, db: number, minDur: number) {
  const r = await run("ffmpeg", ["-v", "info", "-i", audio, "-af", `silencedetect=noise=${db}dB:d=${minDur}`, "-f", "null", "-"], { allowFail: true });
  const out: { start: number; end: number }[] = [];
  let s: number | null = null;
  for (const line of r.stderr.split("\n")) {
    const a = line.match(/silence_start: ([\d.]+)/);
    const b = line.match(/silence_end: ([\d.]+)/);
    if (a) s = Number(a[1]);
    if (b && s !== null) {
      out.push({ start: s, end: Number(b[1]) });
      s = null;
    }
  }
  return out;
}
