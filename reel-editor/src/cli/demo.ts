// npm run demo [-- --only ranking] [--preview-only]
// Builds fully synthetic test recordings (FFmpeg flite voice + generated picture: no real person, no reference
// footage) that exercise the hard ingest cases, then runs all three modes through the real pipeline.
// A synthetic demo proves the plumbing, NOT that Eddie's recording has been edited.
import { writeFileSync } from "node:fs";
import path from "node:path";
import { parseArgs } from "node:util";
import { runJob } from "../pipeline/job";
import { parseDirection, parseRankings } from "../pipeline/planner";
import { ensureDir, exists, rel, run } from "../pipeline/util";

const { values } = parseArgs({ options: { only: { type: "string" }, "preview-only": { type: "boolean", default: false }, force: { type: "boolean", default: false } } });

type Line = { text: string; pauseAfter: number };
// The flite test voice mangles "F tier" ("aft heaver"), so the ranking demo uses explicit --rankings, the same
// route Eddie uses when a spoken rank is unclear. Spoken-tier parsing is covered by unit tests on text.
const DEMOS: Record<string, { lines: Line[]; video: "portrait-hdr-vfr" | "landscape-rotated" | "portrait-sdr"; mode: string; rankings?: string; topic?: string }> = {
  "talking-head": {
    video: "portrait-sdr",
    mode: "auto",
    lines: [
      { text: "Motivation starts. Discipline finishes.", pauseAfter: 0.25 },
      { text: "You already know what to do.", pauseAfter: 1.6 },
      { text: "I was going to, I was going to tell you the hard part.", pauseAfter: 0.3 },
      { text: "Remember, the plan only works on the days you show up.", pauseAfter: 0.3 },
      { text: "Stop waiting for Monday. Start today.", pauseAfter: 0.4 },
    ],
  },
  explainer: {
    video: "portrait-hdr-vfr",
    mode: "auto",
    lines: [
      { text: "Walking is the easiest habit to stack.", pauseAfter: 0.3 },
      { text: "Walk for 30 minutes after dinner.", pauseAfter: 0.3 },
      { text: "Do that 5 days a week.", pauseAfter: 0.3 },
      { text: "That is 150 minutes every week.", pauseAfter: 1.4 },
      { text: "Pick a short walk instead of the couch.", pauseAfter: 0.4 },
    ],
  },
  ranking: {
    video: "landscape-rotated",
    mode: "auto",
    rankings: "Memory=F, Notebook=B, Photos=A, Coach=S",
    topic: "Tracking progress",
    lines: [
      { text: "Ranking ways to track your progress.", pauseAfter: 0.3 },
      { text: "Memory is F tier.", pauseAfter: 0.5 },
      { text: "A notebook is B tier.", pauseAfter: 0.5 },
      { text: "Weekly photos are A tier.", pauseAfter: 0.5 },
      { text: "A coach goes straight to S tier.", pauseAfter: 0.5 },
    ],
  },
};

async function synth(name: string, lines: Line[], kind: string, dir: string) {
  const out = path.join(dir, `${name}.mov`);
  if (exists(out)) return out;
  const parts: string[] = [];
  for (let i = 0; i < lines.length; i++) {
    const tf = path.join(dir, `${name}-${i}.txt`);
    writeFileSync(tf, lines[i].text);
    const wav = path.join(dir, `${name}-${i}.wav`);
    await run("ffmpeg", ["-v", "error", "-y", "-f", "lavfi", "-i", `flite=textfile='${tf}':voice=slt`, "-af", `apad=pad_dur=${lines[i].pauseAfter},aresample=48000`, "-ac", "1", wav]);
    parts.push(wav);
  }
  const list = path.join(dir, `${name}-list.txt`);
  writeFileSync(list, parts.map((p) => `file '${p}'`).join("\n"));
  const voice = path.join(dir, `${name}-voice.wav`);
  await run("ffmpeg", ["-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", list, "-af", "adelay=600|600,apad=pad_dur=0.8", voice]);
  const dur = Number((await run("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", voice])).stdout.trim());
  // Generated picture: gradient "set", a moving geometric subject and a label. Not a person.
  const [w, h] = kind === "landscape-rotated" ? [1920, 1080] : [1080, 1920];
  const label = kind === "portrait-hdr-vfr" ? "SYNTHETIC TEST  HEVC 10-bit HLG  VFR" : kind === "landscape-rotated" ? "SYNTHETIC TEST  rotated landscape" : "SYNTHETIC TEST  H.264 SDR";
  const font = rel("public/fonts/Body.ttf");
  const vf = [
    `drawbox=x=0:y=0:w=${w}:h=${h}:color=0x2a2f3a@1:t=fill`,
    `drawbox=x='${w / 2}-160+60*sin(t)':y='${h * 0.32}-160':w=320:h=320:color=0xd9a066@1:t=fill`,
    `drawbox=x='${w / 2}-240+60*sin(t)':y='${h * 0.32}+190':w=480:h=${Math.round(h * 0.5)}:color=0x3b6ea8@1:t=fill`,
    `drawtext=fontfile=${font}:text='${label}':x=40:y=40:fontsize=36:fontcolor=white`,
    `drawtext=fontfile=${font}:text='%{pts\\:hms}':x=40:y=90:fontsize=36:fontcolor=white`,
  ].join(",");
  const common = ["-v", "error", "-y", "-f", "lavfi", "-i", `color=c=black:s=${w}x${h}:r=30:d=${dur}`, "-i", voice, "-vf", vf, "-c:a", "aac", "-shortest"];
  if (kind === "portrait-hdr-vfr") {
    // Drop every 7th frame without retiming -> variable frame rate; tag as HLG BT.2020 like an iPhone HDR clip.
    await run("ffmpeg", [...common.slice(0, 9), "-vf", `${vf},select='not(eq(mod(n\\,7)\\,3))',format=yuv420p10le`, "-fps_mode", "vfr",
      "-c:v", "libx265", "-x265-params", "log-level=error:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc", "-tag:v", "hvc1",
      "-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", "-c:a", "aac", "-shortest", out]);
  } else if (kind === "landscape-rotated") {
    // Landscape pixels with a 90° display-matrix: players show it portrait (1080x1920).
    const tmp = path.join(dir, `${name}-land.mp4`);
    await run("ffmpeg", [...common, "-c:v", "libx264", "-pix_fmt", "yuv420p", tmp]);
    await run("ffmpeg", ["-v", "error", "-y", "-display_rotation:v:0", "90", "-i", tmp, "-c", "copy", out]);
  } else {
    await run("ffmpeg", [...common, "-c:v", "libx264", "-pix_fmt", "yuv420p", out]);
  }
  return out;
}

async function main() {
  const dir = ensureDir(rel("input/demo"));
  const names = values.only ? [values.only] : Object.keys(DEMOS);
  for (const n of names) {
    const d = DEMOS[n];
    const file = await synth(n, d.lines, d.video, dir);
    console.log(`\n=== demo: ${n} (${file})`);
    const direction = parseDirection("");
    if (d.rankings) direction.rankings = parseRankings(d.rankings);
    if (d.topic) direction.topic = d.topic;
    await runJob({ input: file, direction, music: null, previewOnly: values["preview-only"]!, force: values.force! });
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
