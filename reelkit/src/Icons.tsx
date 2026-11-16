import React from "react";
import { useCurrentFrame } from "remotion";
import { theme } from "./theme";

export type IconName =
  | "newborn" | "lungs" | "sleep" | "bottle" | "rash" | "bolt" | "calendar"
  | "shirt" | "water" | "syrup" | "ice" | "pill" | "siren" | "eye";

const K = theme.colors.ink;
const SW = 4.5;

/** Chunky outlined pastel icons, each with its own idle motion. 100x100 viewBox. */
export const Icon: React.FC<{ name: IconName; size?: number }> = ({ name, size = 200 }) => {
  const f = useCurrentFrame();
  const c = theme.colors;
  let g: React.ReactNode = null;
  switch (name) {
    case "newborn": {
      const rock = Math.sin(f / 10) * 6;
      g = (
        <g transform={`rotate(${rock} 50 60)`}>
          <path d="M22 50 q28 -14 56 0 q6 30 -28 40 q-34 -10 -28 -40 z" fill={c.sky} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M30 56 q20 10 40 0" stroke={K} strokeWidth={3} fill="none" />
          <circle cx={50} cy={38} r={18} fill={c.skin} stroke={K} strokeWidth={SW} />
          <path d="M43 38 q3 3 6 0 M52 38 q3 3 6 0" stroke={K} strokeWidth={3} fill="none" strokeLinecap="round" />
          <circle cx={42} cy={44} r={3.5} fill={c.cheek} />
          <circle cx={59} cy={44} r={3.5} fill={c.cheek} />
        </g>
      );
      break;
    }
    case "lungs": {
      const s = 1 + Math.sin(f / 3) * 0.06; // fast breathing
      g = (
        <g>
          <g transform={`translate(50 55) scale(${s}) translate(-50 -55)`}>
            <path d="M46 30 q-26 4 -30 40 q0 16 14 14 q16 -2 16 -20 z" fill={c.pink} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
            <path d="M54 30 q26 4 30 40 q0 16 -14 14 q-16 -2 -16 -20 z" fill={c.pink} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          </g>
          <path d="M50 12 v26 M50 34 q-6 6 -10 10 M50 34 q6 6 10 10" stroke={K} strokeWidth={SW} fill="none" strokeLinecap="round" />
          {[0, 1].map((i) => (
            <path key={i} d="M88 30 q6 6 0 12" stroke={theme.colors.hero} strokeWidth={4} fill="none" strokeLinecap="round" opacity={0.4 + 0.6 * Math.abs(Math.sin(f / 4 + i))} transform={`translate(${i * 6} ${i * 14 - 4})`} />
          ))}
        </g>
      );
      break;
    }
    case "sleep": {
      const z = (f % 40) / 40;
      g = (
        <g>
          <path d="M60 20 a32 32 0 1 0 22 52 a26 26 0 1 1 -22 -52 z" fill={c.lemon} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M40 58 q5 4 10 0" stroke={K} strokeWidth={3.5} fill="none" strokeLinecap="round" />
          <text x={70 + z * 10} y={36 - z * 20} fontFamily={theme.fonts.display} fontWeight={800} fontSize={22} fill="#8B7CFF" opacity={Math.sin(z * Math.PI)}>z</text>
          <text x={80 + z * 8} y={22 - z * 14} fontFamily={theme.fonts.display} fontWeight={800} fontSize={16} fill="#8B7CFF" opacity={Math.sin(z * Math.PI)}>z</text>
        </g>
      );
      break;
    }
    case "bottle": {
      const tip = Math.sin(f / 18) * 5;
      g = (
        <g transform={`rotate(${tip} 50 55)`}>
          <path d="M40 14 h20 l4 12 h-28 z" fill={c.peach} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <rect x={30} y={26} width={40} height={10} rx={4} fill={c.lavender} stroke={K} strokeWidth={SW} />
          <rect x={30} y={36} width={40} height={52} rx={10} fill="#fff" stroke={K} strokeWidth={SW} />
          <rect x={34} y={68} width={32} height={16} rx={6} fill={c.sky} />
          <path d="M36 50 h10 M36 60 h10" stroke={K} strokeWidth={3} />
          <circle cx={78} cy={78} r={15} fill={theme.colors.hero} stroke={K} strokeWidth={SW} />
          <path d="M71 78 h14" stroke="#fff" strokeWidth={5} strokeLinecap="round" />
        </g>
      );
      break;
    }
    case "rash": {
      const press = Math.max(0, Math.sin(f / 12)) * 6;
      g = (
        <g>
          <ellipse cx={50} cy={66} rx={40} ry={22} fill={c.skin} stroke={K} strokeWidth={SW} />
          {[[30, 62], [44, 72], [58, 60], [66, 74], [40, 56], [72, 64], [52, 66]].map(([x, y], i) => (
            <circle key={i} cx={x} cy={y} r={4} fill="#D81B3C" />
          ))}
          <g transform={`translate(0 ${press - 6})`}>
            <path d="M32 18 h36 l-4 44 h-28 z" fill="rgba(191,227,255,0.55)" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
            <path d="M40 26 v26" stroke="#fff" strokeWidth={4} strokeLinecap="round" />
          </g>
        </g>
      );
      break;
    }
    case "bolt": {
      const j = Math.sin(f * 1.7) * 2;
      g = (
        <g transform={`translate(${j} 0)`}>
          <path d="M58 8 L24 56 h22 l-8 36 l38 -52 h-22 z" fill={c.lemon} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M16 30 l-8 -4 M14 46 h-9 M84 64 l9 3 M86 48 h9" stroke={K} strokeWidth={4} strokeLinecap="round" opacity={0.5 + 0.5 * Math.sin(f / 3)} />
        </g>
      );
      break;
    }
    case "calendar": {
      const flip = Math.sin(f / 16) * 3;
      g = (
        <g>
          <rect x={14} y={20} width={72} height={66} rx={10} fill="#fff" stroke={K} strokeWidth={SW} />
          <path d="M14 30 a10 10 0 0 1 10 -10 h52 a10 10 0 0 1 10 10 v10 h-72 z" fill={c.peach} stroke={K} strokeWidth={SW} />
          <path d="M32 12 v14 M68 12 v14" stroke={K} strokeWidth={5} strokeLinecap="round" />
          <text x={50} y={78 + flip * 0} textAnchor="middle" fontFamily={theme.fonts.display} fontWeight={800} fontSize={34} fill={K} transform={`rotate(${flip} 50 66)`}>5+</text>
        </g>
      );
      break;
    }
    case "shirt": {
      const sway = Math.sin(f / 16) * 4;
      g = (
        <g transform={`rotate(${sway} 50 20)`}>
          <path d="M34 16 l-22 12 l8 18 l10 -4 v42 h40 v-42 l10 4 l8 -18 l-22 -12 q-16 12 -32 0 z" fill={c.mint} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M30 60 q20 6 40 0" stroke="#fff" strokeWidth={4} fill="none" strokeLinecap="round" />
        </g>
      );
      break;
    }
    case "water": {
      const lvl = 4 * Math.sin(f / 10);
      g = (
        <g>
          <path d="M24 18 h52 l-7 70 h-38 z" fill="#fff" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d={`M27 ${44 + lvl} q12 -6 23 0 q11 6 23 0 l-5 41 h-36 z`} fill={c.sky} />
          <path d="M24 18 h52 l-7 70 h-38 z" fill="none" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <text x={50} y={74} textAnchor="middle" fontFamily={theme.fonts.display} fontWeight={800} fontSize={15} fill={K}>ORS</text>
        </g>
      );
      break;
    }
    case "syrup": {
      const t = Math.sin(f / 14) * 4;
      g = (
        <g transform={`rotate(${t} 50 60)`}>
          <rect x={38} y={10} width={24} height={14} rx={3} fill={c.lavender} stroke={K} strokeWidth={SW} />
          <path d="M34 24 h32 q8 8 8 20 v38 q0 8 -8 8 h-32 q-8 0 -8 -8 v-38 q0 -12 8 -20 z" fill={c.peach} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <rect x={30} y={48} width={40} height={24} rx={4} fill="#fff" stroke={K} strokeWidth={3} />
          <path d="M44 60 h12 M50 54 v12" stroke={theme.colors.hero} strokeWidth={4} strokeLinecap="round" />
        </g>
      );
      break;
    }
    case "ice": {
      const sh = Math.sin(f / 5) * 2;
      g = (
        <g transform={`translate(${sh} 0)`}>
          <path d="M22 38 l28 -14 l28 14 v34 l-28 14 l-28 -14 z" fill={c.sky} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M22 38 l28 14 l28 -14 M50 52 v34" stroke={K} strokeWidth={SW} fill="none" strokeLinejoin="round" />
          <path d="M30 46 l10 5" stroke="#fff" strokeWidth={4} strokeLinecap="round" />
        </g>
      );
      break;
    }
    case "pill": {
      const r = Math.sin(f / 15) * 10 - 30;
      g = (
        <g transform={`rotate(${r} 50 50)`}>
          <rect x={14} y={36} width={72} height={28} rx={14} fill="#fff" stroke={K} strokeWidth={SW} />
          <path d="M50 36 h22 a14 14 0 0 1 0 28 h-22 z" fill={c.pink} stroke={K} strokeWidth={SW} />
        </g>
      );
      break;
    }
    case "siren": {
      const on = Math.sin(f / 3) > 0;
      g = (
        <g>
          {[0, 1, 2].map((i) => (
            <path key={i} d="M50 30 l0 -16" stroke={theme.colors.hero} strokeWidth={5} strokeLinecap="round" transform={`rotate(${(i - 1) * 45} 50 52)`} opacity={on ? 1 : 0.3} />
          ))}
          <path d="M28 76 v-20 a22 22 0 0 1 44 0 v20 z" fill={on ? theme.colors.hero : "#FF8F9A"} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M40 58 a10 10 0 0 1 10 -10" stroke="#fff" strokeWidth={5} fill="none" strokeLinecap="round" />
          <rect x={20} y={76} width={60} height={12} rx={4} fill={c.lavender} stroke={K} strokeWidth={SW} />
        </g>
      );
      break;
    }
    case "eye": {
      const look = Math.sin(f / 20) * 8;
      g = (
        <g>
          <path d="M8 50 q42 -44 84 0 q-42 44 -84 0 z" fill="#fff" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <circle cx={50 + look} cy={50} r={16} fill="#6B8BFF" stroke={K} strokeWidth={SW} />
          <circle cx={50 + look} cy={50} r={7} fill={K} />
          <circle cx={55 + look} cy={45} r={3.5} fill="#fff" />
        </g>
      );
      break;
    }
  }
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" style={{ overflow: "visible" }}>
      {g}
    </svg>
  );
};
