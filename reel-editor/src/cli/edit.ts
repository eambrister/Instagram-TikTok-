// npm run edit -- --input "input/my video.mov" [--mode auto|talking_head|explainer|ranking] [--intensity light|medium|high]
//   [--direction "plain-language notes"] [--topic "..."] [--pin-title] [--caption-gap "1.4-4.2"] [--broll "licensed-media/broll/x.mp4@4.3-9.5"] [--rankings "Eggs=S, Granola=F"] [--music original|hiphop|spooky|none|licensed-media/music/x.mp3]
//   [--preview-only] [--force]
import { parseArgs } from "node:util";
import { parseDirection, parseRankings } from "../pipeline/planner";
import { runJob } from "../pipeline/job";

const { values } = parseArgs({
  options: {
    input: { type: "string" },
    mode: { type: "string", default: "auto" },
    intensity: { type: "string" },
    direction: { type: "string", default: "" },
    topic: { type: "string" },
    "pin-title": { type: "boolean", default: false },
    "caption-gap": { type: "string" },
    broll: { type: "string" },
    rankings: { type: "string" },
    music: { type: "string" },
    "preview-only": { type: "boolean", default: false },
    force: { type: "boolean", default: false },
    concurrency: { type: "string" },
  },
});

if (!values.input) {
  console.error('Usage: npm run edit -- --input "input/my-video.mov" [--mode auto] [--direction "..."]');
  process.exit(2);
}
const modes: Record<string, any> = { auto: "auto", talking_head: "TALKING_HEAD", explainer: "EXPLAINER", ranking: "RANKING" };
const d = parseDirection(values.direction ?? "");
if (values.mode && values.mode !== "auto") {
  const m = modes[values.mode.toLowerCase()];
  if (!m) throw new Error(`Unknown mode ${values.mode}`);
  d.mode = m;
}
if (values.intensity) d.intensity = values.intensity as any;
if (values.topic) d.topic = values.topic;
if (values["pin-title"]) d.pinHook = true;
// "--broll file@4.3-9.5;file2@20-23": his own clips as cutaways over those output-time windows.
if (values.broll)
  d.broll = values.broll.split(";").map((s) => {
    const m = s.trim().match(/^(.+)@([\d.]+)-([\d.]+)$/);
    if (!m || !(Number(m[3]) > Number(m[2]))) throw new Error(`Bad B-roll "${s}". Use file@start-end in seconds.`);
    return { file: m[1], start: Number(m[2]), end: Number(m[3]) };
  });
// "--caption-gap 1.39-4.25,30-31.5": no captions starting in these output-time windows.
if (values["caption-gap"])
  d.captionGaps = values["caption-gap"].split(",").map((s) => {
    const [start, end] = s.split("-").map(Number);
    if (!(end > start)) throw new Error(`Bad caption gap "${s}". Use start-end in seconds.`);
    return { start, end };
  });
if (values.rankings) d.rankings = parseRankings(values.rankings);

runJob({ input: values.input, direction: d, music: values.music ?? null, previewOnly: values["preview-only"]!, force: values.force!,
  concurrency: values.concurrency ? Number(values.concurrency) : undefined })
  .then((r) => {
    console.log(`\nDone: ${r.final ?? r.preview}\nOutputs: ${r.outDir}`);
  })
  .catch((e) => {
    console.error(`\nFAILED: ${e.message}`);
    process.exit(1);
  });
