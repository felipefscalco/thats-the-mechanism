import { getInputProps } from "remotion";
import React from "react";
import { Sequence, staticFile } from "remotion";
import { Audio } from "@remotion/media";
const STEM_SFX = (getInputProps() as { stem?: string }).stem;

/** Library in public/sfx (see sfx/CREDITS.csv). All normalised so volume=1 sits ~12-14 dB under the voice. */
export type SfxName = "whoosh" | "riser" | "sting" | "tick" | "pop" | "click" | "confirm" | "error" | "glitch" | "thud" | "clank";
export type Cue = { at: number; sfx: SfxName; vol?: number };
export const cue = (at: number, sfx: SfxName, vol = 1): Cue => ({ at, sfx, vol });

export const SfxTrack: React.FC<{ cues: Cue[] }> = ({ cues }) => (
  <>
    {cues.filter((c) => c.at >= 0).map((c, i) => (
      <Sequence key={i} from={c.at} name={`sfx:${c.sfx}`} layout="none">
        <Audio src={staticFile(`sfx/${c.sfx}.wav`)} volume={STEM_SFX === "voice" ? 0 : c.vol ?? 1} />
      </Sequence>
    ))}
  </>
);
