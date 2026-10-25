import React from "react";
import {
  AbsoluteFill,
  Easing,
  getStaticFiles,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Footage } from "../Footage";
import { UI_FONT } from "../fonts";

export type Tier = "S" | "A" | "B" | "C" | "D";

export type TierListProps = {
  topic: string;
  tiers: Record<Tier, string[]>;
  startFrom?: number;
};

export const tierListDefaults: TierListProps = {
  // Placeholder topic and items: replace with yours.
  topic: "protein sources",
  tiers: {
    S: ["Chicken breast"],
    A: ["Eggs", "Greek yogurt", "Lean beef"],
    B: ["Tuna", "Whey"],
    C: ["Tofu", "Beans"],
    D: ["Bacon"],
  },
  startFrom: 1560,
};

const TIERS: Tier[] = ["S", "A", "B", "C", "D"];
const TIER_COLOR: Record<Tier, string> = {
  S: "#E5484D",
  A: "#F28C28",
  B: "#F5C518",
  C: "#3CB371",
  D: "#3B82F6",
};
const PANEL = { left: 140, width: 800, top: 1330 };
const ROW_H = 76;
const FIRST_DROP = 10;
const DROP_EVERY = 4;
const LAND_FRAMES = 8;
// Length of the effect, so its exit timing holds when it plays inside a longer sequence.
const TIER_LIST_FRAMES = 90;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// A logo in public/logos whose file name matches the item, e.g. "Greek yogurt" -> greek-yogurt.png.
const slug = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
const findLogo = (item: string) => {
  const files = getStaticFiles().map((f) => f.name);
  const wanted = [slug(item), item.toLowerCase()];
  return files.find((f) => {
    const m = f.match(/^logos\/(.+)\.(png|jpe?g|svg|webp)$/i);
    return m && wanted.includes(m[1].toLowerCase());
  });
};

const Item: React.FC<{ name: string; at: number }> = ({ name, at }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const drop = spring({ frame: frame - at, fps, config: { damping: 9, stiffness: 170, mass: 0.6 } });
  const opacity = interpolate(frame - at, [0, 3], [0, 1], clamp);
  const logo = findLogo(name);
  return (
    <div style={{ transform: `translateY(${(1 - drop) * -70}px)`, opacity }}>
      {logo ? (
        <Img
          src={staticFile(logo)}
          style={{ width: 62, height: 62, borderRadius: 14, objectFit: "cover", backgroundColor: "#fff" }}
        />
      ) : (
        <div
          style={{
            height: 58,
            padding: "0 20px",
            display: "flex",
            alignItems: "center",
            borderRadius: 14,
            backgroundColor: "#3B3B42",
            border: "1px solid rgba(255,255,255,0.08)",
            color: "white",
            fontSize: 26,
            fontWeight: 700,
            whiteSpace: "nowrap",
          }}
        >
          {name}
        </div>
      )}
    </div>
  );
};

const Spinner: React.FC<{ frame: number }> = ({ frame }) => (
  <svg width={26} height={26} viewBox="0 0 26 26" style={{ transform: `rotate(${frame * 18}deg)` }}>
    <circle cx={13} cy={13} r={10} fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth={3.5} />
    <path d="M13 3 A10 10 0 0 1 23 13" fill="none" stroke="white" strokeWidth={3.5} strokeLinecap="round" />
  </svg>
);

const Tick: React.FC = () => (
  <svg width={26} height={26} viewBox="0 0 26 26">
    <circle cx={13} cy={13} r={12} fill="#3CB371" />
    <path d="M7.5 13.5 L11.5 17.5 L19 9.5" fill="none" stroke="white" strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const StatusPill: React.FC<{ topic: string; doneAt: number }> = ({ topic, doneAt }) => {
  const frame = useCurrentFrame();
  // Old label fades out fully before the new one fades in, so they never overlap.
  const oldOpacity = interpolate(frame, [doneAt, doneAt + 3], [1, 0], clamp);
  const newOpacity = interpolate(frame, [doneAt + 3, doneAt + 7], [0, 1], clamp);
  const label = (children: React.ReactNode, opacity: number) =>
    opacity > 0 ? (
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", gap: 12, opacity }}>
        {children}
      </div>
    ) : null;
  return (
    <div
      style={{
        position: "relative",
        height: 50,
        width: 420,
        padding: "0 22px",
        borderRadius: 999,
        backgroundColor: "rgba(255,255,255,0.08)",
        color: "#E6E6EC",
        fontSize: 24,
        fontWeight: 500,
      }}
    >
      <div style={{ position: "absolute", left: 22, right: 22, top: 0, bottom: 0 }}>
        {label(
          <>
            <Spinner frame={frame} />
            <span style={{ whiteSpace: "nowrap" }}>Ranking {topic}...</span>
          </>,
          oldOpacity,
        )}
        {label(
          <>
            <Tick />
            <span>Ranked</span>
          </>,
          newOpacity,
        )}
      </div>
    </div>
  );
};

export const TierList: React.FC<TierListProps> = ({ topic, tiers, startFrom = tierListDefaults.startFrom! }) => {
  const frame = useCurrentFrame();

  // Drop order: top tier first, left to right.
  let n = 0;
  const dropAt: Record<string, number> = {};
  for (const t of TIERS) {
    tiers[t].forEach((item, i) => {
      dropAt[`${t}-${i}`] = FIRST_DROP + DROP_EVERY * n++;
    });
  }
  const lastLand = FIRST_DROP + DROP_EVERY * Math.max(0, n - 1) + LAND_FRAMES;

  const enter = interpolate(frame, [0, 8], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const exit = interpolate(frame, [TIER_LIST_FRAMES - 10, TIER_LIST_FRAMES], [0, 1], clamp);

  return (
    <AbsoluteFill>
      <Footage framing={{ startFrom, centerX: 0.578 }} />
      <div
        style={{
          position: "absolute",
          left: PANEL.left,
          top: PANEL.top,
          width: PANEL.width,
          boxSizing: "border-box",
          padding: 22,
          borderRadius: 32,
          backgroundColor: "rgba(16, 16, 20, 0.92)",
          boxShadow: "0 24px 60px rgba(0,0,0,0.4)",
          fontFamily: UI_FONT,
          opacity: enter * (1 - exit),
          transform: `translateY(${(1 - enter) * 60}px)`,
        }}
      >
        <div style={{ marginBottom: 14 }}>
          <StatusPill topic={topic} doneAt={lastLand} />
        </div>
        {TIERS.map((t) => (
          <div
            key={t}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 14,
              height: ROW_H,
              marginTop: 8,
              padding: "0 12px 0 0",
              borderRadius: 16,
              backgroundColor: "#26262B",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: ROW_H,
                height: ROW_H,
                flexShrink: 0,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: TIER_COLOR[t],
                color: "#141418",
                fontSize: 40,
                fontWeight: 700,
              }}
            >
              {t}
            </div>
            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              {tiers[t].map((item, i) =>
                frame >= dropAt[`${t}-${i}`] ? <Item key={item} name={item} at={dropAt[`${t}-${i}`]} /> : null,
              )}
            </div>
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
