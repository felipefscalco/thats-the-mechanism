import React from "react";
import type { LucideIcon } from "lucide-react";
import { getInputProps } from "remotion";
import { C, DISPLAY, LAYOUT } from "./tokens";
import { EASE } from "./timing";

/** QA contrast probe (scripts/contrast.py): render with --props='{"probe":true}' and every Label/Pill text is drawn in pure
 *  key magenta with no outline, so the QA can find the text pixels and measure the real background around them. */
export const PROBE = !!(getInputProps() as { probe?: boolean }).probe;
/** Second probe pass ({probeOccupancy:true}) used only for the overlap gate. */
export const PROBE_OCC = !!(getInputProps() as { probeOccupancy?: boolean }).probeOccupancy;
/** Magenta text mask: on for both the WCAG pass and the occupancy pass. */
export const PROBE_TEXT = PROBE || PROBE_OCC;
export const PROBE_KEY = "#FF00FF";
/** Occupancy-only: TagLabel/Pill/TitleHook backings are pure cyan. Not painted on the
 *  WCAG pass, so contrast still samples the real backing behind the glyphs. */
export const PROBE_BACKING_KEY = "#00FFFF";
/** Minimum clearance between a label pill and any other label or icon (qa.py overlap gate). */
export const LANE_GAP = 36;

/** r9 atomic text rule (gate: contrast.py "ghost text"; Sky v8 critic blocker 0:18/0:32/0:35/0:42, contrast min 1.04):
 *  on-screen text is never semi-transparent. `o` is ENTRANCE PROGRESS, not opacity: o <= 0.02 hides it, anything above
 *  draws it fully opaque and carries the entrance/exit as a scale pop (0.62x -> overshoot -> 1x). */
export const atomic = (o: number) => ({ show: o > 0.02, sc: o >= 0.999 ? 1 : o <= 0.02 ? 0 : 0.62 + 0.38 * EASE.OVERSHOOT(o) });
const scaleAbout = (sc: number, cx: number, cy: number) => (sc === 1 ? undefined : `translate(${cx} ${cy}) scale(${sc}) translate(${-cx} ${-cy})`);

/** SVG label. Enforces the >= 30px text rule at bundle time. The ONLY way an episode draws SVG text (static gate:
 *  "no raw <text>"). `outline={false}` for dark text on a light backing (no ink stroke). */
export const Label: React.FC<{ x: number; y: number; text: string; color?: string; size?: number; o?: number; anchor?: "middle" | "start" | "end"; weight?: number; font?: string; outline?: boolean }> =
  ({ x, y, text, color = C.paper, size = 40, o = 1, anchor = "middle", weight = 700, font = DISPLAY, outline = true }) => {
    if (size < LAYOUT.minText) throw new Error(`Label "${text}" is ${size}px (< ${LAYOUT.minText}px rule)`);
    const a = atomic(o);
    if (!a.show) return null;
    const w = text.length * size * 0.6, cx = anchor === "middle" ? x : anchor === "end" ? x - w / 2 : x + w / 2, cy = y - size * 0.35;
    if (PROBE_TEXT) return <text x={x} y={y} fill={PROBE_KEY} fontSize={size} fontFamily={font} fontWeight={weight} textAnchor={anchor} transform={scaleAbout(a.sc, cx, cy)}>{text}</text>;
    return <text x={x} y={y} fill={color} fontSize={size} fontFamily={font} fontWeight={weight} textAnchor={anchor} transform={scaleAbout(a.sc, cx, cy)}
      style={outline ? { paintOrder: "stroke", stroke: C.ink, strokeWidth: 6, strokeLinejoin: "round" } : undefined}>{text}</text>;
  };

/** r9 atomic badge: any episode-drawn backing (rect/pill/box) plus its text, as ONE unit. Backing and text share one
 *  transform and are fully opaque from the first visible frame (no ghost text, no text without its backing).
 *  `children` draws the backing in local coords; the label is centred at (tx, ty) in the same coords. */
export const Badge: React.FC<{ x: number; y: number; o?: number; children?: React.ReactNode; text?: string; tx?: number; ty?: number; color?: string; size?: number; anchor?: "middle" | "start" | "end"; font?: string; outline?: boolean; pivot?: [number, number] }> =
  ({ x, y, o = 1, children, text, tx = 0, ty = 0, color = C.paper, size = 32, anchor = "middle", font = DISPLAY, outline = false, pivot = [0, 0] }) => {
    const a = atomic(o);
    if (!a.show) return null;
    return (
      <g transform={`translate(${x} ${y})${a.sc === 1 ? "" : ` translate(${pivot[0]} ${pivot[1]}) scale(${a.sc}) translate(${-pivot[0]} ${-pivot[1]})`}`}>
        {children}
        {text !== undefined && <Label x={tx} y={ty} text={text} color={color} size={size} anchor={anchor} font={font} outline={outline} />}
      </g>
    );
  };

