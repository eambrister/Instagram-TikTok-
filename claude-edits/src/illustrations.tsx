// Line-art illustrations for reels, drawn in a 200 x 200 box: white strokes with a yellow accent.
// Each takes `t`, frames since it appeared, and animates from there.
import React from "react";
import { Easing, interpolate } from "remotion";

export const INK = "#FFFFFF";
export const ACCENT = "#FFD84D";
export const MUTED = "#8E939E";
const SW = 9; // stroke width
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.inOut(Easing.cubic);

const line = { fill: "none", stroke: INK, strokeWidth: SW, strokeLinecap: "round", strokeLinejoin: "round" } as const;
const accentLine = { ...line, stroke: ACCENT };

// Draws a path on over `frames`, starting at `at`.
const draw = (t: number, at: number, frames: number, length: number) => ({
  strokeDasharray: length,
  strokeDashoffset: interpolate(t, [at, at + frames], [length, 0], { ...clamp, easing: ease }),
});

const Svg: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <svg viewBox="0 0 200 200" width="100%" height="100%" style={{ overflow: "visible" }}>
    {children}
  </svg>
);

// "Keeping your word to yourself": a speech bubble that gets a check.
export const PromiseKept: React.FC<{ t: number }> = ({ t }) => (
  <Svg>
    <path d="M40 40 H160 a16 16 0 0 1 16 16 V120 a16 16 0 0 1 -16 16 H92 L58 166 V136 H40 a16 16 0 0 1 -16 -16 V56 a16 16 0 0 1 16 -16 Z" {...line} />
    <path d="M66 90 L90 112 L136 64" {...accentLine} strokeWidth={13} style={draw(t, 8, 12, 110)} />
  </Svg>
);

const MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV"];

// "Start in January ... but it's almost November": the page flips from JAN through to NOV.
export const CalendarFlip: React.FC<{ t: number; flipAt: number; flipFrames: number }> = ({ t, flipAt, flipFrames }) => {
  const p = interpolate(t, [flipAt, flipAt + flipFrames], [0, MONTHS.length - 1], { ...clamp, easing: Easing.in(Easing.quad) });
  const i = Math.floor(p);
  const turn = p - i; // current page lifting away
  const circled = interpolate(t, [45, 57], [0, 1], clamp) * (i === 0 ? 1 : 0);
  return (
    <Svg>
      <rect x={30} y={40} width={140} height={140} rx={18} {...line} />
      <path d="M30 78 H170" {...line} />
      <rect x={30} y={40} width={140} height={38} rx={14} fill={ACCENT} />
      <path d="M66 26 V54 M134 26 V54" {...line} />
      <g style={{ transformOrigin: "100px 78px", transform: `rotateX(${turn * 90}deg)` }}>
        <text x={100} y={150} textAnchor="middle" fill={i === MONTHS.length - 1 ? ACCENT : INK} fontSize={56}
          fontFamily="Barlow Condensed" fontWeight={800}>
          {MONTHS[i]}
        </text>
      </g>
      {circled > 0 ? (
        <ellipse cx={100} cy={131} rx={58} ry={34} {...accentLine} strokeWidth={6} style={draw(circled * 20, 0, 20, 300)} />
      ) : null}
    </Svg>
  );
};

// "Up early training": an alarm clock ringing in front of a rising sun.
export const AlarmClock: React.FC<{ t: number }> = ({ t }) => {
  const sun = interpolate(t, [0, 24], [40, 0], { ...clamp, easing: Easing.out(Easing.cubic) });
  const shake = t < 30 ? Math.sin(t * 2.2) * 6 : 0;
  const hand = interpolate(t, [0, 20], [-300, 0], { ...clamp, easing: Easing.out(Easing.cubic) });
  return (
    <Svg>
      <clipPath id="sun-clip">
        <rect x={0} y={0} width={200} height={150} />
      </clipPath>
      <circle cx={100} cy={150 + sun} r={70} fill={ACCENT} opacity={0.35} clipPath="url(#sun-clip)" />
      <g style={{ transformOrigin: "100px 110px", transform: `rotate(${shake}deg)` }}>
        <circle cx={100} cy={110} r={56} {...line} />
        <path d="M56 58 a22 22 0 0 1 30 -10 M144 58 a22 22 0 0 0 -30 -10" {...accentLine} />
        <path d="M72 162 L62 178 M128 162 L138 178" {...line} />
        <path d="M100 110 V80" {...line} style={{ transformOrigin: "100px 110px", transform: `rotate(${hand}deg)` }} />
        <path d="M100 110 L120 122" {...line} />
      </g>
    </Svg>
  );
};

