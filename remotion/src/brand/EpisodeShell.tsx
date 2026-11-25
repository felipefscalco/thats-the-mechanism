import { getInputProps } from "remotion";
import React from "react";
import { AbsoluteFill, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Audio } from "@remotion/media";
import { Pillar } from "./tokens";
import { Background, BrandChip, Captions, Chapter, Deck } from "./Chrome";
import { MechanismCard, outroCues } from "./Outro";
import { Cue, SfxTrack, cue } from "./Sfx";
import { AtFrame } from "./frame";
import { Word } from "./timing";
import { T_FRAMES } from "./Shot";
import { PillarCtx, ShotLayers } from "./Depth";
import { createTikTokStyleCaptions } from "@remotion/captions";
/** QA stems: render with --props='{"stem":"sfx"}' (SFX only) or '{"stem":"voice"}' (narration+bed only). */
export const STEM = (getInputProps() as { stem?: string }).stem;

export const LOOP_FRAMES = 14; // final 0.47 s: whip back into the hook frozen at frame 0

/**
 * Standard wrapper for every episode. Provides: background, brand chip + intro sting, captions,
 * lower deck (chapters + progress), fixed outro card with riser/sting, SFX track, and an exact loop:
 * the last LOOP_FRAMES re-enter the hook (rendered at frame 0) so frame N-1 -> frame 0 is seamless.
 */
export const EpisodeShell: React.FC<{
  audio: string; words: Word[]; pillar: Pillar; ep: string; source?: string;
  chapters: Chapter[]; cardAt: number; cardUntil: number; cues: Cue[];
  backdrop?: string; backdropDim?: number; microGap?: number;
  hook: React.ReactNode; children: React.ReactNode;
}> = ({ audio, words, pillar, ep, source, chapters, cardAt, cardUntil, cues, backdrop, backdropDim, microGap = 15, hook, children }) => {
  const f = useCurrentFrame();
  const { durationInFrames: D, fps } = useVideoConfig();
  const loopFrom = D - LOOP_FRAMES;
  const manual = [cue(2, "click", 0.7), ...outroCues(cardAt, cardUntil), cue(loopFrom - T_FRAMES / 2, "whoosh", 0.7), ...cues];
  // micro-ticks: a very quiet click on every caption page that has no other cue within 9 frames (texture, not clutter)
  const pages = createTikTokStyleCaptions({ captions: words.map((w, i) => ({ text: (i === 0 ? "" : " ") + w.text, startMs: w.start * 1000, endMs: w.end * 1000, timestampMs: null, confidence: null })), combineTokensWithinMilliseconds: 850 }).pages;
  const micro = pages.map((p) => Math.round((p.startMs / 1000) * fps)).filter((t) => (t < cardAt || t >= cardUntil) && !manual.some((c) => Math.abs(c.at - t) < microGap)).map((t) => cue(t, "micro", 0.9));
  const allCues = [...manual, ...micro];
  return (
    <PillarCtx.Provider value={pillar}><AbsoluteFill>
      <Background pillar={pillar} backdrop={backdrop} backdropDim={backdropDim} />
      <AtFrame f={f}>
        <AbsoluteFill>{children}</AbsoluteFill>
      </AtFrame>
      {f >= loopFrom - T_FRAMES && <LoopBack from={loopFrom} hook={hook} />}
      <MechanismCard at={cardAt} until={cardUntil} pillar={pillar} />
      <BrandChip pillar={pillar} ep={ep} source={source} />
      <Deck chapters={chapters} pillar={pillar} rewindFrom={loopFrom} />
      <Captions words={words} hideFrom={cardAt} hideTo={cardUntil} fadeFrom={loopFrom} />
      <Audio src={staticFile(audio)} volume={STEM === "sfx" ? 0 : 1} />
      <SfxTrack cues={allCues} />
    </AbsoluteFill></PillarCtx.Provider>
  );
};

/** Whip the frozen hook (frame 0) in from the right; at the last frame it is exactly frame 0. */
const LoopBack: React.FC<{ from: number; hook: React.ReactNode }> = ({ from, hook }) => {
  const f = useCurrentFrame();
  const { durationInFrames: D } = useVideoConfig();
  const p = Math.min(1, Math.max(0, (f - (from - T_FRAMES)) / (D - 1 - (from - T_FRAMES))));
  const q = 1 - Math.min(1, p * 1.6); // arrives a little before the end, then holds
  return (
    <Sequence from={0} layout="none">
      <AbsoluteFill style={{ transform: `translateX(${1080 * q * q}px)`, filter: `blur(${Math.min(14, q * 22)}px)`, background: "transparent" }}>
        <AtFrame f={0}><ShotLayers seed={0} g={0}>{hook}</ShotLayers></AtFrame>
      </AbsoluteFill>
    </Sequence>
  );
};
