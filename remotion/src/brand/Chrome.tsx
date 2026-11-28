import React, { useMemo } from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { createTikTokStyleCaptions, Caption } from "@remotion/captions";
import { C, DISPLAY, LAYOUT, MONO, Pillar, SANS } from "./tokens";
import { Gear, GearG } from "./Gear";
import { ease, pop, Word } from "./timing";

/** Everything periodic in the chrome uses phase = f / durationInFrames so frame N == frame 0 (exact loop). */
const usePhase = () => {
  const f = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return { f, D: durationInFrames, ph: f / durationInFrames };
};

/** Two-layer surface (base + light + dot grid), drifting, never flat (bang-motion §7d). */
export const Background: React.FC<{ pillar: Pillar; backdrop?: string; backdropDim?: number }> = ({ pillar, backdrop, backdropDim = 0.45 }) => {
  const { ph } = usePhase();
  const drift = (ph * 3 * 60) % 60; // integer cycles over the video
  const gx = 50 + 8 * Math.sin(ph * Math.PI * 2);
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      {backdrop && <Img src={staticFile(backdrop)} style={{ position: "absolute", inset: 0, width: 1080, height: 1920, objectFit: "cover", opacity: 1 - backdropDim }} />}
      {backdrop && <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(13,14,18,0.68) 0%, rgba(13,14,18,0.22) 26%, rgba(13,14,18,0.28) 60%, rgba(13,14,18,0.88) 76%, rgba(13,14,18,0.96) 100%)" }} />}
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 85% 45% at ${gx}% 34%, ${pillar.color}26, transparent 70%)` }} />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 70% 30% at ${100 - gx}% 88%, ${C.amber}12, transparent 70%)` }} />
      <svg width={1080} height={1920} style={{ position: "absolute" }}>
        <defs>
          <pattern id="dots" width={60} height={60} patternUnits="userSpaceOnUse" patternTransform={`translate(0 ${drift})`}>
            <circle cx={30} cy={30} r={2} fill="rgba(255,255,255,0.07)" />
          </pattern>
        </defs>
        <rect width={1080} height={1920} fill="url(#dots)" />
      </svg>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.55))" }} />
    </AbsoluteFill>
  );
};

/** Brand chip, always on screen. Intro sting (0-1.2 s) plays ON the hook: gear spins one turn,
 *  a shine sweeps the name, amber glow pulses. Rest state at f=0 == rest state at the end. */
export const BrandChip: React.FC<{ pillar: Pillar; ep: string; source?: string }> = ({ pillar, ep, source }) => {
  const { f, ph } = usePhase();
  const spin = 360 * ease(f, 0, 30);
  const rot = spin + ph * 360 * 4;
  const glow = Math.sin(Math.PI * Math.min(1, f / 36)) ** 2;
  const shine = interpolate(f, [4, 34], [-40, 140], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      {/* r10 header plate (e07 v2 critic: the water pipe covered "#007 · PHYSICS"): a feathered ink plate keeps the brand
          lines readable over any stage art; over empty background it is invisible (same colour as C.ink). */}
      <div style={{
        position: "absolute", left: 0, top: 118, width: 860, height: 156,
        background: "linear-gradient(90deg, rgba(13,14,18,0.9) 0%, rgba(13,14,18,0.9) 70%, rgba(13,14,18,0) 100%)",
        WebkitMaskImage: "linear-gradient(180deg, transparent 0%, #000 18%, #000 82%, transparent 100%)",
        maskImage: "linear-gradient(180deg, transparent 0%, #000 18%, #000 82%, transparent 100%)",
      }} />
      <div style={{ position: "absolute", left: 60, top: 146, display: "flex", alignItems: "center", gap: 16 }}>
        <div style={{ filter: `drop-shadow(0 0 ${18 * glow}px ${C.amber})`, transform: `scale(${1 + 0.18 * glow})` }}>
          <Gear size={50} color={C.amber} rot={rot} />
        </div>
        <span style={{
          fontFamily: DISPLAY, fontWeight: 700, fontSize: 34, letterSpacing: 4, color: C.paper,
          backgroundImage: `linear-gradient(100deg, ${C.paper} ${shine - 18}%, ${C.amber} ${shine}%, ${C.paper} ${shine + 18}%)`,
          WebkitBackgroundClip: "text", backgroundClip: "text", WebkitTextFillColor: "transparent",
        }}>THAT'S THE MECHANISM</span>
      </div>
      <div style={{ position: "absolute", left: 60, top: 214, fontFamily: MONO, fontWeight: 500, fontSize: 30, letterSpacing: 2, color: pillar.color, whiteSpace: "nowrap" }}>
        #{ep} · {pillar.name}{source ? <span style={{ color: C.dim }}> · SRC: {source}</span> : null}
      </div>
    </AbsoluteFill>
  );
};

export type Chapter = { at: number; label: string };
/** Lower deck (fills the bottom third inside the safe zone): chapter counter + progress rail with a gear rider.
 *  During the last `rewind` frames the rail rewinds to 0 so the final frame equals frame 0. */
