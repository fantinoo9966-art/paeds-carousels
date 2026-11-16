import { Easing } from "remotion";
import { loadFont as loadBaloo } from "@remotion/google-fonts/Baloo2";
import { loadFont as loadNunito } from "@remotion/google-fonts/Nunito";
import { loadFont as loadCaveat } from "@remotion/google-fonts/Caveat";

const baloo = loadBaloo("normal", { weights: ["600", "700", "800"], subsets: ["latin"] });
const nunito = loadNunito("normal", { weights: ["600", "700", "800"], subsets: ["latin"] });
const caveat = loadCaveat("normal", { weights: ["700"], subsets: ["latin"] });

// Pastel "Pediatrics Made Simple" palette, matching the channel's infographic posts.
export const theme = {
  colors: {
    bg: "#FFF7EE", // cream paper
    bgWarm: "#FFE9DA",
    ink: "#2A2540",
    inkSoft: "#6B6480",
    hero: "#FF4D5E", // alert red: max one element per frame
    heroSoft: "#FFE1E4",
    good: "#2FB37A",
    goodSoft: "#DDF5EA",
    pink: "#FFC7D9",
    peach: "#FFD3B0",
    mint: "#BFEBD8",
    lavender: "#D9CCFF",
    sky: "#BFE3FF",
    lemon: "#FFF0A8",
    skin: "#FFD7B8",
    skinShade: "#F4B996",
    cheek: "#FF9AA8",
    white: "#FFFFFF",
  },
  fonts: {
    display: baloo.fontFamily,
    body: nunito.fontFamily,
    hand: caveat.fontFamily,
  },
  ease: {
    out: Easing.bezier(0.16, 1, 0.3, 1),
    inOut: Easing.bezier(0.83, 0, 0.17, 1),
    in: Easing.bezier(0.7, 0, 0.84, 0),
  },
  spring: {
    snappy: { damping: 14, stiffness: 160, mass: 0.6 },
    smooth: { damping: 20, stiffness: 90, mass: 1 },
    bouncy: { damping: 11, stiffness: 170, mass: 0.7 },
  },
} as const;

export const FPS = 30;
export const W = 1080;
export const H = 1920;
export const HANDLE = "@paediatrick_or_treats";
