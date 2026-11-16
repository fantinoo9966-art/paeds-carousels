import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme, HANDLE } from "./theme";

const C = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const ease = (
  frame: number,
  inp: [number, number],
  out: [number, number],
  e: (t: number) => number = theme.ease.out,
) => interpolate(frame, inp, out, { ...C, easing: e });

export const useSpring = (delay: number, cfg: keyof typeof theme.spring = "smooth") => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({ frame: frame - delay, fps, config: theme.spring[cfg] });
};

/** Fade + rise + scale entrance. */
export const Pop: React.FC<{
  delay?: number;
  cfg?: keyof typeof theme.spring;
  rise?: number;
  from?: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({ delay = 0, cfg = "smooth", rise = 40, from = 0.9, style, children }) => {
  const p = useSpring(delay, cfg);
  return (
    <div
      style={{
        opacity: Math.min(1, p * 1.4),
        transform: `translateY(${interpolate(p, [0, 1], [rise, 0])}px) scale(${interpolate(p, [0, 1], [from, 1])})`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** Whole-scene exit: faster than the entrances. */
export const SceneExit: React.FC<{ children: React.ReactNode; len?: number }> = ({ children, len = 10 }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const t = interpolate(frame, [durationInFrames - len, durationInFrames], [0, 1], { ...C, easing: theme.ease.in });
  return (
    <AbsoluteFill style={{ opacity: 1 - t * 0.9, transform: `translateY(${-50 * t}px) scale(${1 - 0.04 * t})` }}>
      {children}
    </AbsoluteFill>
  );
};

/** Word-by-word reveal. Words wrapped in *stars* get the highlight colour + marker swipe. */
export const Words: React.FC<{
  text: string;
  delay?: number;
  per?: number;
  size: number;
  color?: string;
  hi?: string;
  font?: string;
  weight?: number;
  align?: "center" | "left";
  gap?: number;
  lineHeight?: number;
}> = ({ text, delay = 0, per = 3, size, color = theme.colors.ink, hi = theme.colors.ink, font = theme.fonts.display, weight = 800, align = "center", gap, lineHeight = 1.08 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = text.split(" ");
  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        justifyContent: align === "center" ? "center" : "flex-start",
        columnGap: gap ?? Math.round(size * 0.24),
        rowGap: 0,
        fontFamily: font,
        fontWeight: weight,
        fontSize: size,
        lineHeight,
        color,
        letterSpacing: "-0.01em",
      }}
    >
      {words.map((w, i) => {
        // *multi word* highlights: a word is highlighted if it sits inside a *...* span
        const before = words.slice(0, i).join(" ").split("*").length - 1;
        const isHi = w.startsWith("*") || before % 2 === 1;
        const clean = w.replace(/\*/g, "");
        const p = spring({ frame: frame - delay - i * per, fps, config: theme.spring.snappy });
        const swipe = interpolate(frame - delay - i * per, [6, 16], [0, 1], { ...C, easing: theme.ease.out });
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              position: "relative",
              opacity: Math.min(1, p * 1.5),
              transform: `translateY(${interpolate(p, [0, 1], [size * 0.45, 0])}px) rotate(${interpolate(p, [0, 1], [4, 0])}deg)`,
              color: isHi ? hi : color,
            }}
          >
            {isHi && (
              <span
                style={{
                  position: "absolute",
                  left: -size * 0.08,
                  right: -size * 0.08,
                  bottom: size * 0.12,
                  height: size * 0.3,
                  background: theme.colors.lemon,
                  borderRadius: size * 0.1,
                  transformOrigin: "left center",
                  transform: `scaleX(${swipe}) rotate(-1.5deg)`,
                  zIndex: -1,
                }}
              />
            )}
            {clean}
          </span>
        );
      })}
    </div>
  );
};

/* ------------------------------------------------------------------ layers */

const Doodle: React.FC<{ kind: "plus" | "star" | "dot" | "heart"; x: number; y: number; s: number; c: string; ph: number }> = ({ kind, x, y, s, c, ph }) => {
  const frame = useCurrentFrame();
  const fy = Math.sin(frame / 34 + ph) * 12;
  const r = Math.sin(frame / 50 + ph) * 12;
  let shape: React.ReactNode;
  if (kind === "plus")
    shape = <path d="M20 4 v32 M4 20 h32" stroke={c} strokeWidth={8} strokeLinecap="round" />;
  else if (kind === "star")
    shape = <path d="M20 2 L24 15 L38 15 L27 23 L31 37 L20 29 L9 37 L13 23 L2 15 L16 15 Z" fill={c} />;
  else if (kind === "heart")
    shape = <path d="M20 36 C4 24 2 14 8 8 C13 3 19 6 20 11 C21 6 27 3 32 8 C38 14 36 24 20 36 Z" fill={c} />;
  else shape = <circle cx={20} cy={20} r={12} fill={c} />;
  return (
    <svg width={s} height={s} viewBox="0 0 40 40" style={{ position: "absolute", left: x, top: y + fy, transform: `rotate(${r}deg)`, opacity: 0.55 }}>
      {shape}
    </svg>
  );
};

