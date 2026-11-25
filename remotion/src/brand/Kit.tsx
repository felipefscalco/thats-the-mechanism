import React from "react";
import type { LucideIcon } from "lucide-react";
import { getInputProps } from "remotion";
import { C, DISPLAY, LAYOUT } from "./tokens";
import { popOpacity, popScale } from "./timing";

/** QA contrast probe (scripts/contrast.py): render with --props='{"probe":true}' and every Label/Pill text is drawn in pure
 *  key magenta with no outline, so the QA can find the text pixels and measure the real background around them. */
export const PROBE = !!(getInputProps() as { probe?: boolean }).probe;
export const PROBE_KEY = "#FF00FF";

/** SVG label. Enforces the >= 30px text rule at bundle time. */
export const Label: React.FC<{ x: number; y: number; text: string; color?: string; size?: number; o?: number; anchor?: "middle" | "start" | "end"; weight?: number; font?: string }> =
  ({ x, y, text, color = C.paper, size = 40, o = 1, anchor = "middle", weight = 700, font = DISPLAY }) => {
    if (size < LAYOUT.minText) throw new Error(`Label "${text}" is ${size}px (< ${LAYOUT.minText}px rule)`);
    if (PROBE) return o < 0.02 ? null : <text x={x} y={y} fill={PROBE_KEY} fontSize={size} fontFamily={font} fontWeight={weight} textAnchor={anchor}>{text}</text>;
    return <text x={x} y={y} fill={color} fontSize={size} fontFamily={font} fontWeight={weight} textAnchor={anchor} opacity={o}
      style={{ paintOrder: "stroke", stroke: C.ink, strokeWidth: 6, strokeLinejoin: "round" }}>{text}</text>;
  };

/** r5: Label on a dark rounded backing (for labels that sit on busy art, e.g. over a planet). Width estimated from glyph count. */
export const TagLabel: React.FC<{ x: number; y: number; text: string; color?: string; size?: number; o?: number; anchor?: "middle" | "start" | "end" }> =
  ({ x, y, text, color = C.paper, size = 36, o = 1, anchor = "middle" }) => {
    const w = text.length * size * 0.6 + 36, h = size + 22;
    const x0 = anchor === "middle" ? x - w / 2 : anchor === "end" ? x - w + 18 : x - 18;
    return (
      <g opacity={o}>
        <rect x={x0} y={y - size * 0.8 - 10} width={w} height={h} rx={h / 2} fill={C.ink} opacity={0.82} />
        <Label x={x} y={y} text={text} color={color} size={size} anchor={anchor} />
      </g>
    );
  };

/** Verdict pill. Optional lucide icon (ISC licence) replaces unicode ✓/✕ glyphs for crisp, consistent symbols. */
export const Pill: React.FC<{ x: number; y: number; w: number; text: string; color: string; s: number; textColor?: string; icon?: LucideIcon }> = ({ x, y, w, text, color, s, textColor = C.ink, icon: Icon }) => (
  <g transform={`translate(${x} ${y}) scale(${popScale(s)})`} opacity={popOpacity(s)}>
    <rect x={-w / 2 + 4} y={-30} width={w} height={76} rx={38} fill="#000" opacity={0.35} />
    <rect x={-w / 2} y={-38} width={w} height={76} rx={38} fill={color} />
    {Icon && <Icon x={-w / 2 + 22} y={-22} width={44} height={44} color={textColor} strokeWidth={3} />}
    <text x={Icon ? 26 : 0} y={14} fill={PROBE ? PROBE_KEY : textColor} fontSize={40} fontFamily={DISPLAY} fontWeight={700} textAnchor="middle">{text}</text>
  </g>
);

/** Full-stage SVG layer for artwork. */
export const Stage: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <svg width={1080} height={1920} style={{ position: "absolute", overflow: "visible" }}>{children}</svg>
);

/** Title-as-hook ("The X that Y", The Why Side grammar) in Look A brand type, safe zone top. */
export const TitleHook: React.FC<{ t: [string, string, string]; top?: number; o?: number }> = ({ t, top = 280, o = 1 }) => (
  <div style={{ position: "absolute", top, left: 48, width: 820, padding: "12px 18px", borderRadius: 22, background: "rgba(13,14,18,0.82)", fontFamily: DISPLAY, fontWeight: 700, lineHeight: 0.96, letterSpacing: -1, opacity: o }}>
    <div style={{ fontSize: 38, color: PROBE ? PROBE_KEY : C.paper, letterSpacing: 2, textShadow: PROBE ? undefined : "0 4px 16px rgba(0,0,0,0.85)" }}>{t[0]}</div>
    <div style={{ fontSize: 82, color: PROBE ? PROBE_KEY : C.amber, textShadow: PROBE ? undefined : "0 6px 24px rgba(0,0,0,0.85)" }}>{t[1]}</div>
    <div style={{ fontSize: 82, color: PROBE ? PROBE_KEY : C.paper, textShadow: PROBE ? undefined : "0 6px 24px rgba(0,0,0,0.85)" }}>{t[2]}</div>
  </div>
);
