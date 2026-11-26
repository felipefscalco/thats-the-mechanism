import { getInputProps } from "remotion";
import React from "react";
import { AbsoluteFill, Freeze, Img, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { PROBE, PROBE_KEY, PROBE_TEXT } from "./Kit";
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
/** r9 payoff hold (gate: qa.py "end card ... payoff settled >= 1.5 s before loop"; Sky v8 settled only 0.4 s): the stage
 *  is frozen for the last PAYOFF_HOLD_S before the loop whip, so the payoff is always complete and still. The audio tail
 *  that makes room for it comes from scripts/mix_one.sh (last word + hold + whip). Never freezes while a word is spoken. */
export const PAYOFF_HOLD_S = 1.5;
/** r7 gate (contrast.py): on the probe passes, raw SVG <text> drawn by an episode (not via <Label>) is also painted in the
 *  key magenta, so WCAG contrast, safe-zone/edge, overlap and clutter gates see it. Scoped to the stage (chrome excluded). */
const PROBE_RAW_TEXT_CSS = `.ttm-stage svg text, .ttm-stage svg tspan { fill: ${PROBE_KEY} !important; stroke: none !important; }`;

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
  const lastWordEnd = words.length ? Math.ceil(words[words.length - 1].end * fps) + 3 : 0;
  const holdFrom = Math.max(lastWordEnd, loopFrom - T_FRAMES - Math.round(PAYOFF_HOLD_S * fps));
  const loopArrived = (loopFrom - T_FRAMES) + Math.ceil((D - 1 - (loopFrom - T_FRAMES)) / 1.6);   // LoopBack q reaches 0 here
  const manual = [cue(2, "click", 0.7), ...outroCues(cardAt, cardUntil), cue(loopFrom - T_FRAMES / 2, "whoosh", 0.7), ...cues];
  // micro-ticks: a very quiet click on every caption page that has no other cue within 9 frames (texture, not clutter)
  const pages = createTikTokStyleCaptions({ captions: words.map((w, i) => ({ text: (i === 0 ? "" : " ") + w.text, startMs: w.start * 1000, endMs: w.end * 1000, timestampMs: null, confidence: null })), combineTokensWithinMilliseconds: 850 }).pages;
  const micro = pages.map((p) => Math.round((p.startMs / 1000) * fps)).filter((t) => (t < cardAt || t >= cardUntil) && !manual.some((c) => Math.abs(c.at - t) < microGap)).map((t) => cue(t, "micro", 0.9));
  const allCues = [...manual, ...micro];
  return (
    <PillarCtx.Provider value={pillar}><AbsoluteFill>
      <Background pillar={pillar} backdrop={backdrop} backdropDim={backdropDim} />
      {PROBE_TEXT && <style>{PROBE_RAW_TEXT_CSS}</style>}
      {/* r10 exact loop: once LoopBack has fully arrived (q = 0 at 1/1.6 of its run) the frozen stage is no longer drawn under
          it, so the last frame is background + frame-0 hook whatever the hook covers (Microwave it10: payoff pills showed
          through a smaller hook, seam PSNR 22.8 dB). */}
      {f >= loopArrived ? null : f >= holdFrom
        ? <Freeze frame={holdFrom}><AtFrame f={holdFrom}><AbsoluteFill className="ttm-stage">{children}</AbsoluteFill></AtFrame></Freeze>
        : <AtFrame f={f}><AbsoluteFill className="ttm-stage">{children}</AbsoluteFill></AtFrame>}
      {f >= loopFrom - T_FRAMES && <AbsoluteFill className="ttm-stage"><LoopBack from={loopFrom} hook={hook} /></AbsoluteFill>}
      <MechanismCard at={cardAt} until={cardUntil} pillar={pillar} />
      <Grain f={f} D={D} />
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

/** Public alias of the frame-0 lock used on the loop whip. Episodes should keep passing
 *  the same `hook` node to EpisodeShell; LoopEnd is the primitive that makes the last
 *  frame identical to frame 0 (do not roll a one-off whip). */
export const LoopEnd = LoopBack;

/** r5 finish texture (mg-styles "finish_texture"; Texturelabs technique, our own procedural tiles from scripts/make_grain.py):
 *  default: one static tile (paper/film texture) at 7% overlay; --props '{"grain":"anim"}' cycles 4 tiles every 2 frames
 *  (frames near the loop seam use tile 0 so last == first); '{"grain":"off"}' disables. */
const Grain: React.FC<{ f: number; D: number }> = ({ f, D }) => {
  const ip = getInputProps() as { grain?: string };
  if (PROBE || ip.grain === "off") return null;
  // default = static paper/film texture (benchmark r5: animated grain +30% render time, +33% file size for little visible gain)
  if (ip.grain !== "anim") return <Img src={staticFile("grain/g0.png")} style={{ position: "absolute", inset: 0, width: 1080, height: 1920, opacity: 0.07, mixBlendMode: "overlay", pointerEvents: "none" }} />;
  const k = f >= D - LOOP_FRAMES ? 0 : Math.floor(f / 2) % 4;
  return <Img src={staticFile(`grain/g${k}.png`)} style={{ position: "absolute", inset: 0, width: 1080, height: 1920, opacity: 0.07, mixBlendMode: "overlay", pointerEvents: "none" }} />;
};