/** r5: Label on a dark rounded backing (for labels that sit on busy art, e.g. over a planet). Width estimated from glyph count. */
export const TagLabel: React.FC<{ x: number; y: number; text: string; color?: string; size?: number; o?: number; anchor?: "middle" | "start" | "end" }> =
  ({ x, y, text, color = C.paper, size = 36, o = 1, anchor = "middle" }) => {
    const w = text.length * size * 0.6 + 36, h = size + 22;
    const x0 = anchor === "middle" ? x - w / 2 : anchor === "end" ? x - w + 18 : x - 18;
    // r6 component (gate: qa.py "badge entrances overshoot") + r9 atomic: the pill pops from 0.62x through an overshoot
    // to 1x as `o` ramps, backing and text fully opaque from the first visible frame (never a ghost).
    const a = atomic(o);
    if (!a.show) return null;
    const cx = x0 + w / 2, cy = y - size * 0.8 - 10 + h / 2;
    return (
      <g transform={scaleAbout(a.sc, cx, cy)}>
        <rect x={x0} y={y - size * 0.8 - 10} width={w} height={h} rx={h / 2} fill={PROBE_OCC ? PROBE_BACKING_KEY : C.ink} opacity={PROBE_OCC ? 1 : 0.88} />
        <Label x={x} y={y} text={text} color={color} size={size} anchor={anchor} />
      </g>
    );
  };

/** Verdict pill. Optional lucide icon (ISC licence) replaces unicode ✓/✕ glyphs for crisp, consistent symbols. */
export const Pill: React.FC<{ x: number; y: number; w: number; text: string; color: string; s: number; textColor?: string; icon?: LucideIcon }> = ({ x, y, w, text, color, s, textColor = C.ink, icon: Icon }) => (
  // r9 atomic: fully opaque from the first visible frame; the entrance is the scale pop only
  s <= 0.01 ? null : <g transform={`translate(${x} ${y}) scale(${s >= 0.999 ? 1 : 0.62 + 0.38 * EASE.OVERSHOOT(s)})`}>
    {!PROBE_OCC && <rect x={-w / 2 + 4} y={-30} width={w} height={76} rx={38} fill="#000" opacity={0.35} />}
    <rect x={-w / 2} y={-38} width={w} height={76} rx={38} fill={PROBE_OCC ? PROBE_BACKING_KEY : color} />
    {Icon && <Icon x={-w / 2 + 22} y={-22} width={44} height={44} color={PROBE_TEXT ? PROBE_KEY : textColor} strokeWidth={3} />}
    <text x={Icon ? 26 : 0} y={14} fill={PROBE_TEXT ? PROBE_KEY : textColor} fontSize={40} fontFamily={DISPLAY} fontWeight={700} textAnchor="middle">{text}</text>
  </g>
);

/** Full-stage SVG layer for artwork. */
export const Stage: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <svg width={1080} height={1920} style={{ position: "absolute", overflow: "visible" }}>{children}</svg>
);

/** Title-as-hook ("The X that Y", The Why Side grammar) in Look A brand type, safe zone top. */
export const TitleHook: React.FC<{ t: [string, string, string]; top?: number; o?: number }> = ({ t, top = 280, o = 1 }) => {
  const a = atomic(o);   // r9 atomic: backing + lines are one opaque unit; `o` drives a scale pop, never a fade
  if (!a.show) return null;
  return (
  <div style={{ position: "absolute", top, left: 48, width: 820, padding: "12px 18px", borderRadius: 22, background: PROBE_OCC ? PROBE_BACKING_KEY : "rgba(13,14,18,0.88)", fontFamily: DISPLAY, fontWeight: 700, lineHeight: 0.96, letterSpacing: -1, transform: a.sc === 1 ? undefined : `scale(${a.sc})`, transformOrigin: "0 0" }}>
    <div style={{ fontSize: 38, color: PROBE_TEXT ? PROBE_KEY : C.paper, letterSpacing: 2, textShadow: PROBE_TEXT ? undefined : "0 4px 16px rgba(0,0,0,0.85)" }}>{t[0]}</div>
    <div style={{ fontSize: 82, color: PROBE_TEXT ? PROBE_KEY : C.amber, textShadow: PROBE_TEXT ? undefined : "0 6px 24px rgba(0,0,0,0.85)" }}>{t[1]}</div>
    <div style={{ fontSize: 82, color: PROBE_TEXT ? PROBE_KEY : C.paper, textShadow: PROBE_TEXT ? undefined : "0 6px 24px rgba(0,0,0,0.85)" }}>{t[2]}</div>
  </div>
  );
};

