/* Script-driven scenes. Same brand pieces as the hand-made Reels (Baby, icons, fonts, palette, SFX),
   laid out with flex columns + text auto-fit so any script fits the safe area (y 300 to 1540). */
import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "./theme";
import { Baby } from "./Baby";
import { Icon, IconName } from "./Icons";
import { Icon2, Icon2Name } from "./Icons2";
import { Germ, Icon3 } from "./Icons3";
import { Pop, SceneExit, Sfx, Words, ease, useSpring } from "./fx";
import { CTA } from "./scenes";
import type { Item, Scene, Script, Side, Visual } from "./types";

const c = theme.colors;
const RED = "#E5384B";
const CL = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const TOP = 300;
const BOTTOM = 1540;
const SIDE = 64;
const WIDTH = 1080 - SIDE * 2;
export const T = 14; // transition frames

/* ---------------------------------------------------------------- timing */
export const readS = (t = "") => 0.6 + t.replace(/\*/g, "").length / 16;
const sec = (s: number, pace: number) => Math.round(s * 30 * pace);
const itemText = (it: Item) => `${it.text} ${it.sub ?? ""}`;

/** Frame at which each list item / card / pearl appears. */
export const delays = (texts: string[], pace: number, first = 1.0) => {
  const out: number[] = [];
  let t = sec(first, pace);
  for (const s of texts) {
    out.push(t);
    t += sec(0.35 + readS(s) * 0.45, pace);
  }
  return out;
};

const sceneTexts = (s: Scene): string[] => {
  switch (s.type) {
    case "list": return s.items.map(itemText);
    case "cards": return s.cards.map((k) => `${k.title} ${k.lines.join(" ")}`);
    case "pearls": return s.items;
    case "split": return [...s.left.lines, ...s.right.lines];
    default: return [];
  }
};

export const sceneLen = (s: Scene, pace: number): number => {
  switch (s.type) {
    case "hook": return sec(4.0, pace);
    case "cta": return sec(3.8, pace);
    case "big": return Math.max(sec(3.4, pace), sec(1.2 + readS(s.text) * 0.8 + readS(s.sub) * 0.7, pace));
    case "split": return sec(3.0 + sceneTexts(s).reduce((a, t) => a + readS(t) * 0.4, 0), pace);
    default: {
      const texts = sceneTexts(s);
      const d = delays(texts, pace);
      return d[d.length - 1] + sec(readS(texts[texts.length - 1]) * 0.4 + 1.5, pace);
    }
  }
};

export const totalLen = (sc: Script) => {
  const pace = sc.pace ?? 1.0;
  return sc.scenes.reduce((a, s) => a + sceneLen(s, pace), 0) - T * (sc.scenes.length - 1);
};

/* ---------------------------------------------------------------- text fitting */
/** Biggest font size (min..max) at which `text` fits a w x h box (Baloo/Nunito average glyph ~0.52em). */
export const fit = (text: string, w: number, h: number, max: number, min = 30, lh = 1.14) => {
  const clean = text.replace(/\*/g, "");
  for (let size = max; size > min; size -= 2) {
    const perLine = Math.max(4, Math.floor(w / (size * 0.5)));
    const words = clean.split(/\s+/);
    let lines = 1, cur = 0;
    for (const wd of words) {
      if (cur && cur + 1 + wd.length > perLine) { lines++; cur = wd.length; } else cur += (cur ? 1 : 0) + wd.length;
    }
    if (lines * size * lh <= h) return size;
  }
  return min;
};

/** Body text with **key values** in red (PG) or bold ink on a lemon marker (parents). */
export const Rich: React.FC<{ text: string; size: number; pg: boolean; color?: string; weight?: number; align?: "left" | "center" }> = ({ text, size, pg, color = c.ink, weight = 700, align = "left" }) => {
  const parts = text.split("**");
  return (
    <div style={{ fontFamily: theme.fonts.display, fontWeight: weight, fontSize: size, lineHeight: 1.14, color, textAlign: align }}>
      {parts.map((p, i) =>
        i % 2 ? (
          <span key={i} style={pg ? { color: RED, fontWeight: 800 } : { fontWeight: 800, background: `linear-gradient(transparent 58%, ${c.lemon} 58%)` }}>{p}</span>
        ) : (
          <span key={i}>{p.replace(/\*/g, "")}</span>
        ),
      )}
    </div>
  );
};

/* ---------------------------------------------------------------- icons */
const ICON1 = ["newborn", "lungs", "sleep", "bottle", "rash", "bolt", "calendar", "shirt", "water", "syrup", "ice", "pill", "siren", "eye"];
const ICON2 = ["packet", "drop", "lips", "tear", "urine", "sunken", "zinc", "breast", "bowl", "soda", "blood", "noglass", "clock", "cal", "lamp", "tube", "bulb", "warn", "stool", "camera", "liver", "dna", "shield"];
const ICON3 = ["nosedrop", "honey", "cup", "kettle", "rubjar", "heart"];
export const ICON_NAMES = [...ICON1, ...ICON2, ...ICON3, "germ"];

