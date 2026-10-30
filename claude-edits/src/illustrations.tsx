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
      <text x={74} y={106} fill={INK} fontSize={Math.min(28, 236 / Math.max(1, word.length))} fontFamily="Barlow Condensed" fontWeight={800}>
        {word.slice(0, shown)}
        {shown < word.length && t % 16 < 9 ? "|" : ""}
      </text>
      <path d="M150 168 c-18 -12 -30 -22 -30 -36 a14 14 0 0 1 30 -6 a14 14 0 0 1 30 6 c0 14 -12 24 -30 36 Z" fill={ACCENT}
        style={{ transformOrigin: "150px 150px", transform: `scale(${heart})` }} />
    </Svg>
  );
};

// "Here's what I learned": a lightbulb switching on.
export const Lightbulb: React.FC<{ t: number }> = ({ t }) => {
  const on = interpolate(t, [8, 14], [0, 1], clamp);
  return (
    <Svg>
      <circle cx={100} cy={84} r={70} fill={ACCENT} opacity={0.25 * on} />
      <path d="M70 120 a46 46 0 1 1 60 0 c-8 8 -10 14 -10 24 H80 c0 -10 -2 -16 -10 -24 Z" {...line} fill={on > 0.5 ? ACCENT : "none"} />
      <path d="M82 162 H118 M86 180 H114" {...line} />
      {[-60, -30, 0, 30, 60].map((a) => (
        <path key={a} d="M100 6 V20" {...accentLine} strokeWidth={7} opacity={on} transform={`rotate(${a} 100 84)`} />
      ))}
    </Svg>
  );
};

// "Walking": footprints stepping up the card.
export const Footsteps: React.FC<{ t: number }> = ({ t }) => {
  const steps = [
    [70, 160, -8],
    [124, 126, 8],
    [72, 92, -8],
    [126, 58, 8],
  ];
  return (
    <Svg>
      {steps.map(([x, y, r], k) => {
        const o = interpolate(t, [k * 6, k * 6 + 5], [0, 1], clamp);
        return (
          <g key={k} opacity={o} transform={`rotate(${r} ${x} ${y})`}>
            <ellipse cx={x} cy={y} rx={13} ry={20} fill={k === steps.length - 1 ? ACCENT : INK} />
            <circle cx={x} cy={y + 28} r={9} fill={k === steps.length - 1 ? ACCENT : INK} />
          </g>
        );
      })}
    </Svg>
  );
};

// "That's exactly why it works": an arrow hitting a target.
export const Target: React.FC<{ t: number }> = ({ t }) => {
  const fly = interpolate(t, [4, 14], [1, 0], { ...clamp, easing: Easing.in(Easing.quad) });
  return (
    <Svg>
      <circle cx={92} cy={108} r={70} {...line} />
      <circle cx={92} cy={108} r={44} {...line} />
      <circle cx={92} cy={108} r={16} fill={ACCENT} />
      <g transform={`translate(${fly * 70} ${-fly * 70})`}>
        <path d="M96 104 L170 30" {...line} strokeWidth={8} />
        <path d="M154 28 L174 26 L172 46" {...accentLine} strokeWidth={8} />
      </g>
    </Svg>
  );
};

// "It's low-impact": a feather drifting down.
export const Feather: React.FC<{ t: number }> = ({ t }) => {
  const y = Math.sin(t / 10) * 8;
  const r = Math.sin(t / 14) * 10;
  return (
    <Svg>
      <g style={{ transformOrigin: "100px 100px", transform: `translateY(${y}px) rotate(${r - 30}deg)` }}>
        <path d="M100 20 C150 50 150 130 100 180 C50 130 50 50 100 20 Z" {...line} />
        <path d="M100 30 V190" {...accentLine} strokeWidth={7} />
        {[60, 85, 110, 135].map((yy) => (
          <path key={yy} d={`M100 ${yy} L${126} ${yy - 14} M100 ${yy + 8} L74 ${yy - 6}`} {...line} strokeWidth={5} opacity={0.7} />
        ))}
      </g>
    </Svg>
  );
};

// "You can do it every day": a week ticking off.
export const StreakCalendar: React.FC<{ t: number }> = ({ t }) => (
  <Svg>
    <rect x={20} y={40} width={160} height={130} rx={16} {...line} />
    <rect x={20} y={40} width={160} height={30} rx={12} fill={ACCENT} />
    {Array.from({ length: 7 }, (_, k) => {
      const x = 40 + (k % 4) * 40;
      const y = 96 + Math.floor(k / 4) * 44;
      return <path key={k} d={`M${x - 10} ${y} l8 8 l14 -16`} {...accentLine} strokeWidth={7} style={draw(t, 4 + k * 4, 5, 40)} />;
    })}
  </Svg>
);

