import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { createReadStream, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
export const PY = path.join(ROOT, ".venv/bin/python");
export const rel = (...p: string[]) => path.join(ROOT, ...p);

export type RunResult = { code: number; stdout: string; stderr: string };

/** Spawn without a shell (paths with spaces are safe). Rejects on non-zero exit unless allowFail. */
export function run(cmd: string, args: string[], opts: { allowFail?: boolean; cwd?: string; quiet?: boolean } = {}): Promise<RunResult> {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, { cwd: opts.cwd ?? ROOT, env: process.env });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d));
    child.stderr.on("data", (d) => (stderr += d));
    child.on("error", reject);
    child.on("close", (code) => {
      const r = { code: code ?? -1, stdout, stderr };
      if (code !== 0 && !opts.allowFail) reject(new Error(`${cmd} ${args.slice(0, 6).join(" ")} … exited ${code}\n${stderr.slice(-2000)}`));
      else resolve(r);
    });
  });
}

export const py = (script: string, args: string[], opts: { allowFail?: boolean } = {}) =>
  run(PY, ["-I", rel("scripts", script), ...args], opts);

export function sha256File(file: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const h = createHash("sha256");
    createReadStream(file).on("data", (d) => h.update(d)).on("end", () => resolve(h.digest("hex"))).on("error", reject);
  });
}

export const hashOf = (v: unknown) => createHash("sha256").update(JSON.stringify(v)).digest("hex").slice(0, 16);

export function ensureDir(d: string) {
  mkdirSync(d, { recursive: true });
  return d;
}

export const readJson = <T = any>(f: string): T => JSON.parse(readFileSync(f, "utf8"));
export const writeJson = (f: string, v: unknown) => {
  ensureDir(path.dirname(f));
  writeFileSync(f, JSON.stringify(v, null, 1));
};
export const exists = existsSync;

export function log(stage: string, msg: string) {
  const t = new Date().toISOString().slice(11, 19);
  console.log(`[${t}] ${stage.padEnd(10)} ${msg}`);
}

export const round = (v: number, d = 3) => Math.round(v * 10 ** d) / 10 ** d;
export const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v));