// "When everybody's sleeping": a moon with Zs drifting up.
export const MoonSleep: React.FC<{ t: number }> = ({ t }) => (
  <Svg>
    <path d="M118 40 a64 64 0 1 0 50 98 a52 52 0 1 1 -50 -98 Z" {...line} />
    {[0, 1, 2].map((k) => {
      const cycle = ((t + k * 14) % 42) / 42;
      return (
        <text key={k} x={128 + cycle * 30} y={86 - cycle * 60} fill={ACCENT} fontSize={26 + k * 8} fontFamily="Barlow Condensed"
          fontWeight={800} opacity={interpolate(cycle, [0, 0.2, 0.8, 1], [0, 1, 1, 0])}>
          Z
        </text>
      );
    })}
  </Svg>
);

// "If you're tracking your food": a log that ticks off line by line.
export const FoodLog: React.FC<{ t: number }> = ({ t }) => (
  <Svg>
    <rect x={44} y={30} width={112} height={150} rx={14} {...line} />
    <rect x={76} y={20} width={48} height={22} rx={8} fill={INK} />
    {[70, 108, 146].map((y, k) => (
      <g key={y}>
        <path d={`M64 ${y} l10 10 l18 -20`} {...accentLine} strokeWidth={8} style={draw(t, 6 + k * 9, 8, 40)} />
        <path d={`M104 ${y} H138`} {...line} strokeWidth={7} opacity={0.75} />
      </g>
    ))}
  </Svg>
);

// "Everybody's eating whatever they want": a pizza slice.
export const PizzaSlice: React.FC<{ t: number }> = ({ t }) => {
  const wob = Math.sin(t / 5) * 4;
  return (
    <Svg>
      <g style={{ transformOrigin: "100px 100px", transform: `rotate(${wob}deg)` }}>
        <path d="M34 52 Q100 20 166 52 L100 176 Z" {...line} />
        <path d="M34 52 Q100 20 166 52" {...accentLine} strokeWidth={16} />
        {[
          [84, 78],
          [118, 88],
          [100, 120],
        ].map(([x, y]) => (
          <circle key={`${x}-${y}`} cx={x} cy={y} r={11} fill={ACCENT} />
        ))}
      </g>
    </Svg>
  );
};

// "Showing up when you don't feel like it": a low battery that charges up anyway.
export const BatteryLow: React.FC<{ t: number }> = ({ t }) => {
  const fill = interpolate(t, [24, 60], [0.14, 1], { ...clamp, easing: ease });
  const bolt = interpolate(t, [16, 24], [0, 1], clamp);
  return (
    <Svg>
      <rect x={24} y={64} width={140} height={76} rx={14} {...line} />
      <rect x={168} y={88} width={12} height={28} rx={4} fill={INK} />
      <rect x={38} y={78} width={112 * fill} height={48} rx={6} fill={fill > 0.9 ? ACCENT : INK} opacity={0.9} />
      <path d="M104 48 L80 104 H104 L94 156 L126 94 H102 Z" fill={ACCENT} stroke="#111" strokeWidth={4} strokeLinejoin="round"
        opacity={bolt} style={{ transformOrigin: "100px 100px", transform: `scale(${0.6 + 0.4 * bolt})` }} />
    </Svg>
  );
};

