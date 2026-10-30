// Remotion render of the silent picture. Media is served from a localhost-only static server so large
// proxies are not copied into the bundle.
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import { createReadStream, existsSync, readdirSync, statSync } from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import type { ScenePlan } from "../shared/plan";
import type { HouseStyle } from "./config";
import { log, rel, ROOT } from "./util";

const ALLOWED = ["jobs/", "public/", "licensed-media/"];
const TYPES: Record<string, string> = { ".mp4": "video/mp4", ".ttf": "font/ttf", ".otf": "font/otf", ".png": "image/png", ".webp": "image/webp", ".jpg": "image/jpeg" };

export async function startMediaServer(): Promise<{ base: string; close: () => void }> {
  const server = http.createServer((req, res) => {
    const url = decodeURIComponent((req.url ?? "/").split("?")[0]).replace(/^\/+/, "");
    const file = path.resolve(ROOT, url);
    if (!ALLOWED.some((p) => url.startsWith(p)) || !file.startsWith(ROOT + path.sep) || !existsSync(file) || !statSync(file).isFile()) {
      res.writeHead(404).end();
      return;
    }
    const size = statSync(file).size;
    const headers = { "Content-Type": TYPES[path.extname(file)] ?? "application/octet-stream", "Accept-Ranges": "bytes", "Access-Control-Allow-Origin": "*" };
    const m = (req.headers.range ?? "").match(/bytes=(\d*)-(\d*)/);
    if (m) {
      const start = m[1] ? Number(m[1]) : 0;
      const end = m[2] ? Number(m[2]) : size - 1;
      res.writeHead(206, { ...headers, "Content-Range": `bytes ${start}-${end}/${size}`, "Content-Length": end - start + 1 });
      createReadStream(file, { start, end }).pipe(res);
    } else {
      res.writeHead(200, { ...headers, "Content-Length": size });
      createReadStream(file).pipe(res);
    }
  });
  await new Promise<void>((r) => server.listen(0, "127.0.0.1", r));
  const port = (server.address() as any).port;
  return { base: `http://127.0.0.1:${port}/`, close: () => server.close() };
}

let bundled: Promise<string> | null = null;
export function getBundle() {
  bundled ??= bundle({ entryPoint: rel("src/remotion/index.ts"), publicDir: rel("cache/empty-public"), onProgress: () => undefined });
  return bundled;
}

/** Remotion's own headless shell when available, else the preinstalled Playwright headless shell. */
export function browserExecutable(): string | null {
  if (process.env.REMOTION_BROWSER) return process.env.REMOTION_BROWSER;
  const base = "/opt/pw-browsers";
  if (!existsSync(base)) return null;
  for (const d of readdirSync(base).filter((x) => x.startsWith("chromium_headless_shell"))) {
    for (const sub of readdirSync(path.join(base, d))) {
      const f = path.join(base, d, sub, "chrome-headless-shell");
      if (existsSync(f)) return f;
    }
  }
  return null;
}

export function renderConcurrency(jobsInParallel = 1) {
  const cpu = os.cpus().length;
  const memGb = os.freemem() / 1e9;
  // Each Chromium tab rendering 1080x1920 + OffthreadVideo cache needs roughly 0.8-1.2 GB.
  return Math.max(1, Math.min(Math.floor(cpu / jobsInParallel), Math.floor(memGb / jobsInParallel / 1.2)));
}

/** Headless Chromium occasionally dies ("Target closed"); retry once with fewer tabs before failing the job. */
export async function renderVideo(plan: ScenePlan, style: HouseStyle, out: string, opts: { frameRange?: [number, number]; concurrency?: number } = {}) {
  const c = opts.concurrency ?? renderConcurrency();
  try {
    await renderOnce(plan, style, out, { ...opts, concurrency: c });
  } catch (e: any) {
    if (!/Target closed|Protocol error|crashed/i.test(String(e?.message))) throw e;
    log("render", `browser crashed (${String(e.message).split("\n")[0]}); retrying once with concurrency ${Math.max(1, Math.floor(c / 2))}`);
    await renderOnce(plan, style, out, { ...opts, concurrency: Math.max(1, Math.floor(c / 2)) });
  }
}

async function renderOnce(plan: ScenePlan, style: HouseStyle, out: string, opts: { frameRange?: [number, number]; concurrency: number }) {
  const serveUrl = await getBundle();
  const media = await startMediaServer();
  try {
    const inputProps = { plan, mediaBase: media.base };
    const browser = browserExecutable();
    const composition = await selectComposition({ serveUrl, id: "Reel", inputProps, browserExecutable: browser, logLevel: "error" });
    let last = -1;
    const t0 = Date.now();
    await renderMedia({
      serveUrl,
      composition,
      inputProps,
      codec: "h264",
      outputLocation: out,
      muted: true,
      crf: style.output.crf,
      x264Preset: style.output.x264Preset as any,
      pixelFormat: "yuv420p",
      colorSpace: "bt709",
      frameRange: opts.frameRange ?? null,
      concurrency: opts.concurrency,
      browserExecutable: browser,
      offthreadVideoCacheSizeInBytes: 1024 * 1024 * 1024,
      chromiumOptions: { gl: "swangle" },
      timeoutInMilliseconds: 120000,
      logLevel: process.env.REMOTION_LOG === "verbose" ? "verbose" : "warn",
      onProgress: ({ progress }) => {
        const pct = Math.floor(progress * 10) * 10;
        if (pct !== last) {
          last = pct;
          log("render", `${pct}% (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
        }
      },
    });
  } finally {
    media.close();
  }
}
