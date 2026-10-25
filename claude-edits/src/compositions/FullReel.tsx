import React from "react";
import {
  AbsoluteFill,
  Audio,
  CalculateMetadataFunction,
  Freeze,
  getStaticFiles,
  interpolate,
  Sequence,
  Series,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { fitText } from "@remotion/layout-utils";
import { EFFECTS, EFFECT_ORDER, EffectId } from "../effects";
import { DISPLAY_FONT } from "../fonts";
import { AUDIT, HEIGHT, SAFE_LEFT, SAFE_WIDTH, WIDTH } from "../settings";
import { ChatRender, introLength } from "./ChatRender";

export type FullReelProps = { callToAction: string };

export const fullReelDefaults: FullReelProps = {
  // Placeholder call to action: replace with yours.
  callToAction: "Comment CLAUDE",
};

const MUSIC = "music.mp3";
const END_FRAMES = 90;
const GRID = { cols: 3, gap: 16, top: 470 };
const TILE_W = (SAFE_WIDTH - GRID.gap * (GRID.cols - 1)) / GRID.cols;
const TILE_H = (TILE_W * HEIGHT) / WIDTH;

const sectionLength = (id: EffectId) => introLength({ effect: id }) + EFFECTS[id].durationInFrames;
const sectionsLength = () => EFFECT_ORDER.reduce((sum, id) => sum + sectionLength(id), 0);

// Plays an effect once, then holds its last frame.
const PlayOnce: React.FC<{ id: EffectId }> = ({ id }) => {
  const frame = useCurrentFrame();
  const { component: Effect, props, durationInFrames } = EFFECTS[id];
  const effect = <Effect {...props} />;
  return frame < durationInFrames ? effect : <Freeze frame={durationInFrames - 1}>{effect}</Freeze>;
};

// All six effects playing at once, with the call to action on top.
const EndGrid: React.FC<{ callToAction: string }> = ({ callToAction }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame: frame - 8, fps, config: { damping: 11, stiffness: 180, mass: 0.6 } });
  // Leaves room for the pill's padding and the pop's overshoot inside the safe zone.
  const { fontSize } = fitText({ text: callToAction, withinWidth: SAFE_WIDTH - 140, fontFamily: DISPLAY_FONT });
  return (
    <AbsoluteFill style={{ backgroundColor: AUDIT ? undefined : "#0E0E10" }}>
      {EFFECT_ORDER.map((id, i) => (
        <div
          key={id}
          style={{
            position: "absolute",
            left: SAFE_LEFT + (i % GRID.cols) * (TILE_W + GRID.gap),
            top: GRID.top + Math.floor(i / GRID.cols) * (TILE_H + GRID.gap),
            width: TILE_W,
            height: TILE_H,
            borderRadius: 18,
            overflow: "hidden",
          }}
        >
          <div style={{ width: WIDTH, height: HEIGHT, transform: `scale(${TILE_W / WIDTH})`, transformOrigin: "0 0" }}>
            <PlayOnce id={id} />
          </div>
        </div>
      ))}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div
          style={{
            maxWidth: SAFE_WIDTH,
            padding: "18px 30px 10px",
            borderRadius: 28,
            backgroundColor: "rgba(10, 10, 12, 0.82)",
            boxShadow: "0 20px 60px rgba(0,0,0,0.55)",
            fontFamily: DISPLAY_FONT,
            fontSize: Math.min(fontSize, 150),
            lineHeight: 1.1,
            color: "white",
            whiteSpace: "nowrap",
            opacity: Math.min(1, pop * 1.4),
            transform: `scale(${0.7 + 0.3 * pop})`,
          }}
        >
          {callToAction}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const FullReel: React.FC<FullReelProps> = ({ callToAction }) => {
  const { durationInFrames, fps } = useVideoConfig();
  const hasMusic = getStaticFiles().some((f) => f.name === MUSIC);
  return (
    <AbsoluteFill style={{ backgroundColor: AUDIT ? undefined : "black" }}>
      <Series>
        {EFFECT_ORDER.map((id) => (
          <Series.Sequence key={id} durationInFrames={sectionLength(id)}>
            <ChatRender effect={id} />
          </Series.Sequence>
        ))}
        <Series.Sequence durationInFrames={END_FRAMES}>
          <EndGrid callToAction={callToAction} />
        </Series.Sequence>
      </Series>
      {/* Music at normal speed; the talking clip is muted everywhere. Fades out over the last half second. */}
      {hasMusic ? (
        <Sequence>
          <Audio
            src={staticFile(MUSIC)}
            volume={(f) =>
              interpolate(f, [durationInFrames - fps / 2, durationInFrames - 1], [1, 0], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              })
            }
          />
        </Sequence>
      ) : null}
    </AbsoluteFill>
  );
};

export const fullReelMetadata: CalculateMetadataFunction<FullReelProps> = () => ({
  durationInFrames: sectionsLength() + END_FRAMES,
});