export const Deck: React.FC<{ chapters: Chapter[]; pillar: Pillar; rewindFrom: number }> = ({ chapters, pillar, rewindFrom }) => {
  const { f, D } = usePhase();
  const prog = f < rewindFrom ? f / rewindFrom : interpolate(f, [rewindFrom, D - 1], [1, 0], { extrapolateRight: "clamp" });
  // r10: while the rail rewinds for the loop, the chapter number rewinds with it (last frame = "01/NN", as on frame 0)
  const fc = f < rewindFrom ? f : Math.round(prog * rewindFrom);
  const ci = Math.max(0, chapters.filter((c) => c.at <= fc).length - 1);
  const cur = chapters[ci];
  const W = LAYOUT.safeRight - LAYOUT.safeLeft;
  const x0 = LAYOUT.safeLeft;
  const y = LAYOUT.deckTop;
  const s = pop(f, cur.at, 30, 16);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: x0, top: y, width: W, display: "flex", alignItems: "baseline", gap: 18, fontFamily: MONO, fontWeight: 700, fontSize: 30, color: C.dim }}>
        <span style={{ color: pillar.color }}>{String(ci + 1).padStart(2, "0")}/{String(chapters.length).padStart(2, "0")}</span>
        <span style={{ color: C.paper, letterSpacing: 2, transform: `translateY(${(1 - s) * 16}px)`, opacity: Math.min(1, s * 1.4) * (f >= rewindFrom ? interpolate(f, [rewindFrom, D - 1], [1, 0], { extrapolateRight: "clamp" }) : 1), display: "inline-block" }}>{cur.label}</span>
      </div>
      <svg width={1080} height={120} style={{ position: "absolute", top: y + 50 }}>
        <rect x={x0} y={18} width={W} height={8} rx={4} fill={C.ink3} />
        <rect x={x0} y={18} width={W * prog} height={8} rx={4} fill={C.amber} />
        {chapters.slice(1).map((c, i) => {
          const cx = x0 + (W * c.at) / rewindFrom;
          return <rect key={i} x={cx - 2} y={12} width={4} height={20} rx={2} fill={c.at <= f && f < rewindFrom ? C.amber : C.line} />;
        })}
        <g transform={`translate(${x0 + W * prog} 22)`}>
          <circle r={24} fill={C.ink} />
          <GearG r={20} color={C.amber} rot={prog * 720} />
        </g>
      </svg>
    </AbsoluteFill>
  );
};

/** TikTok-style word captions: 2-3 words per page, current word amber, >= 80px, inside safe zone. */
export const Captions: React.FC<{ words: Word[]; hideFrom?: number; hideTo?: number; fadeFrom?: number }> = ({ words, hideFrom = -1, hideTo = -1, fadeFrom = 1e9 }) => {
  const f = useCurrentFrame();
  const { fps, durationInFrames: D } = useVideoConfig();
  const loopFade = f >= fadeFrom ? interpolate(f, [fadeFrom, D - 1], [1, 0], { extrapolateRight: "clamp" }) : 1; // exact loop: frame 0 has no caption
  const pages = useMemo(() => {
    const caps: Caption[] = words.map((w, i) => ({ text: (i === 0 ? "" : " ") + w.text, startMs: w.start * 1000, endMs: w.end * 1000, timestampMs: null, confidence: null }));
    return createTikTokStyleCaptions({ captions: caps, combineTokensWithinMilliseconds: 850 }).pages;
  }, [words]);
  if (f >= hideFrom && f < hideTo) return null;
  const ms = (f / fps) * 1000;
  const lastEnd = words[words.length - 1].end * 1000 + 350;
  if (ms > lastEnd) return null;
  const page = pages.find((p, i) => ms >= p.startMs && (i === pages.length - 1 ? true : ms < pages[i + 1].startMs));
  if (!page) return null;
  const local = f - Math.round((page.startMs / 1000) * fps);
  const s = pop(local, 0, fps, 16);
  return (
    <div style={{ position: "absolute", left: LAYOUT.safeLeft, width: LAYOUT.safeRight - LAYOUT.safeLeft, top: LAYOUT.captionTop, opacity: loopFade, display: "flex", justifyContent: "center" }}>
      {/* r8 root cause (Sky_v7 0:38, critic "captions drop to ghostly dark grey"): every page faded in from opacity 0
          (Math.min(1, s * 1.5) on a spring that starts at 0), so each page started with 3-4 ghost frames at 0-60 %,
          and fast speech (pages every ~0.5 s) spent up to a third of the time dimmed. Pages now land at full opacity
          and pop by scale only; qa.py "captions: never dimmed" holds it. */}
      {/* r10 (critic R-045, gatesmith pilot): balanced lines, so a short word ("a", "of") is never stranded alone on line 2 */}
      <div style={{ textAlign: "center", textWrap: "balance", fontFamily: SANS, fontWeight: 900, fontSize: 84, lineHeight: 1.12, color: "white", transform: `scale(${0.9 + 0.1 * s})` }}>
        {page.tokens.map((t, i) => {
          const active = ms >= t.fromMs && ms < t.toMs + 80;
          return (
            <span key={i} style={{
              color: active ? C.amber : "white", WebkitTextStroke: "14px #000", paintOrder: "stroke fill",
              textShadow: "0 8px 24px rgba(0,0,0,0.6)", whiteSpace: "nowrap",
              display: "inline-block", margin: "0 0.22em", transform: `scale(${active ? 1.07 : 1})`,   // r10 R-045: the 14 px stroke ate the 0.13em gap ("themicrowaves"); 0.22em leaves ~20 px
            }}>{t.text.trim()}</span>
          );
        })}
      </div>
    </div>
  );
};
