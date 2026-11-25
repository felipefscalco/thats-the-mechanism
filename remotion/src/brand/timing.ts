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
export const keyed = (f: number, keys: [number, number][]) =>
  interpolate(f, keys.map((k) => k[0]), keys.map((k) => k[1]), { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
