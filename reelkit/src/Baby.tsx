import React from "react";
import { useCurrentFrame } from "remotion";
import { theme } from "./theme";

export type Mood = "hot" | "sleepy" | "happy" | "think" | "doctor" | "ouch" | "sneeze" | "queasy";

/**
 * Original cartoon baby (pink bow, round face) drawn in SVG.
 * Idle life: bob, blinks, cheek pulse; mood-specific props.
 */
export const Baby: React.FC<{ mood: Mood; size?: number; thermo?: number; wave?: boolean; skin?: string }> = ({ mood, size = 520, thermo = 0, wave = false, skin }) => {
  const f = useCurrentFrame();
  const c = { ...theme.colors, ...(skin ? { skin } : {}) };
  const bob = Math.sin(f / 14) * (mood === "sleepy" ? 2 : 5);
  const tilt = mood === "sleepy" ? -8 + Math.sin(f / 30) * 3 : mood === "think" ? 6 : Math.sin(f / 26) * 2.5;
  // blink every ~2.7s (not when sleeping)
  const bl = f % 80;
  const blink = mood !== "sleepy" && bl > 74 ? Math.abs(77 - bl) / 3 : 1;
  const hot = mood === "hot";
  const cheekPulse = hot ? 1 + Math.sin(f / 6) * 0.08 : 1;
  const armRot = wave ? Math.sin(f / 4.5) * 22 - 10 : 0;

  const eyes = () => {
    if (mood === "sleepy")
      return (
        <g stroke={c.ink} strokeWidth={9} strokeLinecap="round" fill="none">
          <path d="M128 212 q22 16 44 0" />
          <path d="M228 212 q22 16 44 0" />
        </g>
      );
    if (mood === "ouch" || mood === "sneeze")
      return (
        <g stroke={c.ink} strokeWidth={8} strokeLinecap="round" strokeLinejoin="round" fill="none">
          <path d="M132 192 l26 14 l-26 14" />
          <path d="M268 192 l-26 14 l26 14" />
          <path d="M128 172 q18 -2 40 -16" strokeWidth={6} />
          <path d="M272 172 q-18 -2 -40 -16" strokeWidth={6} />
        </g>
      );
    if (hot || mood === "queasy")
      return (
        <g>
          {/* tired half-closed eyes */}
          <path d="M130 206 a20 18 0 0 0 40 0 z" fill={c.ink} />
          <path d="M230 206 a20 18 0 0 0 40 0 z" fill={c.ink} />
          <path d="M126 206 h48 M226 206 h48" stroke={c.ink} strokeWidth={7} strokeLinecap="round" />
          <circle cx={157} cy={213} r={4} fill="#fff" />
          <circle cx={257} cy={213} r={4} fill="#fff" />
          {/* worried brows (raised in the middle) */}
          <path d="M128 176 q18 -2 40 -16" stroke={c.ink} strokeWidth={6} fill="none" strokeLinecap="round" />
          <path d="M272 176 q-18 -2 -40 -16" stroke={c.ink} strokeWidth={6} fill="none" strokeLinecap="round" />
        </g>
      );
    return (
      <g>
        <ellipse cx={150} cy={205} rx={20} ry={24 * blink} fill={c.ink} />
        <ellipse cx={250} cy={205} rx={20} ry={24 * blink} fill={c.ink} />
        <circle cx={158} cy={196} r={7 * blink} fill="#fff" />
        <circle cx={258} cy={196} r={7 * blink} fill="#fff" />
        <circle cx={145} cy={214} r={3 * blink} fill="#fff" />
        <circle cx={245} cy={214} r={3 * blink} fill="#fff" />
      </g>
    );
  };

  const mouth = () => {
    if (hot) return <path d="M178 268 q22 -14 44 0" stroke={c.ink} strokeWidth={8} fill="none" strokeLinecap="round" />;
    if (mood === "sneeze") return <g><ellipse cx={200} cy={274} rx={26} ry={22} fill="#C2475A" stroke={c.ink} strokeWidth={7} /><ellipse cx={200} cy={243} rx={16} ry={11} fill="#FF7A8A" /></g>;
    if (mood === "queasy") return <path d={`M168 ${270 + Math.sin(f / 5) * 3} q8 -9 16 0 q8 9 16 0 q8 -9 16 0 q8 9 16 0`} stroke={c.ink} strokeWidth={7} fill="none" strokeLinecap="round" />;
    if (mood === "ouch") return <path d="M170 270 q8 -10 15 0 q8 10 15 0 q8 -10 15 0 q8 10 15 0" stroke={c.ink} strokeWidth={7} fill="none" strokeLinecap="round" />;
    if (mood === "sleepy") return <ellipse cx={200} cy={266} rx={12} ry={9} fill="#C2475A" />;
    if (mood === "think") return <path d="M182 266 q18 6 36 -4" stroke={c.ink} strokeWidth={8} fill="none" strokeLinecap="round" />;
    return (
      <g>
        <path d="M168 252 q32 44 64 0 z" fill="#C2475A" stroke={c.ink} strokeWidth={7} strokeLinejoin="round" />
        <ellipse cx={200} cy={274} rx={14} ry={7} fill="#FF8FA0" />
      </g>
    );
  };

  return (
    <svg width={size} height={size * 1.15} viewBox="0 0 400 460" style={{ overflow: "visible" }}>
      <g transform={`translate(0 ${bob})`}>
        {/* body / onesie */}
        <g>
          <path d="M120 330 q80 -40 160 0 l18 110 q-98 30 -196 0 z" fill={mood === "doctor" ? "#FFFFFF" : c.sky} stroke={c.ink} strokeWidth={7} strokeLinejoin="round" />
          {mood === "doctor" ? (
            <g>
              <path d="M200 312 l0 130" stroke={c.ink} strokeWidth={5} />
              <path d="M150 320 q-10 60 30 80 q20 10 20 -10" stroke="#5B6CFF" strokeWidth={8} fill="none" strokeLinecap="round" />
              <circle cx={200} cy={392} r={14} fill="#5B6CFF" stroke={c.ink} strokeWidth={5} />
              <path d="M236 360 h28 v20 h-28 z" fill={c.pink} stroke={c.ink} strokeWidth={4} />
            </g>
          ) : mood === "ouch" ? (
            <g>
              <path d={`M200 ${392 + Math.sin(f / 5) * 2} m-26 0 a26 26 0 1 1 52 0 a18 18 0 1 1 -36 0 a10 10 0 1 1 20 0`} stroke="#8B7CFF" strokeWidth={6} fill="none" strokeLinecap="round" transform={`rotate(${f * 6} 200 392)`} />
            </g>
          ) : (
            <g>
              <circle cx={200} cy={372} r={10} fill="#fff" stroke={c.ink} strokeWidth={4} />
              <circle cx={200} cy={406} r={10} fill="#fff" stroke={c.ink} strokeWidth={4} />
            </g>
          )}
          {/* left arm */}
          <path d="M126 346 q-40 30 -34 66" stroke={c.ink} strokeWidth={30} strokeLinecap="round" fill="none" />
          <path d="M126 346 q-40 30 -34 66" stroke={mood === "doctor" ? "#fff" : c.sky} strokeWidth={17} strokeLinecap="round" fill="none" />
          <circle cx={92} cy={414} r={17} fill={c.skin} stroke={c.ink} strokeWidth={6} />
          {/* right arm (waves) */}
          <g transform={`rotate(${wave ? -150 + armRot : 0} 274 346)`}>
            <path d="M274 346 q40 30 34 66" stroke={c.ink} strokeWidth={30} strokeLinecap="round" fill="none" />
            <path d="M274 346 q40 30 34 66" stroke={mood === "doctor" ? "#fff" : c.sky} strokeWidth={17} strokeLinecap="round" fill="none" />
            <circle cx={308} cy={414} r={17} fill={c.skin} stroke={c.ink} strokeWidth={6} />
          </g>
        </g>

        <g transform={`rotate(${tilt} 200 220)`}>
          {/* ears */}
          <circle cx={58} cy={222} r={30} fill={c.skin} stroke={c.ink} strokeWidth={7} />
          <circle cx={342} cy={222} r={30} fill={c.skin} stroke={c.ink} strokeWidth={7} />
          {/* head */}
          <ellipse cx={200} cy={210} rx={150} ry={140} fill={c.skin} stroke={c.ink} strokeWidth={8} />
          {/* hair curl */}
          <path d="M186 74 q-6 -36 26 -34 q22 2 12 22 q-8 14 -20 4" stroke={c.ink} strokeWidth={8} fill="none" strokeLinecap="round" />
          {/* bow */}
          <g transform="translate(110 92) rotate(-18)">
            <path d="M0 0 l-46 -28 q-10 28 0 56 z" fill={c.pink} stroke={c.ink} strokeWidth={6} strokeLinejoin="round" />
            <path d="M0 0 l46 -28 q10 28 0 56 z" fill={c.pink} stroke={c.ink} strokeWidth={6} strokeLinejoin="round" />
            <circle cx={0} cy={0} r={13} fill="#FF7FA6" stroke={c.ink} strokeWidth={6} />
          </g>
          {/* cheeks */}
          <ellipse cx={112} cy={252} rx={30 * cheekPulse} ry={20 * cheekPulse} fill={hot ? "#FF6B7D" : mood === "queasy" ? "#9BD67E" : c.cheek} opacity={hot ? 0.75 : 0.55} />
          <ellipse cx={288} cy={252} rx={30 * cheekPulse} ry={20 * cheekPulse} fill={hot ? "#FF6B7D" : mood === "queasy" ? "#9BD67E" : c.cheek} opacity={hot ? 0.75 : 0.55} />
          {eyes()}
          {mouth()}
          {/* thermometer in mouth */}
          {hot && thermo > 0 && (
            <g transform="translate(214 262) rotate(-28)">
              <rect x={0} y={-10} width={130} height={20} rx={10} fill="#fff" stroke={c.ink} strokeWidth={5} />
              <rect x={8} y={-4} width={8 + 104 * thermo} height={8} rx={4} fill={theme.colors.hero} />
              <circle cx={8} cy={0} r={12} fill={theme.colors.hero} stroke={c.ink} strokeWidth={5} />
            </g>
          )}
          {/* sweat drops */}
          {hot && (
            <g>
              {[0, 1].map((i) => {
                const t = ((f + i * 22) % 44) / 44;
                return <path key={i} d="M0 0 q10 16 0 24 q-10 -8 0 -24 z" transform={`translate(${i ? 330 : 82} ${120 + t * 60}) scale(1.6)`} fill="#7CC8FF" stroke={c.ink} strokeWidth={2.5} opacity={1 - t} />;
              })}
            </g>
          )}
        </g>
        {/* heat waves */}
        {hot &&
          [0, 1, 2].map((i) => (
            <path
              key={i}
              d="M0 0 q12 -14 0 -28 q-12 -14 0 -28"
              stroke={theme.colors.hero}
              strokeWidth={7}
              fill="none"
              strokeLinecap="round"
              opacity={0.35 + 0.35 * Math.sin(f / 7 + i)}
              transform={`translate(${150 + i * 50} ${44 - Math.sin(f / 9 + i) * 8})`}
            />
          ))}
        {/* queasy swirls */}
        {mood === "queasy" &&
          [0, 1].map((i) => (
            <path key={i} d="M0 0 m-16 0 a16 16 0 1 1 32 0 a11 11 0 1 1 -22 0 a6 6 0 1 1 12 0" stroke="#6CC36A" strokeWidth={6} fill="none" strokeLinecap="round"
              transform={`translate(${i ? 352 : 48} ${80 + Math.sin(f / 9 + i) * 8}) rotate(${f * 7 * (i ? -1 : 1)})`} opacity={0.85} />
          ))}
        {/* zzz */}
        {mood === "sleepy" &&
          [0, 1, 2].map((i) => {
            const t = ((f + i * 18) % 54) / 54;
            return (
              <text key={i} x={320 + t * 40} y={110 - t * 90} fontFamily={theme.fonts.display} fontWeight={800} fontSize={40 + i * 6} fill="#8B7CFF" opacity={Math.sin(t * Math.PI)}>
                z
              </text>
            );
          })}
        {/* think bubble dots */}
        {mood === "think" &&
          [0, 1, 2].map((i) => <circle key={i} cx={330 + i * 26} cy={90 - i * 30} r={8 + i * 5} fill="#fff" stroke={c.ink} strokeWidth={4} opacity={0.5 + 0.5 * Math.sin(f / 8 - i)} />)}
      </g>
    </svg>
  );
};
