// npm run batch -- [--dir input] [--mode auto] [--intensity medium] [--jobs N]
// Edits every video in a folder. Jobs are isolated and resumable; parallelism is limited by free memory.
import { readdirSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { parseArgs } from "node:util";
import { runJob } from "../pipeline/job";
import { parseDirection } from "../pipeline/planner";
import { renderConcurrency } from "../pipeline/render";
import { rel } from "../pipeline/util";

const { values } = parseArgs({ options: { dir: { type: "string", default: "input" }, mode: { type: "string", default: "auto" },
  intensity: { type: "string" }, direction: { type: "string", default: "" }, jobs: { type: "string" } } });

const dir = path.resolve(rel("."), values.dir!);
const files = readdirSync(dir).filter((f) => /\.(mov|mp4|m4v|hevc)$/i.test(f)).map((f) => path.join(dir, f));
// ~4 GB per concurrent job (Chromium tabs + ffmpeg + Whisper); never more jobs than half the cores.
const jobs = Math.max(1, Math.min(Number(values.jobs ?? Infinity), Math.floor(os.freemem() / 4e9), Math.floor(os.cpus().length / 2), files.length));
console.log(`${files.length} videos, ${jobs} at a time`);

const modes: Record<string, any> = { auto: "auto", talking_head: "TALKING_HEAD", explainer: "EXPLAINER", ranking: "RANKING" };
const queue = [...files];
const results: { file: string; ok: boolean; msg: string }[] = [];
async function worker() {
  for (let f = queue.shift(); f; f = queue.shift()) {
    const d = parseDirection(values.direction!);
    if (values.mode !== "auto") d.mode = modes[values.mode!.toLowerCase()];
    if (values.intensity) d.intensity = values.intensity as any;
    try {
      const r = await runJob({ input: f, direction: d, music: null, previewOnly: false, force: false, concurrency: renderConcurrency(jobs) });
      results.push({ file: f, ok: true, msg: r.final ?? "" });
    } catch (e: any) {
      results.push({ file: f, ok: false, msg: e.message.split("\n")[0] });
    }
  }
}
Promise.all(Array.from({ length: jobs }, worker)).then(() => {
  console.log("\nBatch summary:");
  for (const r of results) console.log(`${r.ok ? "OK  " : "FAIL"} ${path.basename(r.file)} -> ${r.msg}`);
  process.exit(results.some((r) => !r.ok) ? 1 : 0);
});