/**
 * Stack items with a guaranteed gap (default LANE_GAP = 36 px) so a label pill cannot
 * sit on top of an icon or another label. Prefer this over hand-placed x/y for callouts.
 * `x,y` is the anchor of the first item's top-left (dir=down/right) or bottom-left / top-right
 * for up / left. Each item must declare its axis-aligned box.
 */
export const Lane: React.FC<{
  x: number; y: number;
  dir?: "down" | "up" | "right" | "left";
  gap?: number;
  align?: "start" | "middle" | "end";
  items: { w: number; h: number; node: React.ReactNode }[];
}> = ({ x, y, dir = "down", gap = LANE_GAP, align = "middle", items }) => {
  let cursor = 0;
  const vertical = dir === "down" || dir === "up";
  const sign = dir === "down" || dir === "right" ? 1 : -1;
  return (
    <g>
      {items.map((it, i) => {
        const off = cursor;
        cursor += (vertical ? it.h : it.w) + gap;
        const along = sign < 0 ? off - (vertical ? it.h : it.w) : off;
        const cross = vertical
          ? (align === "start" ? 0 : align === "end" ? -it.w : -it.w / 2)
          : (align === "start" ? 0 : align === "end" ? -it.h : -it.h / 2);
        const tx = vertical ? x + cross : x + along;
        const ty = vertical ? y + along : y + cross;
        return <g key={i} transform={`translate(${tx} ${ty})`}>{it.node}</g>;
      })}
    </g>
  );
};

/**
 * Place a TagLabel next to a subject box with a guaranteed gap (default 36 px).
 * `box` is the subject's axis-aligned frame (top-left x,y, width, height) in stage space.
 */
export const LabeledBox: React.FC<{
  box: { x: number; y: number; w: number; h: number };
  label: string;
  side?: "top" | "bottom" | "left" | "right";
  gap?: number;
  size?: number;
  color?: string;
  o?: number;
}> = ({ box, label, side = "bottom", gap = LANE_GAP, size = 36, color = C.paper, o = 1 }) => {
  let lx = box.x + box.w / 2, ly = box.y + box.h + gap + size * 0.8 + 10, anchor: "middle" | "start" | "end" = "middle";
  if (side === "top") { ly = box.y - gap - 10; }
  else if (side === "right") { lx = box.x + box.w + gap + 18; ly = box.y + box.h / 2 + size * 0.35; anchor = "start"; }
  else if (side === "left") { lx = box.x - gap - 18; ly = box.y + box.h / 2 + size * 0.35; anchor = "end"; }
  return <TagLabel x={lx} y={ly} text={label} size={size} color={color} o={o} anchor={anchor} />;
};

/**
 * r8 component (gate: qa.py "every element entrance scales/slides/draws on", scripts/entrances.py): the one way to bring
 * ANY element on stage. `p` is the entrance progress 0..1 (e.g. ease(f, a, b) or pop(f, at, fps)); the element anticipates
 * (dips to 0.94x for the first 15 %), overshoots (~1.08x) and settles at 1x, or slides in along `from` with the same
 * overshoot. r9 atomic: fully opaque from the first visible frame (no ghost text); motion alone carries it. (cx, cy) = pivot.
 */
export const Enter: React.FC<{ p: number; cx: number; cy: number; from?: "scale" | "up" | "down" | "left" | "right"; dist?: number; children: React.ReactNode }> =
  ({ p, cx, cy, from = "scale", dist = 120, children }) => {
    if (p <= 0) return null;
    if (p >= 1) return <g>{children}</g>;
    const k = EASE.OVERSHOOT(p);                       // 0 -> ~1.1 -> 1
    const antic = p < 0.15 ? 1 - 0.06 * Math.sin((p / 0.15) * Math.PI) : 1;
    let tf: string;
    if (from === "scale") {
      const sc = (0.6 + 0.4 * k) * antic;
      tf = `translate(${cx} ${cy}) scale(${sc}) translate(${-cx} ${-cy})`;
    } else {
      const d = dist * (1 - k);
      const [dx, dy] = from === "up" ? [0, d] : from === "down" ? [0, -d] : from === "left" ? [-d, 0] : [d, 0];
      const sc = 0.92 + 0.08 * k;
      tf = `translate(${dx} ${dy}) translate(${cx} ${cy}) scale(${sc}) translate(${-cx} ${-cy})`;
    }
    return <g transform={tf}>{children}</g>;
  };
