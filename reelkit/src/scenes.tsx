import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "./theme";
import { Baby } from "./Baby";
import { Icon, IconName } from "./Icons";
import { Pop, SceneExit, Sfx, Words, breathe, ease, useSpring } from "./fx";

const c = theme.colors;
const INK_HI = c.ink; // highlighted words: ink on a lemon marker (red is saved for the hero)

const Center: React.FC<{ top: number; children: React.ReactNode; width?: number }> = ({ top, children, width = 900 }) => (
  <div style={{ position: "absolute", top, left: (1080 - width) / 2, width, display: "flex", flexDirection: "column", alignItems: "center" }}>{children}</div>
);

/* ------------------------------------------------------------- 1. HOOK */
export const Hook: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const babyIn = useSpring(0, "bouncy");
  const thermo = ease(f, [24, 70], [0, 1], theme.ease.inOut);
  const numP = spring({ frame: f - 40, fps, config: { damping: 30, stiffness: 60 } });
  const temp = interpolate(numP, [0, 1], [98.6, 100.4]);
  const land = useSpring(66, "bouncy");
  const shake = f > 66 && f < 80 ? Math.sin(f * 2.4) * (80 - f) * 0.7 : 0;
  const numIn = useSpring(36, "snappy");
  return (
    <SceneExit>
      <Center top={300}>
        <Words text="Your child has a *fever?*" size={128} hi={INK_HI} delay={4} per={4} />
      </Center>
      <div style={{ position: "absolute", top: 610, left: 0, right: 0, display: "flex", justifyContent: "center", transform: `scale(${interpolate(babyIn, [0, 1], [0.6, 1])}) rotate(${interpolate(babyIn, [0, 1], [-8, 0])}deg)`, opacity: Math.min(1, babyIn * 1.5) }}>
        <Baby mood="hot" size={500} thermo={thermo} />
      </div>
      <div style={{ position: "absolute", top: 1190, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div
          style={{
            fontFamily: theme.fonts.display,
            fontWeight: 800,
            fontSize: 190,
            lineHeight: 1,
            color: c.hero,
            fontVariantNumeric: "tabular-nums",
            textShadow: `0 0 50px ${c.hero}55, 0 8px 0 ${c.white}`,
            opacity: numIn,
            transform: `translateX(${shake}px) scale(${interpolate(numIn, [0, 1], [0.5, 1]) * (1 + 0.08 * Math.sin(Math.min(1, land) * Math.PI))})`,
          }}
        >
          {temp.toFixed(1)}°F
        </div>
        <Pop delay={74} cfg="snappy" rise={24}>
          <div style={{ marginTop: 18, padding: "14px 34px", borderRadius: 60, background: c.white, boxShadow: "0 10px 30px rgba(80,40,60,0.12)", fontFamily: theme.fonts.body, fontWeight: 800, fontSize: 50, color: c.ink }}>
            (38°C) or higher = <span style={{ color: c.ink, background: c.lemon, padding: "0 12px", borderRadius: 12 }}>FEVER</span>
          </div>
        </Pop>
      </div>
      <Sfx at={0} name="whoosh" vol={0.35} />
      <Sfx at={4} name="pop" vol={0.4} />
      <Sfx at={40} name="riser" vol={0.3} />
      <Sfx at={64} name="ding" vol={0.45} />
      <Sfx at={72} name="pop" vol={0.35} />
    </SceneExit>
  );
};

/* ------------------------------------------------------------- 2. KEY MESSAGE */
export const KeyMessage: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <SceneExit>
      <Center top={330}>
        <Pop delay={2} cfg="snappy">
          <div style={{ fontFamily: theme.fonts.body, fontWeight: 800, fontSize: 54, color: c.inkSoft, textAlign: "center", maxWidth: 800 }}>More important than the thermometer number</div>
        </Pop>
        <div style={{ height: 16 }} />
        <Words text="is *how* your child looks and acts" size={104} hi={INK_HI} delay={14} per={4} />
      </Center>
      <div style={{ position: "absolute", top: 900, left: 140, transform: `scale(${breathe(f, 0.03, 18)})` }}>
        <Pop delay={30} cfg="bouncy" from={0.4}>
          <Icon name="eye" size={330} />
        </Pop>
      </div>
      <div style={{ position: "absolute", top: 860, left: 520 }}>
        <Pop delay={40} cfg="bouncy" from={0.5}>
          <Baby mood="think" size={400} />
        </Pop>
      </div>
      <Sfx at={2} name="whoosh" vol={0.3} />
      <Sfx at={30} name="pop" vol={0.4} />
      <Sfx at={40} name="pop" vol={0.3} />
    </SceneExit>
  );
};

