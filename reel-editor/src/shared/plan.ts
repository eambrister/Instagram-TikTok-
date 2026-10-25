// Scene plan schema shared by the pipeline (validation) and the Remotion composition (rendering).
// All times are seconds on the OUTPUT timeline unless a field says src*.
import { z } from "zod";

export const TIERS = ["S", "A", "B", "C", "D", "F"] as const;
export type Tier = (typeof TIERS)[number];
export const MODES = ["TALKING_HEAD", "EXPLAINER", "RANKING"] as const;
export type Mode = (typeof MODES)[number];
export const INTENSITIES = ["light", "medium", "high"] as const;

const time = z.number().finite().nonnegative();
const rect = z.object({ x: z.number(), y: z.number(), w: z.number().positive(), h: z.number().positive() });
export type Rect = z.infer<typeof rect>;

export const segmentSchema = z.object({
  srcStart: time,
  srcEnd: time,
  outStart: time,
  outEnd: time,
  // Face centre in proxy-normalised coordinates (0..1) for framing; null = no confident face.
  focus: z.object({ cx: z.number(), cy: z.number(), w: z.number() }).nullable(),
});
export type Segment = z.infer<typeof segmentSchema>;

export const layoutSchema = z.object({
  start: time,
  end: time,
  kind: z.enum(["full", "panel-top", "board-bottom"]),
});
export type LayoutSpan = z.infer<typeof layoutSchema>;

export const zoomSchema = z.object({
  at: time,
  scale: z.number().min(1).max(1.3),
  frames: z.number().int().min(0).max(30), // 0 = hard punch-in on a cut
  reason: z.string(),
});
export type ZoomKey = z.infer<typeof zoomSchema>;

export const captionWordSchema = z.object({
  text: z.string().min(1),
  start: time,
  end: time,
  emphasis: z.boolean(),
  uncertain: z.boolean(),
});
export const captionSchema = z.object({
  id: z.string(),
  start: time,
  end: time,
  words: z.array(captionWordSchema).min(1),
  lines: z.array(z.array(z.number().int().nonnegative())).min(1).max(2),
  fontSize: z.number().min(30).max(110),
  box: rect, // measured bounding box, output pixels
  suppressed: z.boolean(), // true while the hook title already shows these exact words (still exported to SRT)
});
export type Caption = z.infer<typeof captionSchema>;

const sourceRef = z.object({
  kind: z.enum(["speech", "instruction", "supplied-source"]),
  quote: z.string(),
  at: time.optional(),
  confidence: z.number().min(0).max(1).optional(),
});

export const graphicSchema = z.discriminatedUnion("kind", [
  z.object({ kind: z.literal("hook"), id: z.string(), start: time, end: time, region: rect,
    data: z.object({ kicker: z.string().nullable(), title: z.string(), highlight: z.array(z.number().int()), times: z.array(z.number()) }), source: sourceRef }),
  z.object({ kind: z.literal("card"), id: z.string(), start: time, end: time, region: rect,
    data: z.object({ label: z.string().nullable(), text: z.string(), icon: z.string().nullable(), tilt: z.number() }), source: sourceRef }),
  z.object({ kind: z.literal("counter"), id: z.string(), start: time, end: time, region: rect,
    data: z.object({ value: z.number(), decimals: z.number().int().min(0).max(2), unit: z.string(), caption: z.string(), estimate: z.boolean() }), source: sourceRef }),
  z.object({ kind: z.literal("comparison"), id: z.string(), start: time, end: time, region: rect,
    data: z.object({ left: z.string(), right: z.string(), joiner: z.string() }), source: sourceRef }),
  z.object({ kind: z.literal("object"), id: z.string(), start: time, end: time, region: rect,
    data: z.object({ label: z.string(), image: z.string().nullable() }), source: sourceRef }),
]);
export type Graphic = z.infer<typeof graphicSchema>;

export const tierEventSchema = z.object({
  id: z.string(),
  item: z.string().min(1),
  tier: z.enum(TIERS),
  introAt: time, // item appears large
  placeAt: time, // item flies into its row
  image: z.string().nullable(),
  source: sourceRef,
});
export type TierEvent = z.infer<typeof tierEventSchema>;

export const fontsSchema = z.object({
  heading: z.object({ url: z.string(), family: z.string(), source: z.string() }),
  caption: z.object({ url: z.string(), family: z.string(), source: z.string() }),
  body: z.object({ url: z.string(), family: z.string(), source: z.string() }),
});

export const scenePlanSchema = z.object({
  version: z.literal(1),
  jobId: z.string(),
  mode: z.enum(MODES),
  modeReason: z.string(),
  intensity: z.enum(INTENSITIES),
  fps: z.number().int().positive(),
  width: z.number().int().positive(),
  height: z.number().int().positive(),
  duration: z.number().positive(),
  preview: z.object({ start: time, end: time }).nullable(),
  source: z.object({ url: z.string(), width: z.number(), height: z.number(), fps: z.number(), maxZoom: z.number() }),
  segments: z.array(segmentSchema).min(1),
  layout: z.array(layoutSchema).min(1),
  zooms: z.array(zoomSchema),
  captions: z.array(captionSchema),
  graphics: z.array(graphicSchema),
  tierBoard: z.object({ title: z.string().nullable(), events: z.array(tierEventSchema) }).nullable(),
  style: z.object({
    colors: z.record(z.string(), z.any()),
    captionStrokePx: z.number(),
    captionHighlight: z.string(),
    entranceFrames: z.number().int(),
    captionEntranceFrames: z.number().int(),
    panelHeight: z.number(),
    boardSpeakerHeight: z.number(),
    safeArea: z.object({ x0: z.number(), x1: z.number(), y0: z.number(), y1: z.number() }),
  }),
  fonts: fontsSchema,
  assets: z.array(z.object({ path: z.string(), kind: z.string(), license: z.string() })),
  notes: z.array(z.string()),
});
export type ScenePlan = z.infer<typeof scenePlanSchema>;