export const AnyIcon: React.FC<{ name?: string; size: number }> = ({ name = "", size }) => {
  if (ICON1.includes(name)) return <Icon name={name as IconName} size={size} />;
  if (ICON2.includes(name)) return <Icon2 name={name as Icon2Name} size={size} />;
  if (ICON3.includes(name)) return <Icon3 name={name as any} size={size} />;
  if (name === "germ") return <Germ size={size} color="#8FD98A" />;
  if (name) return <div style={{ fontSize: size * 0.62, lineHeight: 1, width: size, height: size, display: "flex", alignItems: "center", justifyContent: "center" }}>{name}</div>;
  return null;
};

/* ---------------------------------------------------------------- shared layout */
const Column: React.FC<{ children: React.ReactNode; top?: number; gap?: number }> = ({ children, top = TOP, gap = 30 }) => (
  <div style={{ position: "absolute", top, bottom: 1920 - BOTTOM, left: SIDE, right: SIDE, display: "flex", flexDirection: "column", gap }}>{children}</div>
);

const titleSize = (t: string, pg: boolean) => fit(t, WIDTH, pg ? 190 : 250, pg ? 80 : 98, 56, 1.08);
const titleH = (t: string, pg: boolean) => {
  const s = titleSize(t, pg);
  const per = Math.floor(WIDTH / (s * 0.5));
  return Math.ceil(t.replace(/\*/g, "").length / per) * s * 1.1;
};

const Title: React.FC<{ text: string; pg: boolean; seed: number }> = ({ text, pg, seed }) => {
  const size = titleSize(text, pg);
  if (!pg && seed % 3 === 1) {
    // ribbon heading variant
    const p = useSpring(0, "snappy");
    return (
      <div style={{ display: "flex", justifyContent: "center" }}>
        <div style={{ padding: "14px 50px 8px", background: c.lemon, border: `5px solid ${c.ink}`, boxShadow: `0 10px 0 ${c.ink}`, transform: "rotate(-1.5deg)", clipPath: `inset(0 ${(1 - p) * 100}% 0 0)` }}>
          <Rich text={text} size={Math.min(size, 84)} pg={false} weight={800} align="center" />
        </div>
      </div>
    );
  }
  return <Words text={text} size={size} align={pg ? "left" : "center"} delay={2} per={pg ? 3 : 5} hi={c.ink} />;
};

const Tab: React.FC<{ text: string }> = ({ text }) => {
  const p = useSpring(0, "snappy");
  return <div style={{ position: "absolute", top: 232, left: 70, padding: "8px 22px", borderRadius: 14, background: c.ink, color: c.white, fontFamily: theme.fonts.body, fontWeight: 800, fontSize: 26, letterSpacing: "0.08em", opacity: p, transform: `translateX(${(1 - p) * -40}px)`, zIndex: 5 }}>{text}</div>;
};

const Stamp: React.FC<{ kind: "good" | "bad"; at: number; size?: number }> = ({ kind, at, size = 92 }) => {
  const f = useCurrentFrame();
  const p = useSpring(at, kind === "bad" ? "snappy" : "bouncy");
  const t = ease(f - at, [0, 12], [0, 1]);
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" style={{ flex: "0 0 auto", opacity: Math.min(1, p * 2), transform: `scale(${kind === "bad" ? interpolate(p, [0, 1], [2.2, 1]) : 0.6 + 0.4 * p}) rotate(${kind === "bad" ? -12 : 0}deg)` }}>
      <circle cx={50} cy={50} r={44} fill={kind === "bad" ? c.hero : c.good} stroke={c.ink} strokeWidth={6} />
      {kind === "bad" ? <path d="M32 32 l36 36 M68 32 l-36 36" stroke="#fff" strokeWidth={12} strokeLinecap="round" /> : <path d="M28 52 l15 15 l30 -32" stroke="#fff" strokeWidth={11} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={80} strokeDashoffset={80 * (1 - t)} />}
    </svg>
  );
};

/* ================================================================ HOOK */
const Xray: React.FC<{ haze: number; size: number }> = ({ haze, size }) => (
  <svg width={size} height={size * 1.05} viewBox="0 0 100 105">
    <rect x={0} y={0} width={100} height={105} rx={6} fill="#0E1220" />
    <rect x={3} y={3} width={94} height={99} rx={4} fill="#1B2440" />
    {[0, 1].map((s) => <path key={s} d={s ? "M54 22 q22 -4 30 22 q6 30 -2 50 q-14 6 -28 -2 z" : "M46 22 q-22 -4 -30 22 q-6 30 2 50 q14 6 28 -2 z"} fill="#2B3556" stroke="#8FA3C8" strokeWidth={0.8} />)}
    {[0, 1].map((s) => <path key={`h${s}`} d={s ? "M54 22 q22 -4 30 22 q6 30 -2 50 q-14 6 -28 -2 z" : "M46 22 q-22 -4 -30 22 q-6 30 2 50 q14 6 28 -2 z"} fill="#E8EEF8" opacity={0.15 + haze * 0.6} />)}
    <rect x={48} y={10} width={4} height={90} fill="#C9D4EA" opacity={0.5} />
  </svg>
);

