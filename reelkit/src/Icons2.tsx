import React from "react";
import { useCurrentFrame } from "remotion";
import { theme } from "./theme";

export type Icon2Name =
  | "packet" | "drop" | "lips" | "tear" | "urine" | "sunken" | "zinc" | "breast" | "bowl" | "soda" | "blood"
  | "noglass" | "clock" | "cal" | "lamp" | "tube" | "bulb" | "warn" | "stool" | "camera" | "liver" | "dna" | "shield";

const K = theme.colors.ink;
const SW = 4.5;

/** Second icon set (100x100 viewBox), same chunky outlined pastel style with idle motion. */
export const Icon2: React.FC<{ name: Icon2Name; size?: number; label?: string }> = ({ name, size = 200, label }) => {
  const f = useCurrentFrame();
  const c = theme.colors;
  const wob = (s = 18, a = 4) => Math.sin(f / s) * a;
  let g: React.ReactNode = null;
  switch (name) {
    case "packet":
      g = (
        <g transform={`rotate(${wob(16, 5)} 50 50)`}>
          <path d="M22 14 h56 l-3 8 l3 8 v52 l-3 6 h-50 l-3 -6 v-52 l3 -8 z" fill="#fff" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <rect x={24} y={34} width={52} height={30} rx={4} fill={c.sky} stroke={K} strokeWidth={3} />
          <text x={50} y={56} textAnchor="middle" fontFamily={theme.fonts.display} fontWeight={800} fontSize={20} fill={K}>ORS</text>
          <path d="M30 74 h40" stroke={c.good} strokeWidth={5} strokeLinecap="round" />
        </g>
      );
      break;
    case "drop": {
      const s = 1 + Math.sin(f / 10) * 0.05;
      g = (
        <g transform={`translate(50 55) scale(${s}) translate(-50 -55)`}>
          <path d="M50 10 q30 38 30 54 a30 30 0 0 1 -60 0 q0 -16 30 -54 z" fill="#9FD3FF" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M36 62 q0 12 10 18" stroke="#fff" strokeWidth={5} fill="none" strokeLinecap="round" />
        </g>
      );
      break;
    }
    case "lips":
      g = (
        <g>
          <path d="M14 50 q18 -22 36 -10 q18 -12 36 10 q-18 26 -36 26 q-18 0 -36 -26 z" fill="#F7A6A6" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M14 50 q36 10 72 0" stroke={K} strokeWidth={3.5} fill="none" />
          <path d="M34 60 l4 6 M50 62 l-2 7 M64 60 l3 6 M42 42 l3 -4 M60 42 l-3 -4" stroke={K} strokeWidth={2.5} strokeLinecap="round" />
        </g>
      );
      break;
    case "tear":
      g = (
        <g>
          <path d="M12 46 q38 -34 76 0 q-38 34 -76 0 z" fill="#fff" stroke={K} strokeWidth={SW} />
          <circle cx={50} cy={46} r={12} fill="#6B8BFF" stroke={K} strokeWidth={SW} />
          <path d={`M66 ${66 + wob(10, 3)} q8 12 0 18 q-8 -6 0 -18 z`} fill="#9FD3FF" stroke={K} strokeWidth={3} opacity={0.35} />
          <path d="M58 64 l18 22 M76 64 l-18 22" stroke={theme.colors.hero} strokeWidth={6} strokeLinecap="round" />
        </g>
      );
      break;
    case "urine":
      g = (
        <g>
          <path d="M26 20 h48 l-6 66 h-36 z" fill="#fff" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d={`M30 ${56 + wob(12, 2)} q10 -4 20 0 q10 4 20 0 l-4 28 h-32 z`} fill="#E9A62B" />
          <path d="M26 20 h48 l-6 66 h-36 z" fill="none" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
        </g>
      );
      break;
    case "sunken":
      g = (
        <g>
          <ellipse cx={50} cy={50} rx={40} ry={26} fill="#C9B6E8" opacity={0.7} />
          <path d="M16 50 q34 -28 68 0 q-34 28 -68 0 z" fill="#fff" stroke={K} strokeWidth={SW} />
          <circle cx={50 + wob(20, 6)} cy={50} r={11} fill={K} />
          <path d="M18 70 q32 14 64 0" stroke="#8B6CB8" strokeWidth={5} fill="none" strokeLinecap="round" />
        </g>
      );
      break;
    case "zinc":
      g = (
        <g transform={`rotate(${f * 1.2} 50 50)`}>
          <circle cx={50} cy={50} r={34} fill={c.lavender} stroke={K} strokeWidth={SW} />
          <path d="M22 50 h56" stroke={K} strokeWidth={3} />
          <text x={50} y={44} textAnchor="middle" fontFamily={theme.fonts.display} fontWeight={800} fontSize={18} fill={K}>Zn</text>
        </g>
      );
      break;
    case "breast": {
      const b = 1 + Math.sin(f / 7) * 0.06;
      g = (
        <g>
          <path d="M50 86 C14 62 8 38 22 24 C34 14 46 20 50 30 C54 20 66 14 78 24 C92 38 86 62 50 86 Z" fill="#FF9AB8" stroke={K} strokeWidth={SW} transform={`translate(50 50) scale(${b}) translate(-50 -50)`} />
          <path d="M50 38 q12 16 12 24 a12 12 0 0 1 -24 0 q0 -8 12 -24 z" fill="#fff" stroke={K} strokeWidth={3.5} />
        </g>
      );
      break;
    }
    case "bowl":
      g = (
        <g>
          <path d={`M30 ${30 + wob(8, 3)} q4 -8 0 -14 M50 ${28 + wob(9, 3)} q4 -8 0 -14 M70 ${30 + wob(7, 3)} q4 -8 0 -14`} stroke={c.inkSoft} strokeWidth={4} fill="none" strokeLinecap="round" />
          <path d="M10 46 h80 q-4 36 -40 38 q-36 -2 -40 -38 z" fill={c.peach} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <ellipse cx={50} cy={46} rx={40} ry={8} fill={c.lemon} stroke={K} strokeWidth={SW} />
        </g>
      );
      break;
    case "soda":
      g = (
        <g transform={`rotate(${wob(14, 6)} 50 60)`}>
          <rect x={28} y={16} width={44} height={72} rx={8} fill="#FF8F7A" stroke={K} strokeWidth={SW} />
          <path d="M28 30 h44 M28 74 h44" stroke={K} strokeWidth={3} />
          <path d="M36 44 q14 10 28 0" stroke="#fff" strokeWidth={5} fill="none" strokeLinecap="round" />
          {[0, 1, 2].map((i) => <circle key={i} cx={40 + i * 10} cy={10 - ((f + i * 9) % 24) / 2} r={2.5} fill="#9FD3FF" />)}
        </g>
      );
      break;
    case "blood":
      g = (
        <g transform={`translate(0 ${wob(10, 3)})`}>
          <path d="M50 10 q30 38 30 54 a30 30 0 0 1 -60 0 q0 -16 30 -54 z" fill="#E2394F" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M36 62 q0 12 10 18" stroke="#fff" strokeWidth={5} fill="none" strokeLinecap="round" opacity={0.7} />
        </g>
      );
      break;
    case "noglass":
      g = (
        <g>
          <path d="M26 18 h48 l-6 68 h-36 z" fill="#fff" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M30 50 h40 l-3 32 h-34 z" fill="#9FD3FF" />
          <path d="M26 18 h48 l-6 68 h-36 z" fill="none" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <circle cx={74} cy={74} r={16} fill={theme.colors.hero} stroke={K} strokeWidth={SW} />
          <path d="M67 67 l14 14 M81 67 l-14 14" stroke="#fff" strokeWidth={5} strokeLinecap="round" />
        </g>
      );
      break;
    case "clock":
      g = (
        <g>
          <circle cx={50} cy={52} r={36} fill="#fff" stroke={K} strokeWidth={SW} />
          <path d={`M50 52 L50 30`} stroke={K} strokeWidth={5} strokeLinecap="round" transform={`rotate(${f * 6} 50 52)`} />
          <path d="M50 52 L64 52" stroke={K} strokeWidth={5} strokeLinecap="round" transform={`rotate(${f * 0.5} 50 52)`} />
          <circle cx={50} cy={52} r={4} fill={K} />
          <text x={50} y={80} textAnchor="middle" fontFamily={theme.fonts.display} fontWeight={800} fontSize={14} fill={K}>{label ?? ""}</text>
        </g>
      );
      break;
    case "cal":
      g = (
        <g>
          <rect x={14} y={20} width={72} height={66} rx={10} fill="#fff" stroke={K} strokeWidth={SW} />
          <path d="M14 30 a10 10 0 0 1 10 -10 h52 a10 10 0 0 1 10 10 v10 h-72 z" fill={c.peach} stroke={K} strokeWidth={SW} />
          <path d="M32 12 v14 M68 12 v14" stroke={K} strokeWidth={5} strokeLinecap="round" />
          <text x={50} y={78} textAnchor="middle" fontFamily={theme.fonts.display} fontWeight={800} fontSize={label && label.length > 2 ? 26 : 34} fill={K} transform={`rotate(${wob(16, 3)} 50 66)`}>{label}</text>
        </g>
      );
      break;
    case "lamp": {
      const glow = 0.5 + 0.5 * Math.sin(f / 6);
      g = (
        <g>
          <path d="M14 70 L28 40 h44 L86 70" fill="#6FA8FF" opacity={0.25 + 0.25 * glow} />
          <rect x={22} y={22} width={56} height={20} rx={8} fill="#fff" stroke={K} strokeWidth={SW} />
          {[0, 1, 2, 3].map((i) => <rect key={i} x={28 + i * 12} y={30} width={8} height={8} rx={2} fill="#4D86FF" opacity={0.6 + 0.4 * glow} />)}
          <path d="M50 22 v-10" stroke={K} strokeWidth={SW} strokeLinecap="round" />
          <ellipse cx={50} cy={80} rx={26} ry={8} fill={c.lemon} stroke={K} strokeWidth={SW} />
          <circle cx={36} cy={74} r={8} fill={c.lemon} stroke={K} strokeWidth={3.5} />
        </g>
      );
      break;
    }
    case "tube":
      g = (
        <g transform={`rotate(${-20 + wob(18, 5)} 50 50)`}>
          <path d="M38 10 h24 v62 a12 12 0 0 1 -24 0 z" fill="#fff" stroke={K} strokeWidth={SW} />
          <path d={`M40 ${46 + wob(9, 2)} h20 v26 a10 10 0 0 1 -20 0 z`} fill="#F3C623" />
          <path d="M34 10 h32" stroke={K} strokeWidth={SW} strokeLinecap="round" />
        </g>
      );
      break;
    case "bulb": {
      const on = 0.5 + 0.5 * Math.sin(f / 5);
      g = (
        <g>
          {[0, 1, 2, 3, 4].map((i) => <path key={i} d="M50 6 v10" stroke="#F3C623" strokeWidth={5} strokeLinecap="round" opacity={on} transform={`rotate(${(i - 2) * 35} 50 44)`} />)}
          <path d="M50 18 a24 24 0 0 1 14 44 v10 h-28 v-10 a24 24 0 0 1 14 -44 z" fill={c.lemon} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M38 80 h24 M40 88 h20" stroke={K} strokeWidth={SW} strokeLinecap="round" />
        </g>
      );
      break;
    }
    case "warn":
      g = (
        <g transform={`rotate(${wob(6, 3)} 50 60)`}>
          <path d="M50 10 L92 84 H8 Z" fill="#FFD166" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M50 36 v24" stroke={K} strokeWidth={8} strokeLinecap="round" />
          <circle cx={50} cy={72} r={5} fill={K} />
        </g>
      );
      break;
    case "stool":
      g = (
        <g>
          <rect x={10} y={18} width={80} height={64} rx={10} fill="#fff" stroke={K} strokeWidth={SW} />
          {["#F4F1DE", "#EDE6B9", "#E6DA9A"].map((col, i) => (
            <rect key={i} x={18 + i * 25} y={28} width={20} height={26} rx={4} fill={col} stroke={K} strokeWidth={2.5} />
          ))}
          {["#C9A227", "#8A6A1F", "#5E7D2A"].map((col, i) => (
            <rect key={i} x={18 + i * 25} y={58} width={20} height={16} rx={4} fill={col} stroke={K} strokeWidth={2.5} opacity={0.5} />
          ))}
          <path d={`M14 ${41 + wob(10, 1)} h74`} stroke={theme.colors.hero} strokeWidth={3} strokeDasharray="4 4" />
        </g>
      );
      break;
    case "camera":
      g = (
        <g>
          <rect x={12} y={30} width={76} height={52} rx={10} fill="#fff" stroke={K} strokeWidth={SW} />
          <path d="M34 30 l6 -10 h20 l6 10" fill={c.lavender} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <circle cx={50} cy={56} r={15} fill={c.sky} stroke={K} strokeWidth={SW} />
          <circle cx={76} cy={40} r={4} fill={f % 30 < 4 ? "#FFD166" : K} />
        </g>
      );
      break;
    case "liver":
      g = (
        <g transform={`rotate(${wob(20, 3)} 50 50)`}>
          <path d="M10 40 q10 -20 50 -18 q30 2 32 16 q-2 14 -26 26 q-24 12 -40 10 q-18 -2 -16 -34 z" fill="#C46A5A" stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M56 24 q-6 20 2 40" stroke={K} strokeWidth={3} fill="none" />
          <ellipse cx={36} cy={72} rx={8} ry={6} fill="#7DBE6A" stroke={K} strokeWidth={3} />
        </g>
      );
      break;
    case "dna":
      g = (
        <g>
          {Array.from({ length: 8 }).map((_, i) => {
            const y = 12 + i * 10;
            const x = Math.sin(f / 8 + i * 0.8) * 22;
            return (
              <g key={i}>
                <path d={`M${50 - x} ${y} L${50 + x} ${y}`} stroke={K} strokeWidth={3} />
                <circle cx={50 - x} cy={y} r={5} fill={c.pink} stroke={K} strokeWidth={2.5} />
                <circle cx={50 + x} cy={y} r={5} fill={c.sky} stroke={K} strokeWidth={2.5} />
              </g>
            );
          })}
        </g>
      );
      break;
    case "shield":
      g = (
        <g transform={`translate(0 ${wob(14, 2)})`}>
          <path d="M50 8 L84 20 v26 q0 30 -34 46 q-34 -16 -34 -46 v-26 z" fill={c.mint} stroke={K} strokeWidth={SW} strokeLinejoin="round" />
          <path d="M34 50 l12 12 l22 -24" stroke={K} strokeWidth={7} fill="none" strokeLinecap="round" strokeLinejoin="round" />
        </g>
      );
      break;
  }
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" style={{ overflow: "visible" }}>
      {g}
    </svg>
  );
};
