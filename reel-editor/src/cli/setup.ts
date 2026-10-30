// npm run setup [-- --fetch-model]
// Creates the Python env, resolves fonts (Heading Now / Gotham if supplied, else OFL fallbacks) and checks the
// local Whisper model. --fetch-model downloads it (see README: "Transcription model" for provenance).
import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import path from "node:path";
import { parseArgs } from "node:util";
import { loadStyle } from "../pipeline/config";
import { PY, py, rel, run } from "../pipeline/util";

const { values } = parseArgs({ options: { "fetch-model": { type: "boolean", default: false } } });

async function main() {
  if (!existsSync(PY)) {
    console.log("Creating Python venv (.venv) ...");
    await run("python3", ["-m", "venv", rel(".venv")]);
  }
  await run(PY, ["-m", "pip", "install", "-q", "faster-whisper==1.2.1", "opencv-python-headless<5", "fonttools", "brotli", "numpy", "pillow"]);
  console.log("Python deps OK");

  mkdirSync(rel("public/fonts"), { recursive: true });
  mkdirSync(rel("cache/empty-public"), { recursive: true });
  const r = await py("fonts.py", ["resolve", rel("brand-assets/fonts"), rel("../brand/fonts"), rel("node_modules/@fontsource/inter/files"), rel("public/fonts"), rel("cache/fonts.json")]);
  console.log("Fonts:", r.stdout.trim());

  const style = loadStyle();
  const dir = rel(style.transcription.local.modelDir);
  if (!existsSync(path.join(dir, "model.bin"))) {
    if (!values["fetch-model"]) {
      console.log(`\nLocal Whisper model missing at ${dir}.\nRun: npm run setup -- --fetch-model   (≈250 MB download, see README)`);
      return;
    }
    await fetchModel(dir);
  }
  console.log(`Whisper model OK (${dir})`);
}

// Whisper "small" (MIT) converted to CTranslate2 int8, as published in four npm data packages.
// Only data files are extracted (no scripts run). The checksum is the package's own; it proves the parts
// were reassembled intact, not upstream provenance.
async function fetchModel(dir: string) {
  mkdirSync(dir, { recursive: true });
  const tmp = rel("cache/model-download");
  mkdirSync(tmp, { recursive: true });
  const parts: string[] = [];
  for (let i = 0; i < 4; i++) {
    const name = `shortmovie-telop-model-p${i}`;
    const url = `https://registry.npmjs.org/@skillninja/${name}/-/${name}-1.0.0.tgz`;
    console.log(`Downloading ${url}`);
    const tgz = path.join(tmp, `${name}.tgz`);
    await run("curl", ["-sSfL", "-o", tgz, url]);
    const out = path.join(tmp, `p${i}`);
    mkdirSync(out, { recursive: true });
    await run("tar", ["-xzf", tgz, "-C", out, "--no-same-owner"]);
    parts.push(path.join(out, "package", `model.bin.part${i}`));
    if (i === 0) for (const f of ["config.json", "tokenizer.json", "vocabulary.json", "preprocessor_config.json", "LICENSE", "model.sha256"])
      writeFileSync(path.join(dir, f), readFileSync(path.join(out, "package", f)));
  }
  const h = createHash("sha256");
  const chunks = parts.map((p) => readFileSync(p));
  chunks.forEach((c) => h.update(c));
  const expected = readFileSync(path.join(dir, "model.sha256"), "utf8").trim().split(/\s+/)[0];
  if (h.digest("hex") !== expected) throw new Error("Model checksum mismatch; not installing.");
  writeFileSync(path.join(dir, "model.bin.tmp"), Buffer.concat(chunks));
  renameSync(path.join(dir, "model.bin.tmp"), path.join(dir, "model.bin"));
}

main().catch((e) => {
  console.error(e.message);
  process.exit(1);
});