const Hook: React.FC<{ s: Extract<Scene, { type: "hook" }>; pg: boolean; seed: number }> = ({ s, pg, seed }) => {
  const f = useCurrentFrame();
  const b = useSpring(8, "bouncy");
  const wob = Math.sin(f / 5) * ease(f, [30, 50], [0, 4]);
  const tSize = fit(s.title, WIDTH, 380, pg ? 118 : 116, 70, 1.08);
  return (
    <SceneExit>
      <Column gap={22}>
        <Words text={s.title} size={tSize} delay={4} per={5} />
        {s.sub && <Words text={s.sub} size={fit(s.sub, WIDTH, 150, 60, 40)} color={c.inkSoft} delay={20} per={3} />}
        <div style={{ flex: 1, position: "relative", display: "flex", alignItems: "center", justifyContent: "center", gap: 30 }}>
          {s.visual === "xray" ? (
            <>
              <Pop delay={8} cfg="bouncy" from={0.5}><Baby mood={s.mood ?? "sleepy"} size={380} skin={s.skin} /></Pop>
              <Pop delay={22} cfg="bouncy" from={0.5}><Xray haze={ease(f, [30, 100], [0.1, 0.9])} size={440} /></Pop>
            </>
          ) : (
            <div style={{ opacity: Math.min(1, b * 1.5), transform: `scale(${0.6 + 0.4 * b}) rotate(${wob}deg)` }}>
              <Baby mood={s.mood ?? "think"} size={480} skin={s.skin} />
            </div>
          )}
          {s.icon && s.visual !== "xray" && (
            <Pop delay={40} cfg="bouncy" from={0.3} style={{ position: "absolute", right: seed % 2 ? 0 : undefined, left: seed % 2 ? undefined : 0, bottom: 20 }}>
              <div style={{ transform: `rotate(${Math.sin(f / 7) * 8}deg)` }}><AnyIcon name={s.icon} size={210} /></div>
            </Pop>
          )}
        </div>
        {s.hand && (
          <Pop delay={52} cfg="bouncy" from={0.3} style={{ textAlign: "center" }}>
            <div style={{ fontFamily: theme.fonts.hand, fontWeight: 700, fontSize: 92, color: c.ink, transform: "rotate(-4deg)" }}>{s.hand}</div>
          </Pop>
        )}
      </Column>
      <Sfx at={0} name="whoosh" vol={0.3} />
      <Sfx at={4} name="pop" vol={0.35} />
      <Sfx at={26} name="riser" vol={0.2} />
      <Sfx at={40} name="pop" vol={0.35} />
      {s.hand && <Sfx at={52} name="stamp" vol={0.35} />}
    </SceneExit>
  );
};

/* ================================================================ BIG MESSAGE */
const BigVisual: React.FC<{ v: Visual }> = ({ v }) => {
  const f = useCurrentFrame();
  if (v.kind === "calendar") {
    const n = Math.round(interpolate(f, [20, 80], [v.from, v.to], { ...CL, easing: theme.ease.inOut }));
    return (
      <div style={{ width: 380, height: 390, borderRadius: 40, background: c.white, border: `6px solid ${c.ink}`, boxShadow: `10px 12px 0 ${c.ink}`, overflow: "hidden" }}>
        <div style={{ height: 96, background: c.peach, borderBottom: `6px solid ${c.ink}`, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 52, textAlign: "center", lineHeight: "100px", color: c.ink }}>{v.label ?? "DAY"}</div>
        <div style={{ fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 200, textAlign: "center", lineHeight: "280px", color: c.ink }}>{n}</div>
      </div>
    );
  }
  if (v.kind === "number") {
    const m = v.value.match(/^([^\d]*)([\d.]+)(.*)$/);
    const target = m ? parseFloat(m[2]) : 0;
    const dec = m && m[2].includes(".") ? m[2].split(".")[1].length : 0;
    const cur = interpolate(f, [12, 60], [0, target], { ...CL, easing: theme.ease.out });
    return (
      <div style={{ textAlign: "center" }}>
        <div style={{ fontFamily: theme.fonts.display, fontWeight: 800, fontSize: fit(v.value, WIDTH, 300, 240, 120), lineHeight: 1, color: c.hero }}>{m ? `${m[1]}${cur.toFixed(dec)}${m[3]}` : v.value}</div>
        {v.label && <div style={{ fontFamily: theme.fonts.body, fontWeight: 800, fontSize: 48, color: c.inkSoft }}>{v.label}</div>}
      </div>
    );
  }
  if (v.kind === "drop") {
    const lvl = ease(f, [20, 80], [1, 0.25], theme.ease.inOut);
    return (
      <svg width={380} height={500} viewBox="0 0 100 130">
        <defs><clipPath id="kdrop"><path d="M50 4 C50 4 12 52 12 82 a38 38 0 0 0 76 0 C88 52 50 4 50 4 Z" /></clipPath></defs>
        <path d="M50 4 C50 4 12 52 12 82 a38 38 0 0 0 76 0 C88 52 50 4 50 4 Z" fill={c.white} />
        <g clipPath="url(#kdrop)"><path d={`M0 ${120 - 112 * lvl + Math.sin(f / 5) * 2} q12 -4 25 0 t25 0 t25 0 t25 0 V130 H0 Z`} fill="#7CC8FF" /></g>
        <path d="M50 4 C50 4 12 52 12 82 a38 38 0 0 0 76 0 C88 52 50 4 50 4 Z" fill="none" stroke={c.ink} strokeWidth={4} />
      </svg>
    );
  }
  if (v.kind === "clock") return <Pop delay={10} cfg="bouncy" from={0.5}><Icon2 name="clock" size={380} /></Pop>;
  return (
    <div style={{ transform: `translateY(${Math.sin(f / 12) * 10}px) rotate(${Math.sin(f / 20) * 4}deg)` }}>
      <AnyIcon name={(v as any).name} size={380} />
    </div>
  );
};