// "You are not normal": a row of grey figures with one standing out in yellow.
export const StandOut: React.FC<{ t: number }> = ({ t }) => {
  const lift = interpolate(t, [10, 22], [0, 1], { ...clamp, easing: Easing.out(Easing.back(2)) });
  const person = (x: number, color: string, dy: number, k: number) => (
    <g key={k} transform={`translate(${x} ${dy})`}>
      <circle cx={0} cy={96} r={13} fill={color} />
      <path d="M-18 150 Q0 112 18 150 Z" fill={color} />
    </g>
  );
  return (
    <Svg>
      {[22, 58, 142, 178].map((x, k) => person(x, MUTED, 10, k))}
      {person(100, ACCENT, 10 - 22 * lift, 9)}
      <path d="M8 172 H192" {...line} strokeWidth={5} opacity={0.6} />
    </Svg>
  );
};

// "You are rare": a diamond with sparkles.
export const Diamond: React.FC<{ t: number }> = ({ t }) => (
  <Svg>
    <path d="M58 56 H142 L176 92 L100 176 L24 92 Z" {...line} style={draw(t, 0, 14, 470)} />
    <path d="M24 92 H176 M80 56 L100 92 L120 56 M100 92 V176" {...line} strokeWidth={6} opacity={0.8} style={draw(t, 8, 12, 300)} />
    {[
      [160, 40, 0],
      [36, 46, 10],
      [170, 140, 20],
    ].map(([x, y, d]) => {
      const s = interpolate(Math.sin((t - d) / 4), [-1, 1], [0.3, 1]) * interpolate(t, [10, 18], [0, 1], clamp);
      return (
        <path key={`${x}-${y}`} d={`M${x} ${y - 14} L${x + 4} ${y - 4} L${x + 14} ${y} L${x + 4} ${y + 4} L${x} ${y + 14} L${x - 4} ${y + 4} L${x - 14} ${y} L${x - 4} ${y - 4} Z`}
          fill={ACCENT} style={{ transformOrigin: `${x}px ${y}px`, transform: `scale(${s})` }} />
      );
    })}
  </Svg>
);

// "Starting over every Monday": a loop arrow going round MON.
export const MondayLoop: React.FC<{ t: number }> = ({ t }) => (
  <Svg>
    <g style={{ transformOrigin: "100px 100px", transform: `rotate(${t * 9}deg)` }}>
      <path d="M100 30 a70 70 0 1 1 -66 47" {...accentLine} strokeWidth={11} />
      <path d="M22 56 L34 79 L58 70" {...accentLine} strokeWidth={11} />
    </g>
    <text x={100} y={118} textAnchor="middle" fill={INK} fontSize={52} fontFamily="Barlow Condensed" fontWeight={800}>
      MON
    </text>
  </Svg>
);

// "I'll do it tomorrow": a note that keeps getting pushed along.
export const Tomorrow: React.FC<{ t: number }> = ({ t }) => {
  const cycle = (t % 30) / 30;
  const x = interpolate(cycle, [0, 0.5, 0.7, 1], [0, 0, 60, 60], { easing: ease });
  const o = interpolate(cycle, [0, 0.08, 0.6, 0.72], [0, 1, 1, 0]);
  return (
    <Svg>
      <g transform={`translate(${x - 30} 0)`} opacity={o}>
        <rect x={40} y={56} width={110} height={92} rx={10} fill={ACCENT} transform="rotate(-6 95 102)" />
        <text x={95} y={112} textAnchor="middle" fill="#121214" fontSize={26} fontFamily="Barlow Condensed" fontWeight={800}
          transform="rotate(-6 95 102)">
          TOMORROW
        </text>
      </g>
      <path d="M40 176 H150 M132 160 L152 176 L132 192" {...line} strokeWidth={7} />
    </Svg>
  );
};

// "Stop trying to fit in": a square peg bouncing off a round hole.
export const SquarePeg: React.FC<{ t: number }> = ({ t }) => {
  const cycle = (t % 36) / 36;
  const y = interpolate(cycle, [0, 0.45, 0.55, 0.75, 1], [20, 86, 70, 80, 20], { easing: ease });
  const tilt = interpolate(cycle, [0.45, 0.55, 0.7], [0, -10, 0], clamp);
  return (
    <Svg>
      <path d="M20 150 H70 a30 14 0 0 0 60 0 H180" {...line} />
      <ellipse cx={100} cy={150} rx={30} ry={14} fill="#000" opacity={0.35} />
      <rect x={72} y={y} width={56} height={56} rx={6} fill={ACCENT} transform={`rotate(${tilt} 100 ${y + 28})`} />
    </Svg>
  );
};