// "Tomorrow's workout": a dumbbell lifting.
export const Dumbbell: React.FC<{ t: number }> = ({ t }) => {
  const lift = Math.abs(Math.sin(t / 9)) * -18;
  return (
    <Svg>
      <g transform={`translate(0 ${lift}) rotate(-20 100 110)`}>
        <path d="M54 110 H146" {...line} strokeWidth={12} />
        <rect x={28} y={78} width={24} height={64} rx={8} fill={ACCENT} />
        <rect x={148} y={78} width={24} height={64} rx={8} fill={ACCENT} />
        <rect x={14} y={90} width={14} height={40} rx={5} fill={INK} />
        <rect x={172} y={90} width={14} height={40} rx={5} fill={INK} />
      </g>
    </Svg>
  );
};

// "You don't need the gym": a gym building crossed out.
export const NoGym: React.FC<{ t: number }> = ({ t }) => (
  <Svg>
    <path d="M30 80 L100 34 L170 80" {...line} />
    <rect x={44} y={80} width={112} height={92} {...line} />
    <path d="M74 126 H126 M80 112 V140 M120 112 V140" {...line} strokeWidth={7} />
    <path d="M28 28 L172 172" {...accentLine} strokeWidth={12} style={draw(t, 10, 8, 210)} />
  </Svg>
);

// "You just need some shoes": a sneaker.
export const Sneaker: React.FC<{ t: number }> = ({ t }) => {
  const bob = Math.sin(t / 8) * 4;
  return (
    <Svg>
      <g transform={`translate(0 ${bob})`}>
        <path d="M24 136 C24 100 40 80 62 74 L86 96 C110 110 140 112 170 118 C182 120 184 136 176 142 H30 Z" {...line} />
        <path d="M24 150 H180" {...accentLine} strokeWidth={12} />
        <path d="M70 92 L92 82 M82 104 L104 94 M96 112 L116 104" {...line} strokeWidth={6} />
      </g>
    </Svg>
  );
};

// "Running is amazing too": a runner mid-stride.
export const Runner: React.FC<{ t: number }> = ({ t }) => {
  const s = Math.sin(t / 4);
  return (
    <Svg>
      <circle cx={118} cy={38} r={16} fill={ACCENT} />
      <path d="M112 60 L94 110" {...line} strokeWidth={12} />
      <path d={`M108 70 L${136 + s * 10} ${92 - s * 6} M108 70 L${80 - s * 10} ${86 + s * 6}`} {...line} />
      <path d={`M94 110 L${120 + s * 14} ${140} L${118 + s * 14} ${176} M94 110 L${70 - s * 14} ${146} L${44 - s * 10} ${150}`} {...line} />
      {[0, 1, 2].map((k) => (
        <path key={k} d={`M${30 - k * 4} ${70 + k * 22} H${56 - k * 4}`} {...line} strokeWidth={5} opacity={0.6} />
      ))}
    </Svg>
  );
};

// "The best cardio for fat loss": a heartbeat line.
export const HeartPulse: React.FC<{ t: number }> = ({ t }) => {
  const beat = 1 + 0.08 * Math.max(0, Math.sin(t / 3));
  return (
    <Svg>
      <path d="M100 168 C40 124 22 96 22 70 a38 38 0 0 1 78 -14 a38 38 0 0 1 78 14 C178 96 160 124 100 168 Z" {...line}
        style={{ transformOrigin: "100px 110px", transform: `scale(${beat})` }} />
      <path d="M30 104 H70 L84 76 L100 132 L116 92 L126 104 H170" {...accentLine} strokeWidth={8} style={draw(t, 2, 16, 260)} />
    </Svg>
  );
};

// "One you can consistently stick to": a steady flame.
export const Flame: React.FC<{ t: number }> = ({ t }) => {
  const f = 1 + 0.05 * Math.sin(t / 2.5);
  return (
    <Svg>
      <g style={{ transformOrigin: "100px 180px", transform: `scaleY(${f})` }}>
        <path d="M100 20 C130 60 160 86 160 126 a60 60 0 0 1 -120 0 C40 98 60 82 70 60 C78 84 88 92 96 96 C100 70 96 44 100 20 Z" {...line} />
        <path d="M100 98 C116 118 128 130 128 146 a28 28 0 0 1 -56 0 C72 128 88 118 100 98 Z" fill={ACCENT} />
      </g>
    </Svg>
  );
};

