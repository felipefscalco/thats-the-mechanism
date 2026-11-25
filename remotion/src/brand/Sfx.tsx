import { getInputProps } from "remotion";
import React from "react";
import { Sequence, staticFile } from "remotion";
import { Audio } from "@remotion/media";
const STEM_SFX = (getInputProps() as { stem?: string }).stem;

/** Library in public/sfx (see sfx/CREDITS.csv). All normalised so volume=1 sits ~12-14 dB under the voice. */
export type SfxName = "whoosh" | "riser" | "sting" | "tick" | "pop" | "click" | "confirm" | "error" | "glitch" | "thud" | "clank"
  | "swish" | "whip" | "cut" | "glint" | "stamp" | "count" | "pop3" | "micro";
export type Cue = { at: number; sfx: SfxName; vol?: number };
export const cue = (at: number, sfx: SfxName, vol = 1): Cue => ({ at, sfx, vol });

/** Layered reveal: impact + shine 2 frames later (papercut-explainer "stamp" + "glint"). */
export const reveal = (at: number, vol = 0.8): Cue[] => [cue(at, "stamp", vol), cue(at + 2, "glint", vol * 0.8)];

/** Drop duplicates (same sfx within 3 frames) so auto + manual cues never stack into clutter. */
export const dedupe = (cues: Cue[]) => {
  const out: Cue[] = [];
  for (const c of [...cues].sort((a, b) => a.at - b.at)) if (!out.some((o) => o.sfx === c.sfx && Math.abs(o.at - c.at) < 3)) out.push(c);
  return out;
};

export const SfxTrack: React.FC<{ cues: Cue[] }> = ({ cues }) => (
  <>
    {dedupe(cues).filter((c) => c.at >= 0).map((c, i) => (
      <Sequence key={i} from={c.at} name={`sfx:${c.sfx}`} layout="none">
        <Audio src={staticFile(`sfx/${c.sfx}.wav`)} volume={STEM_SFX === "voice" ? 0 : c.vol ?? 1} />
      </Sequence>
    ))}
  </>
);