/* ------------------------------------------------------------- 3. ALERT TITLE */
export const Alert: React.FC = () => {
  const f = useCurrentFrame();
  const rings = [0, 1, 2].map((i) => ((f + i * 12) % 36) / 36);
  return (
    <SceneExit>
      <div style={{ position: "absolute", top: 380, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <div style={{ position: "relative", width: 360, height: 360, display: "flex", alignItems: "center", justifyContent: "center" }}>
          {rings.map((t, i) => (
            <div key={i} style={{ position: "absolute", width: 360, height: 360, borderRadius: "50%", border: `10px solid ${c.hero}`, opacity: (1 - t) * 0.5, transform: `scale(${0.5 + t * 0.9})` }} />
          ))}
          <Pop delay={0} cfg="bouncy" from={0.3}>
            <Icon name="siren" size={300} />
          </Pop>
        </div>
      </div>
      <Center top={830}>
        <Words text="See a *doctor* right away if…" size={112} hi={INK_HI} delay={8} per={4} />
      </Center>
      <Pop delay={34} cfg="snappy" style={{ position: "absolute", top: 1220, left: 0, right: 0, textAlign: "center" }}>
        <div style={{ fontFamily: theme.fonts.hand, fontWeight: 700, fontSize: 68, color: c.inkSoft }}>7 warning signs</div>
      </Pop>
      <Sfx at={0} name="stamp" vol={0.45} />
      <Sfx at={8} name="whoosh" vol={0.25} />
    </SceneExit>
  );
};

/* ------------------------------------------------------------- 4. RED FLAG CARD */
export type Flag = { icon: IconName; title: string; sub: string; color: string };

export const FLAGS: Flag[] = [
  { icon: "newborn", title: "Baby under *3 months* with fever", sub: "Even 100.4°F: see a doctor now", color: c.lemon },
  { icon: "lungs", title: "*Fast* or difficult breathing", sub: "Ribs pull in with each breath", color: c.sky },
  { icon: "sleep", title: "Very *drowsy*, hard to wake", sub: "Not playing or smiling", color: c.lavender },
  { icon: "bottle", title: "Not *feeding*, passing less urine", sub: "Very few wet diapers", color: c.mint },
  { icon: "rash", title: "Rash that *doesn't fade* under a glass", sub: "Glass test: spots still visible = emergency", color: c.pink },
  { icon: "bolt", title: "*Fits* (seizures) or stiff neck", sub: "Go straight to hospital", color: c.peach },
  { icon: "calendar", title: "Fever for more than *5 days*", sub: "Get your child checked by a doctor", color: c.lavender },
];

export const FlagCard: React.FC<{ i: number }> = ({ i }) => {
  const flag = FLAGS[i];
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const card = spring({ frame: f, fps, config: theme.spring.smooth });
  const badge = spring({ frame: f - 8, fps, config: theme.spring.bouncy });
  const icon = spring({ frame: f - 5, fps, config: theme.spring.bouncy });
  const idle = Math.sin(f / 20) * 4;
  return (
    <SceneExit len={8}>
      {/* progress dots */}
      <div style={{ position: "absolute", top: 300, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 18 }}>
        {FLAGS.map((_, k) => {
          const on = k <= i;
          const cur = k === i;
          const s = cur ? 1 + 0.25 * spring({ frame: f - 4, fps, config: theme.spring.bouncy }) : 1;
          return <div key={k} style={{ width: cur ? 54 : 22, height: 22, borderRadius: 11, background: on ? c.ink : `${c.ink}26`, transform: `scale(${s})`, transition: "none" }} />;
        })}
      </div>
      <div
        style={{
          position: "absolute",
          top: 400,
          left: 90,
          width: 900,
          height: 990,
          borderRadius: 56,
          background: c.white,
          border: `5px solid ${c.ink}`,
          boxShadow: `14px 16px 0 ${c.ink}`,
          opacity: Math.min(1, card * 1.5),
          transform: `translateY(${interpolate(card, [0, 1], [120, idle])}px) rotate(${interpolate(card, [0, 1], [i % 2 ? 4 : -4, i % 2 ? 0.6 : -0.6])}deg) scale(${interpolate(card, [0, 1], [0.9, 1])})`,
          overflow: "visible",
        }}
      >
        {/* coloured header with icon */}
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 470, borderRadius: "51px 51px 0 0", background: flag.color, borderBottom: `5px solid ${c.ink}`, overflow: "hidden" }}>
          <div style={{ position: "absolute", inset: 0, backgroundImage: `radial-gradient(${c.white}88 3px, transparent 3.5px)`, backgroundSize: "36px 36px" }} />
        </div>
        <div style={{ position: "absolute", top: 50, left: 0, right: 0, display: "flex", justifyContent: "center", opacity: Math.min(1, icon * 1.4), transform: `scale(${interpolate(icon, [0, 1], [0.3, 1]) * breathe(f, 0.025, 16)}) rotate(${interpolate(icon, [0, 1], [-25, 0])}deg)` }}>
          <Icon name={flag.icon} size={370} />
        </div>
        {/* number badge */}
        <div
          style={{
            position: "absolute",
            top: -46,
            left: -36,
            width: 150,
            height: 150,
            borderRadius: "50%",
            background: c.ink,
            color: c.white,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: theme.fonts.display,
            fontWeight: 800,
            fontSize: 96,
            paddingTop: 10,
            boxSizing: "border-box",
            border: `6px solid ${c.white}`,
            transform: `scale(${badge}) rotate(${interpolate(badge, [0, 1], [-180, -8])}deg)`,
          }}
        >
          {i + 1}
        </div>
        <div style={{ position: "absolute", top: 510, left: 50, right: 50 }}>
          <Words text={flag.title} size={flag.title.length > 29 ? 84 : 98} hi={INK_HI} delay={12} per={3} />
          <div style={{ height: 34 }} />
          <Pop delay={34} cfg="snappy" rise={20}>
            <div style={{ textAlign: "center", fontFamily: theme.fonts.body, fontWeight: 800, fontSize: 54, lineHeight: 1.22, color: c.inkSoft }}>{flag.sub}</div>
          </Pop>
        </div>
      </div>
      <Sfx at={0} name="whoosh" vol={0.22} />
      <Sfx at={5} name="pop" vol={0.4} />
      <Sfx at={10} name="tick" vol={0.4} />
    </SceneExit>
  );
};