// "People who do not keep promises to themselves": a chain link pulling apart.
export const BrokenLink: React.FC<{ t: number }> = ({ t }) => {
  const gap = interpolate(t, [12, 24], [0, 26], { ...clamp, easing: Easing.out(Easing.back(2)) });
  return (
    <Svg>
      <g transform={`translate(${-gap} ${gap * 0.4}) rotate(-35 70 100)`}>
        <rect x={20} y={74} width={100} height={52} rx={26} {...line} />
      </g>
      <g transform={`translate(${gap} ${-gap * 0.4}) rotate(-35 130 100)`}>
        <rect x={80} y={74} width={100} height={52} rx={26} {...accentLine} />
      </g>
      {gap > 10
        ? [-1, 1].map((d) => <path key={d} d={`M${100 + d * 6} ${70 - d * 4} l${d * 10} ${-14}`} {...line} strokeWidth={6} />)
        : null}
    </Svg>
  );
};

// "Being crazy": a lightning bolt with sparks.
export const Lightning: React.FC<{ t: number }> = ({ t }) => {
  const flash = t < 14 ? (Math.floor(t / 3) % 2 ? 1 : 0.55) : 1;
  return (
    <Svg>
      <path d="M116 18 L58 108 H98 L82 182 L148 86 H106 Z" fill={ACCENT} stroke="#111" strokeWidth={5} strokeLinejoin="round"
        opacity={flash} />
      {[
        [40, 60, 24, 44],
        [160, 140, 176, 160],
        [158, 46, 178, 30],
      ].map(([x1, y1, x2, y2]) => (
        <path key={`${x1}`} d={`M${x1} ${y1} L${x2} ${y2}`} {...line} strokeWidth={7} style={draw(t, 6, 8, 40)} />
      ))}
    </Svg>
  );
};

// "Being abnormal": one yellow star among grey dots.
export const OddOneOut: React.FC<{ t: number }> = ({ t }) => {
  const pop = interpolate(t, [8, 18], [0, 1], { ...clamp, easing: Easing.out(Easing.back(2.2)) });
  return (
    <Svg>
      {Array.from({ length: 16 }, (_, k) => {
        const x = 30 + (k % 4) * 46;
        const y = 30 + Math.floor(k / 4) * 46;
        return k === 9 ? null : <circle key={k} cx={x} cy={y} r={10} fill={MUTED} />;
      })}
      <path d="M76 100 l7 15 l16 2 l-12 11 l3 16 l-14 -8 l-14 8 l3 -16 l-12 -11 l16 -2 Z" fill={ACCENT}
        style={{ transformOrigin: "76px 120px", transform: `scale(${0.4 + 1.6 * pop})` }} />
    </Svg>
  );
};

// "Comment abnormal": a comment being typed, then liked.
export const CommentTyping: React.FC<{ t: number; word: string }> = ({ t, word }) => {
  const shown = Math.floor(interpolate(t, [6, 30], [0, word.length], clamp));
  const heart = interpolate(t, [34, 44], [0, 1], { ...clamp, easing: Easing.out(Easing.back(3)) });
  return (
    <Svg>
      <circle cx={30} cy={96} r={20} fill={MUTED} />
      <rect x={58} y={70} width={136} height={52} rx={26} fill="#2A2B31" stroke={INK} strokeWidth={4} />
      <text x={74} y={106} fill={INK} fontSize={28} fontFamily="Barlow Condensed" fontWeight={800}>
        {word.slice(0, shown)}
        {shown < word.length && t % 16 < 9 ? "|" : ""}
      </text>
      <path d="M150 168 c-18 -12 -30 -22 -30 -36 a14 14 0 0 1 30 -6 a14 14 0 0 1 30 6 c0 14 -12 24 -30 36 Z" fill={ACCENT}
        style={{ transformOrigin: "150px 150px", transform: `scale(${heart})` }} />
    </Svg>
  );
};