const Big: React.FC<{ s: Extract<Scene, { type: "big" }>; pg: boolean }> = ({ s, pg }) => (
  <SceneExit>
    <Column gap={30}>
      <Words text={s.text} size={fit(s.text, WIDTH, 360, 104, 60, 1.08)} delay={2} per={5} hi={c.ink} />
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
        {s.visual && <Pop delay={12} cfg="bouncy" from={0.4}><BigVisual v={s.visual} /></Pop>}
      </div>
      {s.sub && (
        <Pop delay={50} cfg="snappy" style={{ textAlign: "center" }}>
          <Rich text={s.sub} size={fit(s.sub, WIDTH, 220, 70, 40)} pg={pg} align="center" color={c.inkSoft} />
        </Pop>
      )}
    </Column>
    <Sfx at={2} name="whoosh" vol={0.3} />
    <Sfx at={12} name="pop" vol={0.35} />
    <Sfx at={50} name="ding" vol={0.3} />
  </SceneExit>
);

/* ================================================================ SPLIT */
const Half: React.FC<{ side: Side; left: boolean; bg: string; delay: number; h: number; pg: boolean }> = ({ side, left, bg, delay, h, pg }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: f - delay, fps, config: theme.spring.smooth });
  const w = (WIDTH - 40) / 2;
  const lineH = (h - 120 - (side.icon ? 200 : 0) - (side.verdict ? 110 : 0)) / Math.max(1, side.lines.length);
  const size = Math.min(...side.lines.map((l) => fit(l, w - 70, lineH - 12, 60, 32)));
  return (
    <div style={{ width: w, height: h, borderRadius: 40, background: bg, border: `5px solid ${c.ink}`, padding: "26px 24px", display: "flex", flexDirection: "column", gap: 14, transform: `translateX(${(1 - p) * (left ? -560 : 560)}px)` }}>
      <div style={{ fontFamily: theme.fonts.display, fontWeight: 800, fontSize: fit(side.title, w - 50, 160, 70, 42, 1.0), color: c.ink, textAlign: "center", lineHeight: 1 }}>{side.title}</div>
      {side.icon && <div style={{ display: "flex", justifyContent: "center", height: 190 }}><AnyIcon name={side.icon} size={190} /></div>}
      {side.lines.map((l, k) => (
        <Pop key={k} delay={delay + 16 + k * 12} cfg="snappy" rise={24}>
          <div style={{ display: "flex", gap: 10 }}><span style={{ fontFamily: theme.fonts.display, fontSize: size, color: c.inkSoft }}>•</span><Rich text={l} size={size} pg={pg} /></div>
        </Pop>
      ))}
      <div style={{ flex: 1 }} />
      {side.verdict && (
        <Pop delay={delay + 60} cfg="bouncy" from={0.5}>
          <div style={{ textAlign: "center", padding: "10px 6px 4px", borderRadius: 24, background: c.white, border: `4px solid ${c.ink}`, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: fit(side.verdict, w - 70, 110, 46, 30), color: c.ink }}>{side.verdict}</div>
        </Pop>
      )}
    </div>
  );
};

const Split: React.FC<{ s: Extract<Scene, { type: "split" }>; pg: boolean; seed: number }> = ({ s, pg, seed }) => {
  const h = BOTTOM - TOP - titleH(s.title, pg) - 60;
  return (
    <SceneExit>
      <Column>
        <Title text={s.title} pg={pg} seed={seed} />
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <Half side={s.left} left bg={c.mint} delay={10} h={h} pg={pg} />
          <Half side={s.right} left={false} bg={c.pink} delay={40} h={h} pg={pg} />
        </div>
      </Column>
      <Sfx at={0} name="pop" vol={0.35} />
      <Sfx at={10} name="whoosh" vol={0.3} />
      <Sfx at={40} name="whoosh" vol={0.3} />
      <Sfx at={70} name="ding" vol={0.3} />
    </SceneExit>
  );
};

/* ================================================================ LISTS */
const TINTS = [c.sky, c.pink, c.lemon, c.mint, c.lavender, c.peach];

type LP = { s: Extract<Scene, { type: "list" }>; pg: boolean; seed: number; d: number[]; h: number };

