import React from "react";
import {
  AbsoluteFill,
  CalculateMetadataFunction,
  Easing,
  Freeze,
  interpolate,
  OffthreadVideo,
  random,
  Series,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { EFFECTS, EffectId, effectStartFrom } from "../effects";
import { UI_FONT } from "../fonts";
import { AUDIT, FRAME_CENTER_X, SOURCE_CLIP } from "../settings";

export type ChatRenderProps = {
  effect: EffectId;
  // Leave empty to use the effect's own command and description.
  command?: string;
  description?: string;
};

export const chatRenderDefaults: ChatRenderProps = { effect: "GlassGraph" };

const ORANGE = "#D97757";
const BG = "#121214";
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// Layout (all inside x = 120 to 960).
const LEFT = 120;
const RIGHT = 960;
const BOX = { top: 1110, height: 290 };
const THUMB = { w: 96, h: 128 };
const SENT_THUMB = { w: 150, h: 200, top: 300 };
const TILE = { left: 120, top: 650, w: 240, h: 427 };
const KEY = { w: 74, h: 92, gap: 10, rowGap: 14, top: 1460 };

// Typing and send timing for a command.
export const timeline = (command: string) => {
  const slashAt = 6;
  const rest = command.replace(/^\//, "");
  const perChar = rest.length > 12 ? 1 : 2;
  const charAt = [slashAt, ...rest.split("").map((_, i) => slashAt + 6 + i * perChar)];
  const typedEnd = charAt[charAt.length - 1];
  const send = typedEnd + 6;
  return { charAt, send, length: send + 37 };
};

const sizeAt = (frame: number, a: number, b: number) =>
  interpolate(frame, [a, b], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });

// ---- Icons (drawn here, not taken from any app) ----

const MenuIcon = () => (
  <svg width={46} height={36} viewBox="0 0 46 36">
    {[4, 18, 32].map((y) => (
      <rect key={y} x={0} y={y - 2.5} width={y === 18 ? 32 : 46} height={5} rx={2.5} fill="#E8E8EC" />
    ))}
  </svg>
);

const ComposeIcon = () => (
  <svg width={46} height={46} viewBox="0 0 46 46" fill="none" stroke="#E8E8EC" strokeWidth={4} strokeLinecap="round">
    <path d="M22 6 H10 a5 5 0 0 0 -5 5 V36 a5 5 0 0 0 5 5 H35 a5 5 0 0 0 5 -5 V24" />
    <path d="M36 5 l5 5 L23 28 l-7 2 l2 -7 Z" strokeLinejoin="round" />
  </svg>
);

const MicIcon = () => (
  <svg width={40} height={46} viewBox="0 0 40 46" fill="none" stroke="#C9C9D0" strokeWidth={4} strokeLinecap="round">
    <rect x={12} y={3} width={16} height={26} rx={8} />
    <path d="M5 22 a15 15 0 0 0 30 0 M20 37 V43" />
  </svg>
);

const SendIcon = () => (
  <svg width={28} height={28} viewBox="0 0 28 28" fill="none" stroke="white" strokeWidth={4} strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 23 V6 M6 13 L14 5 L22 13" />
  </svg>
);

const Star: React.FC<{ frame: number; size?: number }> = ({ frame, size = 30 }) => (
  <svg width={size} height={size} viewBox="-15 -15 30 30" style={{ transform: `rotate(${frame * 14}deg)` }}>
    {[0, 45, 90, 135].map((a) => (
      <line
        key={a}
        x1={0}
        y1={-12}
        x2={0}
        y2={12}
        stroke={ORANGE}
        strokeWidth={a % 90 === 0 ? 4.5 : 3}
        strokeLinecap="round"
        transform={`rotate(${a})`}
      />
    ))}
  </svg>
);

// ---- Pieces ----

const ClipThumb: React.FC<{ effect: EffectId; style: React.CSSProperties; showClose: boolean }> = ({
  effect,
  style,
  showClose,
}) => (
  <div style={{ position: "absolute", borderRadius: 16, overflow: "visible", ...style }}>
    <div style={{ width: "100%", height: "100%", borderRadius: 16, overflow: "hidden", backgroundColor: "#333" }}>
      <Freeze frame={0}>
        <OffthreadVideo
          src={staticFile(SOURCE_CLIP)}
          startFrom={effectStartFrom(effect)}
          muted
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: `${FRAME_CENTER_X * 100}% 30%`,
          }}
        />
      </Freeze>
    </div>
    {showClose ? (
      <div
        style={{
          position: "absolute",
          top: -10,
          right: -10,
          width: 32,
          height: 32,
          borderRadius: 16,
          backgroundColor: "#0E0E10",
          border: "2px solid #4A4A50",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <svg width={12} height={12} viewBox="0 0 12 12" stroke="white" strokeWidth={2.2} strokeLinecap="round">
          <path d="M1 1 L11 11 M11 1 L1 11" />
        </svg>
      </div>
    ) : null}
  </div>
);

const ROWS: string[][] = [
  "qwertyuiop".split(""),
  "asdfghjkl".split(""),
  ["shift", ..."zxcvbnm".split(""), "back"],
  ["123", "/", "space", "-", "return"],
];

const keyWidth = (k: string) => {
  if (k === "space") return KEY.w * 4 + KEY.gap * 3;
  if (k === "return") return KEY.w * 2 + KEY.gap;
  if (k === "123") return KEY.w * 2 + KEY.gap;
  if (k === "shift" || k === "back") return KEY.w * 1.5 - KEY.gap / 2 + 2;
  return KEY.w;
};

const Keyboard: React.FC<{ lit: Record<string, number> }> = ({ lit }) => (
  <div
    style={{
      position: "absolute",
      left: 0,
      right: 0,
      top: KEY.top - 30,
      bottom: 0,
      backgroundColor: AUDIT ? undefined : "#1B1B1E",
    }}
  >
    {ROWS.map((row, r) => {
      const total = row.reduce((s, k) => s + keyWidth(k), 0) + KEY.gap * (row.length - 1);
      let x = LEFT + (RIGHT - LEFT - total) / 2;
      return row.map((k) => {
        const w = keyWidth(k);
        const left = x;
        x += w + KEY.gap;
        const glow = lit[k] ?? 0;
        const special = k.length > 1;
        return (
          <div
            key={`${r}-${k}`}
            style={{
              position: "absolute",
              left,
              top: 30 + r * (KEY.h + KEY.rowGap),
              width: w,
              height: KEY.h,
              borderRadius: 14,
              backgroundColor: glow ? ORANGE : special ? "#2A2A2F" : "#3A3A40",
              boxShadow: glow ? `0 0 ${24 * glow}px rgba(217,119,87,${0.8 * glow})` : "0 2px 0 #0D0D0F",
              transform: `scale(${1 + 0.12 * glow})`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontFamily: UI_FONT,
              fontSize: special ? 24 : 36,
              fontWeight: 500,
            }}
          >
            {k === "space" ? "" : k === "shift" ? "⇧" : k === "back" ? "⌫" : k}
          </div>
        );
      });
    })}
  </div>
);

// A dark tile of tiny dots that light up and open to show the effect's first frame.
const DOT_STEP = 3;
const DOT_COLS = 30;
const DOT_ROWS = 53;
const DOTS = Array.from({ length: DOT_COLS * DOT_ROWS }, (_, i) => ({
  x: DOT_STEP / 2 + (i % DOT_COLS) * DOT_STEP,
  y: DOT_STEP / 2 + Math.floor(i / DOT_COLS) * DOT_STEP,
  order: random(`dot-${i}`),
}));

const RenderTile: React.FC<{ effect: EffectId; send: number; end: number }> = ({ effect, send, end }) => {
  const frame = useCurrentFrame();
  const appear = interpolate(frame, [send + 11, send + 15], [0, 1], clamp);
  const lightUp = interpolate(frame, [send + 12, send + 20], [0, 1], clamp);
  const resolve = interpolate(frame, [send + 16, send + 25], [0, 1], { ...clamp, easing: Easing.in(Easing.quad) });
  // Fills the screen on the intro's last frame, which matches the effect's first frame.
  const grow = sizeAt(frame, send + 26, end - 1);

  const left = TILE.left * (1 - grow);
  const top = TILE.top * (1 - grow);
  const w = TILE.w + (1080 - TILE.w) * grow;
  const h = TILE.h + (1920 - TILE.h) * grow;
  const { component: Effect, props } = EFFECTS[effect];
  // Once it grows, the tile becomes the full-screen effect, so the audit leaves it out.
  if (AUDIT && grow > 0) return null;

  return (
    <div
      style={{
        position: "absolute",
        left,
        top,
        width: w,
        height: h,
        borderRadius: 28 * (1 - grow),
        overflow: "hidden",
        opacity: appear,
        transform: `scale(${0.94 + 0.06 * appear})`,
        boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
        backgroundColor: "#0C0C0E",
      }}
    >
      {resolve > 0 ? (
        <div style={{ width: 1080, height: 1920, transform: `scale(${w / 1080})`, transformOrigin: "0 0" }}>
          <Freeze frame={0}>
            <Effect {...props} />
          </Freeze>
        </div>
      ) : null}
      {resolve < 1 ? (
        <svg
          viewBox={`0 0 ${DOT_COLS * DOT_STEP} ${DOT_ROWS * DOT_STEP}`}
          preserveAspectRatio="none"
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
        >
          <defs>
            <mask id="tile-holes">
              <rect width="100%" height="100%" fill="white" />
              {DOTS.map((d, i) => {
                const r = Math.max(0, Math.min(1, resolve * 1.7 - d.order * 0.7)) * 2.2;
                return r > 0 ? <circle key={i} cx={d.x} cy={d.y} r={r} fill="black" /> : null;
              })}
            </mask>
          </defs>
          <rect width="100%" height="100%" fill="#0C0C0E" mask="url(#tile-holes)" />
          {DOTS.map((d, i) => {
            const on = d.order < lightUp * 1.15;
            const fade = 1 - resolve;
            return (
              <circle
                key={i}
                cx={d.x}
                cy={d.y}
                r={on ? 0.55 : 0.4}
                fill={on ? (d.order < 0.15 ? ORANGE : "#F4EDE8") : "#34343A"}
                opacity={on ? fade : 0.9 * fade}
              />
            );
          })}
        </svg>
      ) : null}
    </div>
  );
};

// ---- The intro ----

export const ChatIntro: React.FC<Required<ChatRenderProps>> = ({ effect, command, description }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { charAt, send, length } = timeline(command);

  const typed = command.slice(0, charAt.filter((t) => frame >= t).length);
  const sent = frame >= send + 1;

  // Keys light as they're pressed and fade over a few frames.
  const lit: Record<string, number> = {};
  command.split("").forEach((ch, i) => {
    const age = frame - charAt[i];
    if (age >= 0 && age < 4) lit[ch] = Math.max(lit[ch] ?? 0, 1 - age / 4);
  });

  const card = spring({ frame: frame - (charAt[0] + 1), fps, config: { damping: 12, stiffness: 220, mass: 0.5 } });
  const cardOut = interpolate(frame, [send, send + 3], [1, 0], clamp);
  const sendPress = frame >= send && frame < send + 3 ? 0.88 : 1;

  // Thumbnail flies from the message box to the sent message.
  const fly = sizeAt(frame, send + 1, send + 9);
  const from = { left: LEFT + 24, top: BOX.top + 22, w: THUMB.w, h: THUMB.h };
  const to = { left: RIGHT - SENT_THUMB.w, top: SENT_THUMB.top, w: SENT_THUMB.w, h: SENT_THUMB.h };
  const thumb = {
    left: from.left + (to.left - from.left) * fly,
    top: from.top + (to.top - from.top) * fly,
    width: from.w + (to.w - from.w) * fly,
    height: from.h + (to.h - from.h) * fly,
  };
  const pill = spring({ frame: frame - (send + 7), fps, config: { damping: 14, stiffness: 200, mass: 0.5 } });
  const editing = interpolate(frame, [send + 9, send + 12], [0, 1], clamp);

  return (
    <AbsoluteFill style={{ backgroundColor: AUDIT ? undefined : BG, fontFamily: UI_FONT }}>
      {/* Header */}
      <div style={{ position: "absolute", left: LEFT + 10, top: 228 }}>
        <MenuIcon />
      </div>
      <div style={{ position: "absolute", right: 1080 - RIGHT + 6, top: 222 }}>
        <ComposeIcon />
      </div>

      {/* Sent message */}
      {sent ? (
        <>
          <div
            style={{
              position: "absolute",
              right: 1080 - RIGHT,
              top: SENT_THUMB.top + SENT_THUMB.h + 18,
              padding: "12px 26px",
              borderRadius: 999,
              backgroundColor: ORANGE,
              color: "white",
              fontSize: 28,
              fontWeight: 700,
              opacity: Math.min(1, pill * 1.5),
              transform: `scale(${0.8 + 0.2 * pill})`,
              transformOrigin: "100% 0",
            }}
          >
            {command}
          </div>
          <div
            style={{
              position: "absolute",
              left: LEFT,
              top: SENT_THUMB.top + SENT_THUMB.h + 96,
              display: "flex",
              alignItems: "center",
              gap: 16,
              color: "#9A9AA3",
              fontSize: 30,
              fontWeight: 500,
              opacity: editing,
            }}
          >
            <Star frame={frame} />
            <span>Editing with {command}...</span>
          </div>
        </>
      ) : null}

      {/* Slash command card */}
      {frame >= charAt[0] + 1 && cardOut > 0 ? (
        <div
          style={{
            position: "absolute",
            left: LEFT,
            top: BOX.top - 150,
            width: 640,
            boxSizing: "border-box",
            padding: "22px 28px",
            borderRadius: 24,
            backgroundColor: "#242428",
            border: "1px solid #3A3A40",
            boxShadow: "0 16px 40px rgba(0,0,0,0.45)",
            opacity: Math.min(1, card * 1.5) * cardOut,
            transform: `translateY(${(1 - card) * 16}px) scale(${0.92 + 0.08 * card})`,
            transformOrigin: "0 100%",
          }}
        >
          <div style={{ color: "white", fontSize: 32, fontWeight: 700 }}>{command}</div>
          <div style={{ color: "#A2A2AA", fontSize: 25, fontWeight: 500, marginTop: 6, whiteSpace: "nowrap" }}>
            {description}
          </div>
        </div>
      ) : null}

      {/* Message box */}
      <div
        style={{
          position: "absolute",
          left: LEFT,
          top: BOX.top,
          width: RIGHT - LEFT,
          height: BOX.height,
          borderRadius: 36,
          backgroundColor: "#232327",
          border: "1px solid #34343A",
        }}
      >
        <div style={{ position: "absolute", left: 28, top: 168, fontSize: 34, fontWeight: 500 }}>
          {typed && !sent ? (
            <span style={{ color: "white" }}>
              {typed}
              <span style={{ color: ORANGE, opacity: frame % 16 < 9 ? 1 : 0 }}>|</span>
            </span>
          ) : (
            <span style={{ color: "#7C7C84" }}>Reply...</span>
          )}
        </div>
        <div
          style={{
            position: "absolute",
            left: 24,
            bottom: 18,
            width: 54,
            height: 54,
            borderRadius: 27,
            border: "3px solid #5A5A62",
            boxSizing: "border-box",
            color: "#C9C9D0",
            fontSize: 38,
            lineHeight: "44px",
            textAlign: "center",
          }}
        >
          +
        </div>
        <div style={{ position: "absolute", right: 104, bottom: 22 }}>
          <MicIcon />
        </div>
        <div
          style={{
            position: "absolute",
            right: 22,
            bottom: 16,
            width: 64,
            height: 64,
            borderRadius: 32,
            backgroundColor: ORANGE,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transform: `scale(${sendPress})`,
          }}
        >
          <SendIcon />
        </div>
      </div>

      <Keyboard lit={lit} />

      <ClipThumb effect={effect} style={thumb} showClose={fly === 0} />

      <RenderTile effect={effect} send={send} end={length} />
    </AbsoluteFill>
  );
};

const resolveProps = (p: ChatRenderProps): Required<ChatRenderProps> => ({
  effect: p.effect,
  command: p.command || EFFECTS[p.effect].command,
  description: p.description || EFFECTS[p.effect].description,
});

export const introLength = (p: ChatRenderProps) => timeline(resolveProps(p).command).length;

// The intro, then a hard cut into the effect.
export const ChatRender: React.FC<ChatRenderProps> = (p) => {
  const props = resolveProps(p);
  const { component: Effect, props: effectProps, durationInFrames } = EFFECTS[props.effect];
  return (
    <Series>
      <Series.Sequence durationInFrames={introLength(props)}>
        <ChatIntro {...props} />
      </Series.Sequence>
      <Series.Sequence durationInFrames={durationInFrames}>
        <Effect {...effectProps} />
      </Series.Sequence>
    </Series>
  );
};

export const chatRenderMetadata: CalculateMetadataFunction<ChatRenderProps> = ({ props }) => ({
  durationInFrames: introLength(props) + EFFECTS[props.effect].durationInFrames,
});
