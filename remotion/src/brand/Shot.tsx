import React from "react";
import { AbsoluteFill, interpolate, Sequence, useCurrentFrame } from "remotion";
import { ShotLayers } from "./Depth";
import { Cue, SfxTrack, cue } from "./Sfx";
import { EASE } from "./timing";

/** Camera moves are punctuation (huashu-art-motion 镜头语言):
 *  push = slow push 0.6-1.5 s to lead the eye; pull = pull-out to show context / close a section;
 *  glide = move sideways to the next thing; punch = fast push 0.25-0.35 s, +18-32 %, only on reveals.
 *  Never chain three pushes in a row; holds are fine while the object itself moves. */
export type CamKind = "push" | "pull" | "glide" | "punch" | "settle";
export type CamMove = { at: number; kind: CamKind; s?: number; x?: number; y?: number; dur?: number };
const DUR: Record<CamKind, number> = { push: 30, pull: 33, glide: 21, punch: 14, settle: 18 };

/** video-shotcraft crash-zoom-punch: 5 f anticipation pull-back (~3.5 % of the move), 5 f fast push, 4 f overshoot recoil. */
const punchCurve = (t: number) => {
  // t in [0,1] over the whole punch; returns progress (can dip < 0 and overshoot > 1)
  const a = 5 / 14, b = 10 / 14;
  if (t <= a) return -0.035 * Math.sin((t / a) * Math.PI * 0.5);
  if (t <= b) { const u = (t - a) / (b - a); return -0.035 + 1.095 * u * u * (3 - 2 * u); }
  const u = (t - b) / (1 - b); return 1.06 - 0.06 * EASE.OUT(u);
};

export const camState = (f: number, moves: CamMove[]) => {
  let s = 1, x = 0, y = 0;
  for (const m of [...moves].sort((a, b) => a.at - b.at)) {
    const d = m.dur ?? DUR[m.kind];
    const t = interpolate(f, [m.at, m.at + d], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const p = m.kind === "punch" ? (t <= 0 ? 0 : t >= 1 ? 1 : punchCurve(t))
      : m.kind === "pull" || m.kind === "settle" ? EASE.OUT(t) : EASE.IN_OUT(t);
    s = s + ((m.s ?? s) - s) * p; x = x + ((m.x ?? x) - x) * p; y = y + ((m.y ?? y) - y) * p;
  }
  return { s, x, y };
};

/** Transitions between shots are moves of the world, not cross-fades (bang-motion anti-slideshow rule #1/#5). */
export type Trans = "none" | "push" | "whip" | "whipUp" | "cut";
export const T_FRAMES = 10;

const transStyle = (kind: Trans, p: number, dir: "in" | "out"): React.CSSProperties => {
  // p: 0 -> 1 progress of the transition
  if (kind === "none" || kind === "cut") return {};
  const q = dir === "in" ? 1 - p : p; // 0 = fully on screen, 1 = fully gone
  const blur = Math.min(14, q * 22);
  if (kind === "push") {
    const sc = dir === "out" ? 1 + 0.7 * q * q : 1 - 0.28 * q;
    return { transform: `scale(${sc})`, filter: `blur(${blur}px)`, opacity: dir === "out" ? 1 - q ** 3 : 1 - q ** 2 };
  }
  if (kind === "whip") {
    const tx = (dir === "out" ? -1 : 1) * 1080 * q * q;
    return { transform: `translateX(${tx}px) skewX(${(dir === "out" ? 1 : -1) * q * 8}deg)`, filter: `blur(${blur}px)` };
  }
  // whipUp
  const ty = (dir === "out" ? -1 : 1) * 1920 * q * q;
  return { transform: `translateY(${ty}px)`, filter: `blur(${blur}px)` };
};

export const Shot: React.FC<{
  from: number; to: number; inT?: Trans; outT?: Trans; cam?: CamMove[]; name?: string; children: React.ReactNode;
  /** screen-space layer (pills, verdicts): moves with the transition but NOT with the camera, so punches never push it into captions */
  hud?: React.ReactNode;
  /** depth layers (parallax plates, shadow, bokeh); default on */
  depth?: boolean;
  /** automatic camera/transition SFX; default on */
  quiet?: boolean;
}> = ({ from, to, inT = "push", outT = "push", cam = [], name, children, hud, depth = true, quiet = false }) => {
  const hi = inT === "none" || inT === "cut" ? 0 : T_FRAMES / 2;
  const ho = outT === "none" || outT === "cut" ? 0 : T_FRAMES / 2;
  const start = Math.max(0, Math.round(from - hi));
  const end = Math.round(to + ho);
  return (
    <Sequence from={start} durationInFrames={Math.max(1, end - start)} name={name} layout="none">
      <ShotInner offset={start} from={from} to={to} inT={inT} outT={outT} cam={cam} hud={hud} depth={depth}>{children}</ShotInner>
      {!quiet && <SfxTrack cues={camCues(cam, inT, from).map((c) => ({ ...c, at: c.at - start }))} />}
    </Sequence>
  );
};
const ShotInner: React.FC<{ offset: number; from: number; to: number; inT: Trans; outT: Trans; cam: CamMove[]; children: React.ReactNode; hud?: React.ReactNode; depth: boolean }> =
  ({ offset, from, to, inT, outT, cam, children, hud, depth }) => {
    const g = useCurrentFrame() + offset; // global frame
    const h = T_FRAMES / 2;
    let st: React.CSSProperties = {};
    if (g < from + h && inT !== "none") {
      if (inT === "cut") {
        const k = interpolate(g, [from, from + 6], [1.06, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        st = { transform: `scale(${k})` };
      } else st = transStyle(inT, interpolate(g, [from - h, from + h], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }), "in");
    } else if (g > to - h && outT !== "none" && outT !== "cut") {
      st = transStyle(outT, interpolate(g, [to - h, to + h], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }), "out");
    }
    const c = camState(g, cam);
    return (
      <AbsoluteFill style={{ ...st, transformOrigin: "50% 40%" }}>
        <ShotLayers seed={from} g={g} cam={c} depth={depth}>{children}</ShotLayers>
        {hud}
      </AbsoluteFill>
    );
  };

/** Every camera move gets a sound (Kurzgesagt-style density, papercut "slide"/"whip"/"stamp"+"glint"):
 *  push/pull/glide = soft swish, punch = layered reveal; whip/cut transitions get their own swoosh. */
export const camCues = (cam: CamMove[], inT: Trans, from: number): Cue[] => {
  const out: Cue[] = [];
  for (const m of cam) {
    if (m.dur === 1) continue; // instantaneous framing, not a move
    if (m.kind === "punch") out.push(cue(m.at + 7, "stamp", 0.55), cue(m.at + 9, "glint", 0.5)); // impact on the hit frame
    else if (m.kind !== "settle") out.push(cue(m.at, "swish", m.kind === "pull" ? 0.7 : 0.6));
  }
  if (inT === "whip" || inT === "whipUp") out.push(cue(from - T_FRAMES / 2, "whip", 0.75));
  if (inT === "cut") out.push(cue(from, "cut", 0.8));
  return out;
};