const Rows: React.FC<LP> = ({ s, pg, seed, d, h }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const n = s.items.length;
  const gap = n > 6 ? 12 : 18;
  const rowH = Math.min(210, (h - gap * (n - 1)) / n);
  const hasIcon = s.items.some((i) => i.icon);
  const ic = Math.min(140, rowH - 30);
  const textW = WIDTH - 48 - (hasIcon ? ic + 20 : 30) - (s.tone === "good" || s.tone === "bad" ? 110 : 0);
  const size = Math.min(...s.items.map((it) => fit(it.text, textW, (rowH - 26) * (it.sub ? 0.62 : 1), 60, 30)));
  const enter = seed % 3;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap }}>
      {s.items.map((it, k) => {
        const p = spring({ frame: f - d[k], fps, config: theme.spring.smooth });
        const tr = enter === 0 ? `translateX(${(1 - p) * -700}px)` : enter === 1 ? `translateY(${(1 - p) * 140}px) scale(${0.85 + 0.15 * p})` : `translateY(${(1 - p) * -120}px) rotate(${(1 - p) * (k % 2 ? 5 : -5)}deg)`;
        return (
          <div key={k} style={{ height: rowH, display: "flex", alignItems: "center", gap: 18, padding: "8px 24px", borderRadius: Math.min(36, rowH / 3), background: c.white, border: `4px solid ${c.ink}`, boxShadow: `6px 7px 0 ${c.ink}`, opacity: Math.min(1, p * 1.6), transform: tr }}>
            {hasIcon ? (
              <div style={{ flex: "0 0 auto", width: ic, height: ic, borderRadius: 26, background: TINTS[(k + seed) % TINTS.length], display: "flex", alignItems: "center", justifyContent: "center" }}><AnyIcon name={it.icon} size={ic * 0.85} /></div>
            ) : s.tone === "alert" ? (
              <div style={{ flex: "0 0 auto", width: 26, height: 26, borderRadius: 13, background: c.hero, boxShadow: `0 0 0 6px ${c.heroSoft}` }} />
            ) : (
              <div style={{ flex: "0 0 auto", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: size * 1.1, color: c.inkSoft, minWidth: size * 0.9 }}>{k + 1}</div>
            )}
            <div style={{ flex: 1 }}>
              <Rich text={it.text} size={size} pg={pg} />
              {it.sub && <Rich text={it.sub} size={Math.round(size * 0.78)} pg={pg} color={c.inkSoft} weight={600} />}
            </div>
            {(s.tone === "good" || s.tone === "bad") && <Stamp kind={s.tone} at={d[k] + 12} />}
            <Sfx at={d[k]} name={s.tone === "bad" ? "whoosh" : "pop"} vol={0.3} />
            {s.tone === "bad" && <Sfx at={d[k] + 12} name="stamp" vol={0.35} />}
          </div>
        );
      })}
    </div>
  );
};

const Notes: React.FC<LP> = ({ s, pg, seed, d, h }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const n = s.items.length;
  const rows = Math.ceil(n / 2);
  const gap = 34;
  const noteH = Math.min(500, (h - gap * (rows - 1) - 20) / rows);
  const w = (WIDTH - gap) / 2;
  const ic = s.items.some((i) => i.icon) ? Math.min(130, noteH * 0.3) : 0;
  const size = Math.min(...s.items.map((it) => fit(itemText(it), w - 50, noteH - ic - 90, 54, 30)));
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap }}>
      {s.items.map((it, k) => {
        const p = spring({ frame: f - d[k], fps, config: theme.spring.bouncy });
        const rot = [-3, 2.5, 2, -2.5, 1.5, -2][k % 6];
        return (
          <div key={k} style={{ position: "relative", height: noteH, background: TINTS[(k + seed) % TINTS.length], border: `5px solid ${c.ink}`, borderRadius: 10, padding: "44px 22px 18px", display: "flex", flexDirection: "column", alignItems: "center", gap: 12, transform: `rotate(${rot}deg) translateY(${(1 - p) * -500}px)`, opacity: Math.min(1, p * 2) }}>
            <div style={{ position: "absolute", top: -20, left: "50%", width: 130, height: 40, marginLeft: -65, background: "#ffffffaa", border: `3px solid ${c.ink}33`, transform: "rotate(-4deg)" }} />
            {ic > 0 && <AnyIcon name={it.icon} size={ic} />}
            <Rich text={it.text} size={size} pg={pg} align="center" />
            {it.sub && <Rich text={it.sub} size={Math.round(size * 0.8)} pg={pg} align="center" color={c.inkSoft} weight={600} />}
            {(s.tone === "good" || s.tone === "bad") && <div style={{ position: "absolute", right: -22, bottom: -22 }}><Stamp kind={s.tone} at={d[k] + 14} size={110} /></div>}
            <Sfx at={d[k]} name="whoosh" vol={0.22} />
            {s.tone === "bad" && <Sfx at={d[k] + 14} name="stamp" vol={0.35} />}
          </div>
        );
      })}
    </div>
  );
};