/* ------------------------------------------------------------- 5/6. LIST CARDS */
export const Check: React.FC<{ delay: number }> = ({ delay }) => {
  const f = useCurrentFrame();
  const t = ease(f - delay, [0, 12], [0, 1]);
  const p = useSpring(delay, "bouncy");
  return (
    <svg width={86} height={86} viewBox="0 0 100 100" style={{ transform: `scale(${0.6 + 0.4 * p})`, opacity: Math.min(1, p * 2) }}>
      <circle cx={50} cy={50} r={44} fill={c.good} stroke={c.ink} strokeWidth={6} />
      <path d="M28 52 l15 15 l30 -32" stroke="#fff" strokeWidth={11} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={80} strokeDashoffset={80 * (1 - t)} />
    </svg>
  );
};

export const Cross: React.FC<{ delay: number }> = ({ delay }) => {
  const f = useCurrentFrame();
  const p = useSpring(delay, "snappy");
  const sl = interpolate(p, [0, 1], [2.4, 1]);
  return (
    <svg width={96} height={96} viewBox="0 0 100 100" style={{ transform: `scale(${sl}) rotate(${-12 + Math.sin(f / 20) * 2}deg)`, opacity: Math.min(1, p * 2) }}>
      <circle cx={50} cy={50} r={44} fill={c.hero} stroke={c.ink} strokeWidth={6} />
      <path d="M32 32 l36 36 M68 32 l-36 36" stroke="#fff" strokeWidth={12} strokeLinecap="round" />
    </svg>
  );
};

type Row = { icon: IconName; text: string };

