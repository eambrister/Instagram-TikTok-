import { z } from "zod";
import { readJson, rel } from "./util";

const level = z.object({ zoomMax: z.number(), changeEverySeconds: z.number(), entranceFrames: z.number().int(), punchChance: z.number() });

export const houseStyleSchema = z.object({
  brand: z.object({ name: z.string(), handle: z.string().nullable(), logo: z.string().nullable(), showBrandMark: z.boolean() }),
  output: z.object({ width: z.number().int(), height: z.number().int(), fps: z.number().int(), match60fpsSource: z.boolean(),
    crf: z.number(), x264Preset: z.string(), previewSeconds: z.number() }),
  colors: z.object({ captionText: z.string(), captionHighlight: z.string(), captionOutline: z.string(), panelTop: z.string(),
    panelBottom: z.string(), card: z.string(), cardBorder: z.string(), text: z.string(), muted: z.string(), accent: z.string(),
    tiers: z.record(z.string(), z.string()) }),
  captions: z.object({ uppercase: z.boolean(), fontSizeMax: z.number(), fontSizeMin: z.number(), maxWordsPerPhrase: z.number().int(),
    minWordsPerPhrase: z.number().int(), maxLines: z.number().int().min(1).max(2), maxPhraseSeconds: z.number(), minPhraseSeconds: z.number(),
    pauseBreakSeconds: z.number(), strokePx: z.number(), highlight: z.enum(["active", "emphasis", "active+emphasis"]), entranceFrames: z.number().int() }),
  safeArea: z.object({ x0: z.number(), x1: z.number(), y0: z.number(), y1: z.number() }),
  motion: z.object({ intensity: z.enum(["light", "medium", "high"]), levels: z.object({ light: level, medium: level, high: level }) }),
  layout: z.object({ explainerPanelHeight: z.number(), rankingSpeakerHeight: z.number() }),
  // Share of the source width shown across a full-screen speaker shot. null = fill the frame (tightest crop).
  // A smaller share backs the camera out; the clip then sits at the bottom with matched wall above it.
  framing: z.object({ fullWidthFraction: z.number().min(0.2).max(1).nullable() }).default({ fullWidthFraction: null }),
  // pinned: the opening-sentence title stays at the top for the whole video (captions carry the opening words).
  hook: z.object({ pinned: z.boolean() }).default({ pinned: false }),
  // mode: used when --mode is auto (null = choose from the speech). speechGraphics: cards/counters planned from
  // what he says (off in the saved style, where illustrations come from the finishing pass instead).
  editor: z.object({ mode: z.enum(["TALKING_HEAD", "EXPLAINER", "RANKING"]).nullable(), speechGraphics: z.boolean() })
    .default({ mode: null, speechGraphics: true }),
  // Music used when --music isn't given: "original" composes a bed for the video, null means none.
  music: z.object({ default: z.string().nullable() }).default({ default: null }),
  edit: z.object({ maxPauseSeconds: z.number(), keepPauseSeconds: z.number(), headPadSeconds: z.number(), tailPadSeconds: z.number(),
    silenceDb: z.number(), removeRestarts: z.boolean(), removeFillers: z.boolean() }),
  audio: z.object({ targetLufs: z.number(), truePeakDb: z.number(), lra: z.number(), highpassHz: z.number(), denoise: z.enum(["off", "light"]),
    musicUnderVoiceDb: z.number(), fadeMs: z.number() }),
  transcription: z.object({
    provider: z.enum(["local-faster-whisper", "openai"]),
    local: z.object({ modelDir: z.string(), threads: z.number().int() }),
    openai: z.object({ model: z.string(), apiKeyEnv: z.string(), enabled: z.boolean() }),
    language: z.string(),
    vocabulary: z.array(z.string()),
    uncertainBelow: z.number(),
  }),
});
export type HouseStyle = z.infer<typeof houseStyleSchema>;

export function loadStyle(file = rel("config/house-style.json")): HouseStyle {
  return houseStyleSchema.parse(readJson(file));
}