const Chat: React.FC<LP> = ({ s, pg, d, h }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const n = s.items.length;
  const bubH = (h - 16 * (n - 1)) / n;
  const size = Math.min(...s.items.map((it) => fit(itemText(it), 760, Math.min(bubH, 190) - 58, 58, 40)));
  const shown = d.filter((t) => f >= t).length;
  const typing = shown < n && f > 6 && d[shown] - f < 16;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {s.items.slice(0, shown).map((it, k) => {
        const p = spring({ frame: f - d[k], fps, config: theme.spring.snappy });
        const right = k % 2 === 1;
        return (
          <div key={k} style={{ alignSelf: right ? "flex-end" : "flex-start", maxWidth: 840, padding: "16px 26px 10px", borderRadius: right ? "34px 34px 8px 34px" : "34px 34px 34px 8px", background: right ? "#DCF8C6" : c.white, border: `4px solid ${c.ink}`, boxShadow: `5px 6px 0 ${c.ink}`, opacity: Math.min(1, p * 1.5), transform: `translateY(${(1 - p) * 40}px) scale(${0.8 + 0.2 * p})`, transformOrigin: right ? "right bottom" : "left bottom" }}>
            <Rich text={it.text} size={size} pg={pg} />
            {it.sub && <Rich text={it.sub} size={Math.round(size * 0.8)} pg={pg} color={c.inkSoft} weight={600} />}
            <div style={{ textAlign: "right", fontFamily: theme.fonts.body, fontWeight: 700, fontSize: 24, color: "#4FA3E0" }}>✓✓</div>
            <Sfx at={d[k]} name="pop" vol={0.35} />
          </div>
        );
      })}
      {typing && (
        <div style={{ alignSelf: shown % 2 ? "flex-end" : "flex-start", padding: "16px 26px", borderRadius: 30, background: c.white, border: `4px solid ${c.ink}`, display: "flex", gap: 10 }}>
          {[0, 1, 2].map((i) => <div key={i} style={{ width: 16, height: 16, borderRadius: 8, background: c.inkSoft, transform: `translateY(${Math.sin(f / 3 + i) * 5}px)` }} />)}
        </div>
      )}
    </div>
  );
};

