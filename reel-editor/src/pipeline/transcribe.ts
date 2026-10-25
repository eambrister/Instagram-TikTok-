// Word-timestamp transcription with pluggable providers and a content-keyed cache.
// Local faster-whisper is the default. The OpenAI provider only runs when explicitly enabled in
// config AND its API key env var is set; footage audio is never sent anywhere otherwise.
import { readFileSync, statSync } from "node:fs";
import path from "node:path";
import type { HouseStyle } from "./config";
import { ensureDir, exists, hashOf, log, py, readJson, rel, writeJson } from "./util";

export type Word = { text: string; start: number; end: number; p: number | null };
export type Transcript = { engine: string; model: string; language: string; words: Word[]; cacheKey: string };
export type Correction = { at: number; from: string; to: string };

export async function transcribe(asrWav: string, sourceSha: string, style: HouseStyle): Promise<Transcript> {
  const t = style.transcription;
  const provider = t.provider;
  const cfg = provider === "openai" ? t.openai : t.local;
  const cacheKey = hashOf({ sourceSha, provider, cfg: { ...cfg, threads: undefined }, language: t.language, vocab: t.vocabulary });
  const cacheFile = rel("cache/transcripts", `${cacheKey}.json`);
  if (exists(cacheFile)) {
    log("transcribe", `cache hit ${cacheKey}`);
    return readJson(cacheFile);
  }
  let result: Omit<Transcript, "cacheKey">;
  if (provider === "local-faster-whisper") {
    const modelDir = rel(t.local.modelDir);
    if (!exists(path.join(modelDir, "model.bin")))
      throw new Error(`Local Whisper model missing at ${modelDir}. Run "npm run setup" (see README: Transcription model).`);
    const out = path.join(ensureDir(rel("cache/transcripts")), `${cacheKey}.raw.json`);
    log("transcribe", `local faster-whisper (${path.basename(modelDir)})`);
    const prompt = t.vocabulary.length ? `Fitness coaching video. Vocabulary: ${t.vocabulary.join(", ")}.` : "";
    await py("transcribe.py", [asrWav, modelDir, out, "--language", t.language, "--prompt", prompt, "--threads", String(t.local.threads)]);
    const raw = readJson(out);
    result = { engine: raw.engine, model: path.basename(modelDir), language: raw.language, words: raw.words };
  } else {
    if (!t.openai.enabled) throw new Error("OpenAI transcription is not enabled in config/house-style.json (transcription.openai.enabled).");
    const key = process.env[t.openai.apiKeyEnv];
    if (!key) throw new Error(`OpenAI transcription selected but ${t.openai.apiKeyEnv} is not set. No key will be invented.`);
    if (statSync(asrWav).size > 24e6) throw new Error("Audio exceeds the OpenAI 25 MB upload limit; split the recording or use the local provider.");
    log("transcribe", `OpenAI ${t.openai.model} (paid API, audio leaves this machine)`);
    const form = new FormData();
    form.append("file", new Blob([readFileSync(asrWav)]), "audio.wav");
    form.append("model", t.openai.model);
    form.append("response_format", "verbose_json");
    form.append("timestamp_granularities[]", "word");
    form.append("language", t.language);
    if (t.vocabulary.length) form.append("prompt", t.vocabulary.join(", "));
    const res = await fetch("https://api.openai.com/v1/audio/transcriptions", { method: "POST", headers: { Authorization: `Bearer ${key}` }, body: form });
    if (!res.ok) throw new Error(`OpenAI transcription failed: ${res.status} ${await res.text()}`);
    const j: any = await res.json();
    result = { engine: "openai", model: t.openai.model, language: j.language,
      words: (j.words ?? []).map((w: any) => ({ text: w.word, start: w.start, end: w.end, p: null })) };
  }
  const full = { ...result, cacheKey };
  writeJson(cacheFile, full);
  return full;
}

/**
 * Apply reviewed corrections (word nearest `at` whose text matches `from`). Timing is preserved.
 * `to: ""` deletes a word Eddie did not say; its span is returned as `notSpeech` so the edit treats it as silence.
 */
export function applyCorrections(words: Word[], corrections: Correction[]): { words: Word[]; applied: string[]; notSpeech: { start: number; end: number }[] } {
  const out: (Word & { deleted?: boolean })[] = words.map((w) => ({ ...w }));
  const applied: string[] = [];
  const notSpeech: { start: number; end: number }[] = [];
  for (const c of corrections) {
    const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9']/g, "");
    let best = -1;
    let bestD = 1.5;
    out.forEach((w, i) => {
      const d = Math.abs(w.start - c.at);
      if (norm(w.text) === norm(c.from) && d < bestD) (best = i), (bestD = d);
    });
    if (best >= 0 && c.to === "") {
      out[best].deleted = true;
      notSpeech.push({ start: out[best].start, end: out[best].end });
      applied.push(`removed "${c.from}" @${c.at}s (not said)`);
    } else if (best >= 0) {
      const punct = out[best].text.match(/[.,!?;:]+$/)?.[0] ?? "";
      out[best].text = c.to + (c.to.match(/[.,!?;:]$/) ? "" : punct);
      out[best].p = 1;
      applied.push(`${c.from} -> ${c.to} @${c.at}s`);
    }
  }
  return { words: out.filter((w) => !w.deleted).map(({ deleted, ...w }) => w), applied, notSpeech };
}

const NUMBER_RE = /^\$?\d|^(zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|half)\b/i;

/** Words to flag for review: low confidence, uncertain numbers, unfamiliar capitalised names. */
export function uncertainWords(words: Word[], style: HouseStyle) {
  const vocab = new Set(style.transcription.vocabulary.flatMap((v) => v.toLowerCase().split(/\s+/)));
  return words
    .map((w, i) => {
      const bare = w.text.replace(/[^A-Za-z0-9'$%]/g, "");
      const reasons: string[] = [];
      if (w.p !== null && w.p < style.transcription.uncertainBelow) reasons.push(`low confidence ${w.p}`);
      if (NUMBER_RE.test(bare) && w.p !== null && w.p < 0.85) reasons.push("number below 0.85 confidence");
      if (i > 0 && /^[A-Z][a-z]+/.test(bare) && !/[.!?]$/.test(words[i - 1].text) && !vocab.has(bare.toLowerCase()) && (w.p ?? 1) < 0.8)
        reasons.push("possible name");
      return reasons.length ? { index: i, text: w.text, at: w.start, reasons } : null;
    })
    .filter((x): x is NonNullable<typeof x> => x !== null);
}
