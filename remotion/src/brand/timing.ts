import { Easing, interpolate, spring } from "remotion";

export type Word = { text: string; start: number; end: number };
const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, "");

/** Frame at which `phrase` is spoken (nth occurrence). Throws at bundle-time if the script changed. */
export const makeAt = (words: Word[], fps: number) => (phrase: string, nth = 0, edge: "start" | "end" = "start") => {
  const p = phrase.split(/\s+/).map(norm);
  let seen = 0;
  for (let i = 0; i + p.length <= words.length; i++) {
    if (p.every((w, k) => norm(words[i + k].text) === w) && seen++ === nth) {
      const w = edge === "start" ? words[i] : words[i + p.length - 1];
      return Math.round((edge === "start" ? w.start : w.end) * fps);
    }
  }
  throw new Error(`phrase not found in captions: "${phrase}"`);
};
export const ease = (f: number, a: number, b: number, from = 0, to = 1) =>
  interpolate(f, [a, b], [from, to], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.33, 0, 0.2, 1) });
export const pop = (f: number, at: number, fps: number, damping = 14) =>
  spring({ frame: f - at, fps, config: { damping, stiffness: 170, mass: 0.7 } });
/** Keyframes from spoken-phrase times. r10 (e07 polish crash: [158,180,175,214,243] -> "inputRange must be strictly
 *  monotonically increasing" mid-render): when a phrase lands before the previous key's offset, the key is pushed to
 *  1 frame after the previous one instead of throwing, so a pacing change can never crash a render. */
export const keyed = (f: number, keys: [number, number][]) => {
  const ts: number[] = [];
  for (const [t] of keys) ts.push(ts.length ? Math.max(t, ts[ts.length - 1] + 1) : t);
  return interpolate(f, ts, keys.map((k) => k[1]), { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
};

/** r5 motion tokens (emilkowalski/skills STANDARDS + mg-styles-15 Flat Vector). One timing family per element:
 *  OUT = entering / responding (never ease-in for entries), IN_OUT = on-screen moves, OVERSHOOT = flat-vector "pop" landings. */
export const EASE = {
  OUT: Easing.bezier(0.23, 1, 0.32, 1),
  IN_OUT: Easing.bezier(0.77, 0, 0.175, 1),
  OVERSHOOT: Easing.bezier(0.34, 1.56, 0.64, 1),
  EXIT: Easing.bezier(0.55, 0, 1, 0.45), // exits only: fast leave, never used on arrivals
};
/** Entry that never starts at scale(0): opacity carries the first frames, scale goes 0.62 -> overshoot -> 1. */
export const popScale = (p: number) => (p <= 0 ? 0 : 0.62 + 0.38 * p);
// r9 atomic: a popped element is fully opaque from its first visible frame (the scale carries the entrance), so text in
// a hand-rolled popping group can never be a ghost. Was min(1, p * 2.5).
export const popOpacity = (p: number) => (p > 0.01 ? 1 : 0);
/** Emil stagger: shrinking delays read organic (first gaps longest). i-th delay in frames. */
export const stagger = (i: number, first = 4, decay = 0.82, min = 2) => {
  let t = 0, d = first;
  for (let k = 0; k < i; k++) { t += Math.max(min, d); d *= decay; }
  return t;
};
/** mg Flat Vector squash & stretch on landing (~10%): returns [sx, sy] around 1 for frames after `at`. */
export const squash = (f: number, at: number, amt = 0.1) => {
  const t = f - at;
  if (t < 0 || t > 14) return [1, 1] as const;
  const k = amt * Math.exp(-t / 4) * Math.cos(t / 2.2);
  return [1 + k, 1 - k] as const;
};
