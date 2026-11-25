import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { C, DISPLAY, Pillar } from "./tokens";
import { Gear } from "./Gear";
import { ease, pop } from "./timing";
import { Cue, cue } from "./Sfx";

/** Fixed outro card on the catchphrase. Camera punch-in + sting; leaves on a push-through. */
export const MechanismCard: React.FC<{ at: number; until: number; pillar: Pillar }> = ({ at, until, pillar }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < at - 2 || f > until + 8) return null;
  const s = pop(f, at, fps, 11);
  const out = ease(f, until, until + 8);
  const line = ease(f, at + 6, at + 20);
  return (
    <AbsoluteFill style={{ opacity: 1 - out, transform: `scale(${1 + out * 0.5})`, filter: `blur(${out * 14}px)` }}>
      <AbsoluteFill style={{ background: `rgba(13,14,18,${0.88 * Math.min(1, s)})` }} />
      <div style={{ position: "absolute", top: 440, width: 1080, display: "flex", flexDirection: "column", alignItems: "center", gap: 36, transform: `scale(${0.6 + 0.4 * s})` }}>
        <div style={{ filter: `drop-shadow(0 0 30px ${C.amber}88)` }}><Gear size={210} color={C.amber} rot={(f - at) * 4} /></div>
        <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 100, lineHeight: 0.98, color: C.paper, textAlign: "center", letterSpacing: -1, textShadow: "0 6px 20px rgba(0,0,0,0.5)" }}>
          THAT'S THE<br />MECHANISM.
        </div>
        <div style={{ width: 560 * line, height: 12, borderRadius: 6, background: `linear-gradient(90deg, ${C.amber}, ${pillar.color})` }} />
      </div>
    </AbsoluteFill>
  );
};
/** Standard sound for the card: riser into it, sting on it, whoosh out. */
export const outroCues = (at: number, until: number): Cue[] => [cue(at - 47, "riser", 0.8), cue(at, "sting", 1), cue(until - 4, "whoosh", 0.8)];