const Wheel: React.FC<LP> = ({ s, pg, d, h }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const n = s.items.length;
  const idx = Math.max(0, d.filter((t) => f >= t).length - 1);
  let rot = 0;
  for (let k = 1; k < n; k++) rot += spring({ frame: f - d[k], fps, config: theme.spring.smooth }) * (360 / n);
  const R = Math.min(240, (h - 330) / 2 - 90);
  const item = s.items[idx];
  const cardP = spring({ frame: f - d[idx] - 4, fps, config: theme.spring.snappy });
  const bub = Math.min(190, R * 0.78);
  return (
    <div style={{ height: h, position: "relative" }}>
      <div style={{ position: "absolute", left: WIDTH / 2 - R - 90, top: 0, width: (R + 90) * 2, height: (R + 90) * 2, transform: `scale(${useSpring(4, "bouncy")}) rotate(${-rot}deg)` }}>
        <div style={{ position: "absolute", inset: 90, borderRadius: "50%", border: `6px dashed ${c.ink}44` }} />
        {s.items.map((it, k) => {
          const a = ((360 / n) * k - 90) * (Math.PI / 180);
          const active = k === idx && f >= d[0];
          return (
            <div key={k} style={{ position: "absolute", left: R + 90 + Math.cos(a) * R - bub / 2, top: R + 90 + Math.sin(a) * R - bub / 2, width: bub, height: bub, borderRadius: "50%", background: TINTS[k % TINTS.length], border: `${active ? 7 : 5}px solid ${c.ink}`, boxShadow: active ? `0 0 0 10px ${c.white}, 0 0 0 15px ${c.ink}` : "none", display: "flex", alignItems: "center", justifyContent: "center", transform: `rotate(${rot}deg) scale(${active ? 1.12 : 0.86})` }}>
              {it.icon ? <AnyIcon name={it.icon} size={bub * 0.68} /> : <div style={{ fontFamily: theme.fonts.display, fontWeight: 800, fontSize: bub * 0.4 }}>{k + 1}</div>}
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", left: WIDTH / 2 - 60, top: R + 90 - 60, width: 120, height: 120, borderRadius: "50%", background: c.white, border: `5px solid ${c.ink}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 60, color: c.ink }}>{f >= d[0] ? idx + 1 : ""}</div>
      {f >= d[0] && (
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 290, padding: "18px 30px", borderRadius: 36, background: c.white, border: `5px solid ${c.ink}`, boxShadow: `8px 10px 0 ${c.ink}`, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", opacity: Math.min(1, cardP * 1.5), transform: `translateY(${(1 - cardP) * 40}px) scale(${0.9 + 0.1 * cardP})` }}>
          <Rich text={item.text} size={fit(item.text, WIDTH - 80, item.sub ? 150 : 240, 66, 36)} pg={pg} weight={800} align="center" />
          {item.sub && <Rich text={item.sub} size={fit(item.sub, WIDTH - 80, 100, 46, 30)} pg={pg} color={c.inkSoft} align="center" />}
        </div>
      )}
      {d.map((t, k) => <Sfx key={k} at={t} name={k ? "whoosh" : "pop"} vol={0.3} />)}
    </div>
  );
};

const Flags: React.FC<LP> = (props) => {
  const f = useCurrentFrame();
  const light = f < 10 ? 2 : f < 20 ? 1 : 0;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div style={{ display: "flex", justifyContent: "center" }}>
        <div style={{ width: 210, height: 76, borderRadius: 38, background: c.ink, display: "flex", alignItems: "center", justifyContent: "space-around", padding: "0 10px" }}>
          {["#FF4D5E", "#FFC857", "#5CCB8F"].map((col, i) => <div key={i} style={{ width: 50, height: 50, borderRadius: 25, background: col, opacity: i === light ? 1 : 0.22, boxShadow: i === light ? `0 0 22px ${col}` : "none" }} />)}
        </div>
      </div>
      <Rows {...props} h={props.h - 100} s={{ ...props.s, tone: "alert" }} />
      <Sfx at={20} name="stamp" vol={0.35} />
    </div>
  );
};

const Steps: React.FC<LP> = ({ s, pg, d, h }) => {
  const f = useCurrentFrame();
  const n = s.items.length;
  const stepH = (h - 10) / n;
  const size = Math.min(...s.items.map((it) => fit(itemText(it), WIDTH - 150, stepH - 24, 54, 30)));
  const lineP = ease(f, [d[0], d[n - 1] + 10], [0, 1]);
  return (
    <div style={{ position: "relative", height: h }}>
      <div style={{ position: "absolute", left: 44, top: stepH / 2, width: 8, height: (n - 1) * stepH * lineP, background: c.ink, borderRadius: 4 }} />
      {s.items.map((it, k) => (
        <div key={k} style={{ position: "absolute", top: k * stepH, left: 0, right: 0, height: stepH, display: "flex", alignItems: "center", gap: 26 }}>
          <Pop delay={d[k]} cfg="bouncy" from={0.2}>
            <div style={{ width: 96, height: 96, borderRadius: 48, background: TINTS[k % TINTS.length], border: `5px solid ${c.ink}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 50, color: c.ink }}>{it.icon ? <AnyIcon name={it.icon} size={70} /> : k + 1}</div>
          </Pop>
          <Pop delay={d[k] + 4} cfg="smooth" rise={30} style={{ flex: 1 }}>
            <Rich text={it.text} size={size} pg={pg} />
            {it.sub && <Rich text={it.sub} size={Math.round(size * 0.78)} pg={pg} color={c.inkSoft} weight={600} />}
          </Pop>
          <Sfx at={d[k]} name="tick" vol={0.3} />
        </div>
      ))}
    </div>
  );
};

const Chips: React.FC<LP> = ({ s, pg, d, h }) => {
  const total = s.items.reduce((a, it) => a + it.text.length + 4, 0);
  const size = Math.max(40, Math.min(66, Math.sqrt((WIDTH * h * 0.5) / (total * 0.55))));
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 18, alignContent: "center", justifyContent: "center", height: h }}>
      {s.items.map((it, k) => (
        <Pop key={k} delay={d[k]} cfg="bouncy" from={0.4}>
          <div style={{ padding: "12px 26px 6px", borderRadius: 50, background: TINTS[k % TINTS.length], border: `4px solid ${c.ink}`, boxShadow: `4px 5px 0 ${c.ink}` }}>
            <Rich text={it.text} size={size} pg={pg} weight={800} />
          </div>
          <Sfx at={d[k]} name="tick" vol={0.28} />
        </Pop>
      ))}
    </div>
  );
};

const List: React.FC<{ s: Extract<Scene, { type: "list" }>; pg: boolean; seed: number; pace: number }> = ({ s, pg, seed, pace }) => {
  const d = delays(s.items.map(itemText), pace);
  const h = BOTTOM - TOP - titleH(s.title, pg) - 50;
  let style = s.style;
  if (!style) style = s.tone === "alert" ? "flags" : s.tone === "bad" && s.items.length <= 4 ? "notes" : "rows";
  if (style === "notes" && s.items.length > 4) style = "rows";
  if (style === "wheel" && (s.items.length > 6 || s.items.length < 3)) style = "rows";
  const props = { s, pg, seed, d, h };
  const body = style === "notes" ? <Notes {...props} /> : style === "chat" ? <Chat {...props} /> : style === "wheel" ? <Wheel {...props} /> : style === "flags" ? <Flags {...props} /> : style === "steps" ? <Steps {...props} /> : style === "chips" ? <Chips {...props} /> : <Rows {...props} />;
  return (
    <SceneExit>
      <Column gap={40}>
        <Title text={s.title} pg={pg} seed={seed} />
        <div style={{ position: "relative", flex: 1, display: "flex", flexDirection: "column", justifyContent: style === "wheel" || style === "steps" || style === "chips" ? "flex-start" : "center" }}>{body}</div>
      </Column>
      <Sfx at={0} name="pop" vol={0.3} />
    </SceneExit>
  );
};

/* ================================================================ CARDS (PG) */
const Cards: React.FC<{ s: Extract<Scene, { type: "cards" }>; pg: boolean; seed: number; pace: number }> = ({ s, pg, seed, pace }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const d = delays(s.cards.map((k) => `${k.title} ${k.lines.join(" ")}`), pace);
  const avail = BOTTOM - TOP - titleH(s.title, pg) - 60 - 24 * (s.cards.length - 1);
  const weight = s.cards.map((k) => 1.6 + k.lines.reduce((a, l) => a + Math.ceil(l.length / 30), 0));
  const sumW = weight.reduce((a, b) => a + b, 0);
  return (
    <SceneExit>
      <Column gap={40}>
        <Title text={s.title} pg={pg} seed={seed} />
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          {s.cards.map((k, i) => {
            const h = Math.min(560, (avail * weight[i]) / sumW);
            const body = h - 90;
            const size = Math.min(...k.lines.map((l) => fit(l, WIDTH - 60, body / k.lines.length - 10, 66, 30)));
            const p = spring({ frame: f - d[i], fps, config: theme.spring.smooth });
            return (
              <div key={i} style={{ height: h, display: "flex", flexDirection: "column", background: c.white, border: `4px solid ${c.ink}`, borderRadius: 22, overflow: "hidden", boxShadow: `6px 7px 0 ${c.ink}`, opacity: Math.min(1, p * 1.5), transform: seed % 2 ? `translateX(${(1 - p) * 90}px) rotate(${(1 - p) * 3}deg)` : `translateY(${(1 - p) * 80}px)` }}>
                <div style={{ background: TINTS[(i + seed) % TINTS.length], borderBottom: `4px solid ${c.ink}`, padding: "8px 22px 2px", fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 48, color: c.ink }}>{k.title}</div>
                <div style={{ flex: 1, padding: "12px 22px 12px", display: "flex", flexDirection: "column", justifyContent: "center", gap: 10 }}>
                  {k.lines.map((l, j) => <Rich key={j} text={l} size={size} pg={pg} />)}
                </div>
                <Sfx at={d[i]} name="pop" vol={0.3} />
              </div>
            );
          })}
        </div>
      </Column>
      <Sfx at={2} name="whoosh" vol={0.3} />
    </SceneExit>
  );
};

/* ================================================================ PEARLS */
const Pearls: React.FC<{ s: Extract<Scene, { type: "pearls" }>; pg: boolean; seed: number; pace: number }> = ({ s, pg, seed, pace }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const d = delays(s.items, pace);
  const n = s.items.length;
  const avail = BOTTOM - TOP - titleH(s.title, pg) - 80 - 46 * (n - 1);
  const size = Math.min(...s.items.map((t) => fit(t, WIDTH - 90, avail / n - 80, 66, 34)));
  return (
    <SceneExit>
      <Column gap={50}>
        <Title text={s.title} pg={pg} seed={seed} />
        <div style={{ display: "flex", flexDirection: "column", gap: 46, padding: "0 12px" }}>
          {s.items.map((t, k) => {
            const p = spring({ frame: f - d[k], fps, config: theme.spring.bouncy });
            return (
              <div key={k} style={{ position: "relative", padding: "40px 30px 30px", background: TINTS[(k + seed + 2) % TINTS.length], border: `4px solid ${c.ink}`, borderRadius: 8, transform: `rotate(${[-2, 1.5, -1, 2][k % 4]}deg) scale(${0.7 + 0.3 * p})`, opacity: Math.min(1, p * 2), boxShadow: `6px 8px 0 ${c.ink}22` }}>
                <div style={{ position: "absolute", top: -18, left: 40, width: 36, height: 36, borderRadius: 18, background: RED, border: `4px solid ${c.ink}` }} />
                <Rich text={t} size={size} pg={pg} />
                <Sfx at={d[k]} name="pop" vol={0.35} />
              </div>
            );
          })}
        </div>
      </Column>
      <Sfx at={2} name="sparkle" vol={0.3} />
    </SceneExit>
  );
};

/* ================================================================ dispatcher */
export const SceneView: React.FC<{ s: Scene; sc: Script; i: number }> = ({ s, sc, i }) => {
  const pg = sc.audience === "pg";
  const seed = (sc.seed ?? 0) + i;
  const pace = sc.pace ?? 1.0;
  const tab = pg && sc.tab ? <Tab text={sc.tab} /> : null;
  let el: React.ReactNode;
  switch (s.type) {
    case "hook": el = <Hook s={s} pg={pg} seed={seed} />; break;
    case "big": el = <Big s={s} pg={pg} />; break;
    case "split": el = <Split s={s} pg={pg} seed={seed} />; break;
    case "list": el = <List s={s} pg={pg} seed={seed} pace={pace} />; break;
    case "cards": el = <Cards s={s} pg={pg} seed={seed} pace={pace} />; break;
    case "pearls": el = <Pearls s={s} pg={pg} seed={seed} pace={pace} />; break;
    case "cta": el = <CTA line={s.line ?? (pg ? "Follow for the full *PG notes* series" : "Save this & share with *every parent*")} sub={s.sub ?? "Follow for more simple paeds"} />; break;
  }
  return <AbsoluteFill>{tab}{el}</AbsoluteFill>;
};
