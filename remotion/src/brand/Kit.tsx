import React from "react";
import { C, DISPLAY, LAYOUT } from "./tokens";

/** SVG label. Enforces the >= 30px text rule at bundle time. */
export const Label: React.FC<{ x: number; y: number; text: string; color?: string; size?: number; o?: number; anchor?: "middle" | "start" | "end"; weight?: number; font?: string }> =
  ({ x, y, text, color = C.paper, size = 40, o = 1, anchor = "middle", weight = 700, font = DISPLAY }) => {
    if (size < LAYOUT.minText) throw new Error(`Label "${text}" is ${size}px (< ${LAYOUT.minText}px rule)`);
    return <text x={x} y={y} fill={color} fontSize={size} fontFamily={font} fontWeight={weight} textAnchor={anchor} opacity={o}
      style={{ paintOrder: "stroke", stroke: C.ink, strokeWidth: 6, strokeLinejoin: "round" }}>{text}</text>;
  };

export const Pill: React.FC<{ x: number; y: number; w: number; text: string; color: string; s: number; textColor?: string }> = ({ x, y, w, text, color, s, textColor = C.ink }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`} opacity={Math.min(1, s)}>
    <rect x={-w / 2} y={-38} width={w} height={76} rx={38} fill={color} />
    <text y={14} fill={textColor} fontSize={40} fontFamily={DISPLAY} fontWeight={700} textAnchor="middle">{text}</text>
  </g>
);

/** Full-stage SVG layer for artwork. */
export const Stage: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <svg width={1080} height={1920} style={{ position: "absolute", overflow: "visible" }}>{children}</svg>
);