const DOODLES = [
  { kind: "plus", x: 70, y: 210, s: 54, c: "#FFB3C7", ph: 0 },
  { kind: "star", x: 930, y: 260, s: 56, c: "#FFD86B", ph: 1 },
  { kind: "dot", x: 120, y: 1530, s: 38, c: "#B9A6FF", ph: 2 },
  { kind: "heart", x: 940, y: 1490, s: 54, c: "#FF9AA8", ph: 3 },
  { kind: "plus", x: 960, y: 900, s: 40, c: "#8FD9B8", ph: 4 },
  { kind: "star", x: 40, y: 880, s: 40, c: "#9CCBFF", ph: 5 },
] as const;

export const Paper: React.FC<{ tint?: string; notes?: boolean }> = ({ tint = theme.colors.bgWarm, notes = false }) => {
  const frame = useCurrentFrame();
  const d1 = Math.sin(frame / 55) * 60;
  const d2 = Math.cos(frame / 70) * 50;
  return (
    <AbsoluteFill style={{ background: theme.colors.bg, overflow: "hidden" }}>
      <div style={{ position: "absolute", width: 1300, height: 1300, borderRadius: "50%", top: -520, left: -380 + d1, filter: "blur(40px)", background: `radial-gradient(circle, ${tint}, transparent 64%)` }} />
      <div style={{ position: "absolute", width: 1100, height: 1100, borderRadius: "50%", bottom: -480, right: -360 - d2, filter: "blur(60px)", background: `radial-gradient(circle, ${theme.colors.lavender}99, transparent 64%)` }} />
      {/* dotted notebook grid */}
      {notes ? (
        <>
          <AbsoluteFill style={{ backgroundImage: `repeating-linear-gradient(180deg, transparent 0 62px, #8EB8E855 62px 65px)`, backgroundPosition: `0 ${frame * 0.4}px` }} />
          <div style={{ position: "absolute", top: 0, bottom: 0, left: 66, width: 4, background: "#FF8FA088" }} />
        </>
      ) : (
        <AbsoluteFill style={{ backgroundImage: `radial-gradient(${theme.colors.ink}14 2.2px, transparent 2.6px)`, backgroundSize: "44px 44px", backgroundPosition: `${frame * 0.3}px ${frame * 0.5}px` }} />
      )}
      {DOODLES.map((d, i) => (
        <Doodle key={i} {...(d as any)} />
      ))}
    </AbsoluteFill>
  );
};

export const Grade: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <AbsoluteFill style={{ backgroundColor: "#FFB38A", mixBlendMode: "soft-light", opacity: 0.12 }} />
    <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(255,170,120,0.10), transparent 25%, transparent 78%, rgba(120,80,160,0.10))" }} />
  </AbsoluteFill>
);

export const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  const noise = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='220' height='220' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E")`;
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        backgroundImage: noise,
        backgroundSize: "220px",
        backgroundPosition: `${(frame * 7) % 220}px ${(frame * 13) % 220}px`,
        opacity: 0.06,
        mixBlendMode: "multiply",
      }}
    />
  );
};

export const Vignette: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none", background: "radial-gradient(ellipse at center, transparent 60%, rgba(90,50,40,0.16) 100%)" }} />
);

/** Persistent branding + disclaimer (sits above content, below grade). */
export const Chrome: React.FC<{ disclaimer?: string }> = ({ disclaimer = "For information only · Always consult your doctor" }) => {
  const p = useSpring(4, "smooth");
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          top: 225,
          right: 56,
          display: "flex",
          alignItems: "center",
          gap: 10,
          padding: "10px 20px 10px 12px",
          background: "rgba(255,255,255,0.78)",
          borderRadius: 40,
          fontFamily: theme.fonts.body,
          fontWeight: 800,
          fontSize: 28,
          color: theme.colors.ink,
          opacity: p,
          transform: `translateX(${(1 - p) * 40}px)`,
          boxShadow: "0 6px 18px rgba(80,40,60,0.10)",
        }}
      >
        <svg width={34} height={34} viewBox="0 0 24 24">
          <defs>
            <linearGradient id="ig" x1="0" y1="1" x2="1" y2="0">
              <stop offset="0" stopColor="#FEC53A" />
              <stop offset="0.5" stopColor="#F2335F" />
              <stop offset="1" stopColor="#8A3AB9" />
            </linearGradient>
          </defs>
          <rect x="2" y="2" width="20" height="20" rx="6" fill="url(#ig)" />
          <circle cx="12" cy="12" r="4.6" fill="none" stroke="#fff" strokeWidth="2" />
          <circle cx="17.3" cy="6.7" r="1.3" fill="#fff" />
        </svg>
        {HANDLE}
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 300,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: theme.fonts.body,
          fontWeight: 700,
          fontSize: 25,
          color: theme.colors.inkSoft,
          opacity: 0.85 * p,
        }}
      >
        {disclaimer}
      </div>
    </AbsoluteFill>
  );
};

export const Sfx: React.FC<{ at: number; name: string; vol?: number }> = ({ at, name, vol = 0.5 }) => (
  <Sequence from={Math.max(0, at)} layout="none">
    <Audio src={staticFile(`sfx/${name}.wav`)} volume={vol} />
  </Sequence>
);

export const breathe = (frame: number, amt = 0.015, speed = 22) => 1 + Math.sin(frame / speed) * amt;
