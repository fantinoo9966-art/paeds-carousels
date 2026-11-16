import React from "react";
import { AbsoluteFill, Composition } from "remotion";
import { TransitionSeries, springTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { flip } from "@remotion/transitions/flip";
import { FPS, W, H, theme } from "./theme";
import { Chrome, Grade, Grain, Paper, Vignette } from "./fx";
import { SceneView, T, sceneLen, totalLen } from "./kit";
import type { Script } from "./types";
import sample from "./sample.json";

const timing = springTiming({ config: { damping: 200 }, durationInFrames: T });
const TINTS = [theme.colors.peach, theme.colors.sky, theme.colors.mint, theme.colors.lavender, theme.colors.lemon, theme.colors.pink, theme.colors.goodSoft];

/* Transition families: the seed picks one, so consecutive Reels feel different. */
const FAMILIES: ((k: number) => any)[] = [
  (k) => (k % 2 ? wipe({ direction: "from-bottom-left" }) : slide({ direction: "from-left" })),
  (k) => (k % 3 === 1 ? flip({ direction: "from-right" }) : slide({ direction: k % 2 ? "from-bottom" : "from-right" })),
  () => flip({ direction: "from-right", perspective: 2400 }),
  () => slide({ direction: "from-bottom" }),
  (k) => (k % 2 ? slide({ direction: "from-top" }) : flip({ direction: "from-bottom", perspective: 2200 })),
  (k) => wipe({ direction: k % 2 ? "from-top-right" : "from-right" }),
];

export const ReelComp: React.FC<Script> = (sc) => {
  const pace = sc.pace ?? 1.3;
  const seed = sc.seed ?? 0;
  const pres = FAMILIES[seed % FAMILIES.length];
  const pg = sc.audience === "pg";
  const disclaimer = sc.disclaimer ?? (pg ? "For medical education · Verify with current guidelines" : "For information only · Always consult your doctor");
  return (
    <AbsoluteFill style={{ background: theme.colors.bg }}>
      <TransitionSeries>
        {sc.scenes.map((s, k) => (
          <React.Fragment key={k}>
            {k > 0 && <TransitionSeries.Transition presentation={pres(k - 1)} timing={timing} />}
            <TransitionSeries.Sequence durationInFrames={sceneLen(s, pace)}>
              <Paper tint={TINTS[(k + seed) % TINTS.length]} notes={pg} />
              <SceneView s={s} sc={sc} i={k} />
            </TransitionSeries.Sequence>
          </React.Fragment>
        ))}
      </TransitionSeries>
      <Chrome disclaimer={disclaimer} />
      <Grade />
      <Grain />
      <Vignette />
    </AbsoluteFill>
  );
};

export const Root: React.FC = () => (
  <Composition
    id="Reel"
    component={ReelComp as any}
    durationInFrames={totalLen(sample as Script)}
    fps={FPS}
    width={W}
    height={H}
    defaultProps={sample as any}
    calculateMetadata={({ props }) => ({ durationInFrames: totalLen(props as unknown as Script) })}
  />
);
