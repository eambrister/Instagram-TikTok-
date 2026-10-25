import React from "react";
import { ColorGrade, colorGradeDefaults } from "./compositions/ColorGrade";
import { FreezeFrame, freezeFrameDefaults } from "./compositions/FreezeFrame";
import { GlassGraph, glassGraphDefaults } from "./compositions/GlassGraph";
import { OverTheShoulder, overTheShoulderDefaults } from "./compositions/OverTheShoulder";
import { TextBehind, textBehindDefaults } from "./compositions/TextBehind";
import { TierList, tierListDefaults } from "./compositions/TierList";

export type EffectId = "OverTheShoulder" | "GlassGraph" | "FreezeFrame" | "TierList" | "TextBehind" | "ColorGrade";

type Effect = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  component: React.FC<any>;
  props: object;
  durationInFrames: number;
  command: string;
  description: string;
};

// Every effect, with the command and description its ChatRender intro shows.
export const EFFECTS: Record<EffectId, Effect> = {
  OverTheShoulder: {
    component: OverTheShoulder,
    props: overTheShoulderDefaults,
    durationInFrames: 84,
    command: "/over-the-shoulder",
    description: "Proof cards behind you, over each shoulder",
  },
  GlassGraph: {
    component: GlassGraph,
    props: glassGraphDefaults,
    durationInFrames: 90,
    command: "/glass-graph",
    description: "A glass card with a graph that climbs",
  },
  FreezeFrame: {
    component: FreezeFrame,
    props: freezeFrameDefaults,
    durationInFrames: 90,
    command: "/freeze-frame",
    description: "Freeze, cut yourself out as a sticker, add a name tag",
  },
  TierList: {
    component: TierList,
    props: tierListDefaults,
    durationInFrames: 90,
    command: "/tier-list",
    description: "Rank anything, row by row",
  },
  TextBehind: {
    component: TextBehind,
    props: textBehindDefaults,
    durationInFrames: 90,
    command: "/text-behind",
    description: "A huge word that sits behind your head",
  },
  ColorGrade: {
    component: ColorGrade,
    props: colorGradeDefaults,
    durationInFrames: 90,
    command: "/color-grade",
    description: "From flat LOG to a cinematic grade",
  },
};

export const EFFECT_ORDER: EffectId[] = [
  "OverTheShoulder",
  "GlassGraph",
  "FreezeFrame",
  "TierList",
  "TextBehind",
  "ColorGrade",
];

// The framing section each effect uses, for thumbnails.
export const effectStartFrom = (id: EffectId) => (EFFECTS[id].props as { startFrom?: number }).startFrom ?? 0;
