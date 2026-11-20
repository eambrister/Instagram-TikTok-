// Transparent coaching overlay for Edison's form videos: a label card that springs in, an arrow that draws
// itself onto the target (e.g. the bar), a glowing highlight line, a pulsing target ring, muscle tags and
// drifting gold particles. Rendered with alpha and composited over graded footage.
import React, { useEffect, useState } from 'react';
import { AbsoluteFill, continueRender, delayRender, Easing, interpolate, random, spring, staticFile,
  useCurrentFrame, useVideoConfig } from 'remotion';

const GOLD = '#D6A918', PALE = '#F3D878', IVORY = '#F6EFE2', OBS = '#07080A';

export const formCalloutDefaults = {
  label: 'CHIN OVER BAR',
  kicker: 'FULL REP',
  barY: 548, barX0: 300, barX1: 790,      // the line to highlight (px)
  target: { x: 545, y: 548 },              // where the arrow lands
  tags: ['LATS', 'BICEPS', 'GRIP'],
};
type Props = typeof formCalloutDefaults;

const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    const faces = [new FontFace('Barlow', `url(${staticFile('BarlowCondensed-ExtraBold.ttf')})`),
      new FontFace('Mont', `url(${staticFile('Montserrat-Bold.ttf')})`)];
    Promise.all(faces.map((f) => f.load())).then((l) => { l.forEach((f) => document.fonts.add(f)); continueRender(h); });
  }, [h]);
};

export const FormCallout: React.FC<Props> = ({ label, kicker, barY, barX0, barX1, target, tags }) => {
  useFonts();
  const f = useCurrentFrame();
  const { fps, durationInFrames: N } = useVideoConfig();
  const out = interpolate(f, [N - 12, N], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // label card
  const cardIn = spring({ frame: f - 2, fps, config: { damping: 14, stiffness: 140 } });
  const cardY = 300;
  const wipe = interpolate(f, [6, 22], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) });

  // arrow from card to target (quadratic curve), drawn with dash offset
  const sx = 760, sy = cardY + 150;
  const cx = 900, cy = (sy + target.y) / 2 + 20;
  const path = `M ${sx} ${sy} Q ${cx} ${cy} ${target.x + 40} ${target.y - 34}`;
  const draw = interpolate(f, [14, 34], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic) });
  const L = 600;
  const head = interpolate(f, [32, 38], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // highlight line along the bar
  const bar = interpolate(f, [30, 46], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.quad) });
  const pulse = (f - 36) / 26;
  const ring = f > 36 ? [0, 1].map((k) => ((pulse + k * 0.5) % 1 + 1) % 1) : [];

  return (
    <AbsoluteFill style={{ opacity: out }}>
      <svg width={1080} height={1920} style={{ position: 'absolute' }}>
        <defs>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="7" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>
        {/* particles */}
        {new Array(26).fill(0).map((_, i) => {
          const x = random(`x${i}`) * 1080, y0 = 250 + random(`y${i}`) * 1300, sp = 0.6 + random(`s${i}`) * 1.4;
          const y = y0 - f * sp * 2, sz = 3 + random(`z${i}`) * 6;
          const a = interpolate(f, [0, 20], [0, 0.55 * random(`a${i}`) + 0.15], { extrapolateRight: 'clamp' });
          return <rect key={i} x={x} y={y} width={sz} height={sz} fill={PALE} opacity={a}
            transform={`rotate(${f * sp * 3 + i * 40} ${x + sz / 2} ${y + sz / 2})`} />;
        })}
        {/* bar highlight */}
        <line x1={barX0} y1={barY} x2={barX0 + (barX1 - barX0) * bar} y2={barY} stroke={PALE} strokeWidth={9}
          strokeLinecap="round" filter="url(#glow)" />
        {/* target rings */}
        {ring.map((r, i) => (
          <circle key={i} cx={target.x} cy={target.y} r={20 + 70 * r} fill="none" stroke={GOLD} strokeWidth={5 * (1 - r)} opacity={1 - r} />
        ))}
        {f > 34 && <circle cx={target.x} cy={target.y} r={11} fill={PALE} filter="url(#glow)" />}
        {/* arrow */}
        <path d={path} fill="none" stroke={IVORY} strokeWidth={8} strokeLinecap="round" strokeDasharray={L}
          strokeDashoffset={L * (1 - draw)} filter="url(#glow)" />
        <g opacity={head} transform={`translate(${target.x + 40} ${target.y - 34}) rotate(${215}) scale(${head})`}>
          <path d="M 0 0 L 34 -16 L 26 0 L 34 16 Z" fill={IVORY} />
        </g>
      </svg>
      {/* label card */}
      <div style={{ position: 'absolute', left: 90, top: cardY, transform: `translateY(${(1 - cardIn) * 60}px) scale(${0.9 + 0.1 * cardIn})`,
        opacity: cardIn, transformOrigin: 'left center' }}>
        <div style={{ fontFamily: 'Mont', fontSize: 30, letterSpacing: 8, color: GOLD, marginBottom: 6 }}>{kicker}</div>
        <div style={{ position: 'relative', background: 'rgba(7,8,10,0.82)', border: `3px solid ${GOLD}`, borderRadius: 22,
          padding: '10px 34px 6px', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${wipe * 100}%`,
            background: `linear-gradient(90deg, rgba(214,169,24,0.0), rgba(214,169,24,0.28))` }} />
          <div style={{ position: 'relative', fontFamily: 'Barlow', fontSize: 108, color: IVORY, letterSpacing: 2, lineHeight: 1.05 }}>{label}</div>
        </div>
      </div>
      {/* muscle tags */}
      <div style={{ position: 'absolute', left: 0, right: 0, top: 1300, display: 'flex', justifyContent: 'center', gap: 22 }}>
        {tags.map((t, i) => {
          const s = spring({ frame: f - 44 - i * 6, fps, config: { damping: 12, stiffness: 160 } });
          return (
            <div key={t} style={{ fontFamily: 'Barlow', fontSize: 58, color: OBS, background: PALE, borderRadius: 40,
              padding: '6px 30px 2px', transform: `translateY(${(1 - s) * 80}px) scale(${s})`, opacity: s }}>{t}</div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
