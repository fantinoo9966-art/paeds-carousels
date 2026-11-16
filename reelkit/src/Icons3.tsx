import React from "react";
import { useCurrentFrame } from "remotion";
import { theme } from "./theme";

export type Icon3Name = "germ" | "nosedrop" | "honey" | "cup" | "kettle" | "rubjar" | "heart";

const K = theme.colors.ink;
const SW = 4.5;

/** Cute germ with spikes and eyes (any colour). */
export const Germ: React.FC<{ size?: number; color?: string; seed?: number }> = ({ size = 120, color = "#8FD98A", seed = 0 }) => {
  const f = useCurrentFrame();
  const wob = Math.sin(f / 6 + seed) * 6;
  const spikes = 9;
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" style={{ overflow: "visible" }}>
      <g transform={`rotate(${wob + seed * 20} 50 50)`}>
        {Array.from({ length: spikes }).map((_, i) => (
          <g key={i} transform={`rotate(${(360 / spikes) * i} 50 50)`}>
            <path d="M50 18 v-10" stroke={K} strokeWidth={4} strokeLinecap="round" />
            <circle cx={50} cy={7} r={5} fill={color} stroke={K} strokeWidth={3} />
          </g>
        ))}
        <circle cx={50} cy={50} r={32} fill={color} stroke={K} strokeWidth={SW} />
        <circle cx={40} cy={44} r={6} fill="#fff" stroke={K} strokeWidth={2.5} />
        <circle cx={60} cy={44} r={6} fill="#fff" stroke={K} strokeWidth={2.5} />
        <circle cx={41} cy={45} r={2.8} fill={K} />
        <circle cx={61} cy={45} r={2.8} fill={K} />
        <path d="M40 60 q10 8 20 0" stroke={K} strokeWidth={3.5} fill="none" strokeLinecap="round" />
      </g>
    </svg>
  );
};

export const Icon3: React.FC<{ name: Icon3Name; size?: number }> = ({ name, size = 200 }) => {
  const f = useCurrentFrame();
  const c = theme.colors;
  const wob = (s = 18, a = 4) => Math.sin(f / s) * a;
  let g: React.ReactNode = null;
  switch (name) {
    case "germ":
      return <Germ size={size} />;
    case "nosedrop": {
      const t = (f % 30) / 30;
      g = (
        <g transform={`rotate(${-25 + wob(20, 4)} 50 50)`}>
          <path d="M42 8 h16 v18 h-16 z" fill={c.pink} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M38 26 h24 v40 q0 6 -6 10 l-6 14 l-6 -14 q-6 -4 -6 -10 z" fill="#fff" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <rect x={42} y={46} width={16} height={20} rx={3} fill={c.sky} />
          <path d={`M50 ${92 + t * 14} q5 7 0 11 q-5 -4 0 -11 z`} fill="#9FD3FF" stroke={K} strokeWidth={2} opacity={1 - t} />
        </g>
      );
      break;
    }
    case "honey": {
      const drip = 6 + Math.abs(Math.sin(f / 14)) * 12;
      g = (
        <g>
          <rect x={26} y={16} width={48} height={12} rx={4} fill={c.peach} stroke={K} strokeWidth={SW} />
          <path d="M22 28 h56 q6 0 6 8 v42 q0 10 -10 10 h-48 q-10 0 -10 -10 v-42 q0 -8 6 -8 z" fill="#F7B733" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d={`M22 40 q8 6 14 0 v${drip} a4 4 0 0 0 8 0 v${-drip} q10 6 18 0 q6 6 16 0`} fill="#FFD36E" stroke={K} strokeWidth={3} strokeLinejoin="round" />
          <rect x={34} y={56} width={32} height={20} rx={5} fill="#fff" stroke={K} strokeWidth={3} />
          <path d="M42 66 h16" stroke={K} strokeWidth={3} strokeLinecap="round" />
        </g>
      );
      break;
    }
    case "cup":
      g = (
        <g>
          {[0, 1, 2].map((i) => (
            <path key={i} d={`M${34 + i * 14} ${26 + wob(8 + i, 3)} q5 -8 0 -16`} stroke={c.inkSoft} strokeWidth={4} fill="none" strokeLinecap="round" opacity={0.5 + 0.5 * Math.sin(f / 7 + i)} />
          ))}
          <path d="M20 36 h56 v30 q0 20 -28 20 q-28 0 -28 -20 z" fill={c.pink} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M76 44 q16 0 14 14 q-2 12 -16 10" stroke={K} strokeWidth={SW} fill="none" />
          <path d="M34 52 q14 8 28 0" stroke="#fff" strokeWidth={4} fill="none" strokeLinecap="round" />
        </g>
      );
      break;
    case "kettle":
      g = (
        <g>
          {[0, 1].map((i) => {
            const t = ((f + i * 12) % 24) / 24;
            return <circle key={i} cx={84 + t * 8} cy={30 - t * 20} r={5 + t * 6} fill="#E6EEF5" stroke={K} strokeWidth={2} opacity={1 - t} />;
          })}
          <path d="M18 80 q-2 -40 32 -42 q34 2 32 42 z" fill={c.sky} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M80 56 l12 -16" stroke={K} strokeWidth={8} strokeLinecap="round" />
          <path d="M36 38 q14 -22 28 0" stroke={K} strokeWidth={SW} fill="none" />
          <rect x={12} y={78} width={76} height={8} rx={4} fill={c.lavender} stroke={K} strokeWidth={3.5} />
        </g>
      );
      break;
    case "rubjar":
      g = (
        <g transform={`rotate(${wob(16, 4)} 50 60)`}>
          <rect x={22} y={24} width={56} height={14} rx={5} fill={c.mint} stroke={K} strokeWidth={SW} />
          <rect x={18} y={38} width={64} height={46} rx={10} fill="#fff" stroke={K} strokeWidth={SW} />
          <path d="M30 56 h40 M30 68 h28" stroke={c.good} strokeWidth={5} strokeLinecap="round" />
        </g>
      );
      break;
    case "heart": {
      const beat = 1 + Math.max(0, Math.sin(f / 3)) * 0.12;
      g = (
        <path d="M50 88 C12 62 6 36 20 22 C32 10 46 16 50 28 C54 16 68 10 80 22 C94 36 88 62 50 88 Z" fill={theme.colors.hero} stroke={K} strokeWidth={SW} transform={`translate(50 50) scale(${beat}) translate(-50 -50)`} />
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
