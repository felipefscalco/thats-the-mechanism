import React, { createContext, useContext } from "react";
import { AbsoluteFill } from "remotion";
import { C, Pillar, PILLARS } from "./tokens";
import { GearG } from "./Gear";

/** Depth kit (motion-design-skills shot-composition: bg/mid/fg = ambient/secondary/primary, parallax 0.35x / 1x / 1.4x).
 *  - back plate: big faint gear outlines, moves at 0.35x the camera
 *  - subject: the shot's art, with a soft drop shadow (light from the top)
 *  - front bokeh: a few out-of-focus specks at the frame edges, 1.4x the camera
 *  Deterministic in (seed, g, cam) so the loop-back can redraw the hook's frame 0 exactly. */
export const PillarCtx = createContext<Pillar>(PILLARS.tech);
export type Cam = { s: number; x: number; y: number };
const ID: Cam = { s: 1, x: 0, y: 0 };
const rnd = (seed: number, i: number) => { const v = Math.sin(seed * 12.9898 + i * 78.233) * 43758.5453; return v - Math.floor(v); };
const camT = (c: Cam, k: number) => `translate(${c.x * k}px, ${c.y * k}px) scale(${1 + (c.s - 1) * k})`;

export const ShotLayers: React.FC<{ seed: number; g: number; cam?: Cam; depth?: boolean; children: React.ReactNode }> = ({ seed, g, cam = ID, depth = true, children }) => {
  const pillar = useContext(PillarCtx);
  if (!depth) return <AbsoluteFill style={{ transform: camT(cam, 1), transformOrigin: "540px 740px" }}>{children}</AbsoluteFill>;
  const plates = [0, 1, 2].map((i) => ({ x: i === 1 ? 960 + 80 * rnd(seed, i) : 120 + 840 * rnd(seed, i + 3), y: 330 + 820 * rnd(seed, i + 7), r: 170 + 150 * rnd(seed, i + 11), dir: i % 2 ? -1 : 1 }));
  const specks = [0, 1, 2, 3, 4].map((i) => ({ x: i % 2 ? 1010 + 50 * rnd(seed, i + 20) : 30 + 50 * rnd(seed, i + 21), y: 340 + 800 * rnd(seed, i + 22), r: 10 + 26 * rnd(seed, i + 23), c: i % 3 ? pillar.color : C.amber }));
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ transform: camT(cam, 0.35), transformOrigin: "540px 740px" }}>
        <svg width={1080} height={1920} style={{ position: "absolute" }}>
          {plates.map((p, i) => <g key={i} transform={`translate(${p.x} ${p.y})`} opacity={0.07}><GearG r={p.r} color={pillar.color} rot={p.dir * g * 0.25 + i * 20} hole={C.ink} /></g>)}
        </svg>
      </AbsoluteFill>
      <AbsoluteFill style={{ transform: camT(cam, 1), transformOrigin: "540px 740px", filter: "drop-shadow(0px 22px 22px rgba(0,0,0,0.55))" }}>{children}</AbsoluteFill>
      <AbsoluteFill style={{ transform: camT(cam, 1.4), transformOrigin: "540px 740px", filter: "blur(7px)" }}>
        <svg width={1080} height={1920} style={{ position: "absolute" }}>
          {specks.map((p, i) => <circle key={i} cx={p.x} cy={p.y + 18 * Math.sin(g / 40 + i)} r={p.r} fill={p.c} opacity={0.22} />)}
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