// "Stop sitting for 12 hours": a chair with a clock spinning round.
export const Chair: React.FC<{ t: number }> = ({ t }) => (
  <Svg>
    <path d="M60 30 V120 H140 M60 120 V176 M140 120 V176 M60 86 H120" {...line} />
    <circle cx={150} cy={52} r={30} {...accentLine} strokeWidth={7} />
    <path d="M150 52 V34" {...accentLine} strokeWidth={6} style={{ transformOrigin: "150px 52px", transform: `rotate(${t * 24}deg)` }} />
    <path d="M150 52 L162 58" {...accentLine} strokeWidth={6} />
  </Svg>
);

// "Stop starving yourself": an empty plate with a fork and knife, a hungry rumble wobbling over it.
export const EmptyPlate: React.FC<{ t: number }> = ({ t }) => {
  const rumble = interpolate(t, [10, 22], [0, 1], clamp);
  const wob = Math.sin(t / 3) * 3 * rumble;
  return (
    <Svg>
      <circle cx={100} cy={112} r={58} {...line} />
      <circle cx={100} cy={112} r={34} {...line} stroke={MUTED} strokeWidth={6} />
      <path d="M22 70 V104 M14 70 V92 Q14 104 22 104 Q30 104 30 92 V70 M22 104 V170" {...line} strokeWidth={7} />
      <path d="M178 70 Q166 92 172 118 H178 V170" {...line} strokeWidth={7} />
      <path d={`M70 ${36 + wob} Q85 ${24 - wob} 100 ${36 + wob} T130 ${36 + wob}`} {...accentLine} opacity={rumble}
        style={draw(t, 10, 12, 80)} />
    </Svg>
  );
};

// "Eating everything inside your fridge": the fridge door swings open and the light comes on.
export const Fridge: React.FC<{ t: number }> = ({ t }) => {
  const open = interpolate(t, [8, 22], [0, 1], { ...clamp, easing: Easing.out(Easing.back(1.6)) });
  return (
    <Svg>
      <rect x={52} y={22} width={96} height={160} rx={14} {...line} />
      <path d="M52 80 H148" {...line} />
      <rect x={60} y={30} width={80} height={144} rx={8} fill={ACCENT} opacity={0.85 * open} />
      <path d="M66 104 H134 M66 140 H134" {...line} stroke="#111" strokeWidth={6} opacity={open} />
      <g style={{ transformOrigin: "52px 100px", transform: `perspective(400px) rotateY(${-110 * open}deg)` }}>
        <rect x={52} y={22} width={96} height={160} rx={14} {...line} fill="#1b1b1b" />
        <path d="M52 80 H148 M132 44 V64 M132 96 V128" {...line} />
      </g>
    </Svg>
  );
};

// "Eat real food": an apple whose leaf sprouts.
export const Apple: React.FC<{ t: number }> = ({ t }) => {
  const leaf = interpolate(t, [10, 22], [0, 1], { ...clamp, easing: Easing.out(Easing.back(2)) });
  return (
    <Svg>
      <path d="M100 66 C70 44 26 58 30 108 C34 152 66 186 100 172 C134 186 166 152 170 108 C174 58 130 44 100 66 Z" {...line} />
      <path d="M100 66 Q98 46 108 30" {...line} />
      <path d="M108 44 Q134 26 152 40 Q130 60 108 44 Z" fill={ACCENT}
        style={{ transformOrigin: "108px 44px", transform: `scale(${leaf})` }} />
      <path d="M58 100 Q60 84 74 78" {...accentLine} strokeWidth={7} style={draw(t, 16, 10, 40)} />
    </Svg>
  );
};

// "Halloween is today": a jack-o'-lantern whose face lights up.
export const Pumpkin: React.FC<{ t: number }> = ({ t }) => {
  const glow = interpolate(t, [8, 18], [0, 1], { ...clamp, easing: ease });
  const flicker = 0.85 + 0.15 * Math.sin(t / 2.3);
  return (
    <Svg>
      <path d="M100 58 C60 50 26 74 28 116 C30 158 64 180 100 176 C136 180 170 158 172 116 C174 74 140 50 100 58 Z" {...line} />
      <path d="M100 58 C86 80 86 156 100 176 M100 58 C114 80 114 156 100 176" {...line} strokeWidth={6} />
      <path d="M100 58 Q98 40 110 28" {...line} />
      <g opacity={glow * flicker}>
        <path d="M58 104 L76 90 L84 112 Z M142 104 L124 90 L116 112 Z" fill={ACCENT} />
        <path d="M60 134 Q100 160 140 134 L128 136 L120 146 L110 138 L100 148 L90 138 L80 146 L72 136 Z" fill={ACCENT} />
      </g>
    </Svg>
  );
};