const ListScene: React.FC<{ title: string; titleBg: string; rows: Row[]; good: boolean; start: number; step: number }> = ({ title, titleBg, rows, good, start, step }) => {
  const f = useCurrentFrame();
  return (
    <SceneExit>
      <Pop delay={0} cfg="bouncy" from={0.6} style={{ position: "absolute", top: 330, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <div style={{ padding: "18px 54px 12px", borderRadius: 80, background: titleBg, border: `5px solid ${c.ink}`, boxShadow: `8px 10px 0 ${c.ink}`, fontFamily: theme.fonts.display, fontWeight: 800, fontSize: 92, color: c.ink, transform: `rotate(${-2 + Math.sin(f / 25)}deg)` }}>{title}</div>
      </Pop>
      <div style={{ position: "absolute", top: good ? 590 : 640, left: 70, right: 70, display: "flex", flexDirection: "column", gap: good ? 44 : 70 }}>
        {rows.map((r, k) => {
          const d = start + k * step;
          return (
            <Pop key={k} delay={d} cfg="smooth" rise={60}>
              <div style={{ display: "flex", alignItems: "center", gap: 30, background: c.white, borderRadius: 44, border: `5px solid ${c.ink}`, boxShadow: `8px 10px 0 ${c.ink}`, padding: "22px 30px" }}>
                <div style={{ flex: "0 0 auto", width: 170, height: 170, borderRadius: 34, background: good ? c.goodSoft : c.heroSoft, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Icon name={r.icon} size={150} />
                </div>
                <div style={{ flex: 1, fontFamily: theme.fonts.display, fontWeight: 700, fontSize: 60, lineHeight: 1.1, color: c.ink }}>{r.text}</div>
                <div style={{ flex: "0 0 auto" }}>{good ? <Check delay={d + 10} /> : <Cross delay={d + 12} />}</div>
              </div>
              <Sfx at={d} name="whoosh" vol={0.2} />
              <Sfx at={d + (good ? 10 : 12)} name={good ? "ding" : "stamp"} vol={good ? 0.3 : 0.45} />
            </Pop>
          );
        })}
      </div>
      <Sfx at={0} name="pop" vol={0.4} />
    </SceneExit>
  );
};

export const HomeCare: React.FC = () => (
  <ListScene
    title="What to do at home"
    titleBg={c.mint}
    good
    start={12}
    step={18}
    rows={[
      { icon: "shirt", text: "Light, loose clothes" },
      { icon: "water", text: "Keep giving milk, water, ORS" },
      { icon: "syrup", text: "Paracetamol: only the dose your doctor advises" },
    ]}
  />
);

export const Donts: React.FC = () => (
  <ListScene
    title="Please don't"
    titleBg={c.heroSoft}
    good={false}
    start={12}
    step={22}
    rows={[
      { icon: "ice", text: "Sponging with cold water or ice" },
      { icon: "pill", text: "Aspirin for children: never" },
    ]}
  />
);

/* ------------------------------------------------------------- 7. CTA */
const Btn: React.FC<{ label: string; icon: "save" | "share"; delay: number; glow?: boolean }> = ({ label, icon, delay, glow }) => {
  const f = useCurrentFrame();
  const p = useSpring(delay, "bouncy");
  const tap = icon === "save" ? Math.max(0, Math.sin((f - delay - 30) / 5)) * (f > delay + 30 && f < delay + 46 ? 0.08 : 0) : 0;
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 16,
        padding: "20px 38px",
        borderRadius: 70,
        background: glow ? c.hero : c.white,
        color: glow ? c.white : c.ink,
        border: `5px solid ${c.ink}`,
        boxShadow: glow ? `8px 10px 0 ${c.ink}, 0 0 60px ${c.hero}66` : `8px 10px 0 ${c.ink}`,
        fontFamily: theme.fonts.display,
        fontWeight: 800,
        fontSize: 62,
        opacity: Math.min(1, p * 1.5),
        transform: `translateY(${(1 - p) * 60}px) scale(${(0.7 + 0.3 * p) * (1 - tap)})`,
      }}
    >
      <svg width={56} height={56} viewBox="0 0 24 24" fill="none" stroke={glow ? c.white : c.ink} strokeWidth={2.6} strokeLinejoin="round" strokeLinecap="round">
        {icon === "save" ? <path d="M6 3h12v18l-6-4.5L6 21z" fill={glow ? c.white : "none"} /> : <path d="M22 3L10 14M22 3l-7 19-4-8-8-4z" />}
      </svg>
      {label}
    </div>
  );
};

export const CTA: React.FC<{ line?: string; sub?: string; extra?: React.ReactNode }> = ({ line = "Share with *every parent* you know", sub = "Follow for more simple paeds", extra }) => {
  const f = useCurrentFrame();
  const heart = useSpring(48, "bouncy");
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", top: 300, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <Pop delay={0} cfg="bouncy" from={0.5}>
          <Baby mood="doctor" size={420} wave />
        </Pop>
      </div>
      <Center top={830}>
        <Words text={line} size={92} hi={INK_HI} delay={10} per={4} />
      </Center>
      <div style={{ position: "absolute", top: 1100, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 34 }}>
        <Btn label="Save" icon="save" delay={30} glow />
        <Btn label="Share" icon="share" delay={36} />
      </div>
      <div style={{ position: "absolute", top: 1290, left: 0, right: 0, display: "flex", justifyContent: "center", alignItems: "center", gap: 14, opacity: Math.min(1, heart * 1.4), transform: `scale(${0.6 + 0.4 * heart})` }}>
        <svg width={56} height={56} viewBox="0 0 40 40" style={{ transform: `scale(${breathe(f, 0.12, 5)})` }}>
          <path d="M20 36 C4 24 2 14 8 8 C13 3 19 6 20 11 C21 6 27 3 32 8 C38 14 36 24 20 36 Z" fill="#FF7FA6" stroke={c.ink} strokeWidth={2.5} />
        </svg>
        <div style={{ fontFamily: theme.fonts.hand, fontWeight: 700, fontSize: 64, color: c.ink }}>{sub}</div>
      </div>
      {extra}
      <Sfx at={0} name="sparkle" vol={0.35} />
      <Sfx at={30} name="pop" vol={0.4} />
      <Sfx at={36} name="pop" vol={0.35} />
      <Sfx at={48} name="ding" vol={0.3} />
    </AbsoluteFill>
  );
};
