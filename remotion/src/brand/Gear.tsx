import React from "react";
import { C } from "./tokens";

export const gearPath = (r: number, teeth = 10, depth = 0.22) => {
  const pts: string[] = [];
  const n = teeth * 4;
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2;
    const rr = i % 4 < 2 ? r : r * (1 - depth);
    pts.push(`${(Math.cos(a) * rr).toFixed(2)},${(Math.sin(a) * rr).toFixed(2)}`);
  }
  return `M${pts.join("L")}Z`;
};
/** Gear drawn inside an existing <svg>. */
export const GearG: React.FC<{ r: number; color: string; rot?: number; hole?: string }> = ({ r, color, rot = 0, hole = C.ink }) => (
  <g transform={`scale(${r / 46}) rotate(${rot})`}>
    <path d={gearPath(46, 10, 0.2)} fill={color} />
    <circle r={17} fill={hole} />
    <circle r={7} fill={color} />
  </g>
);
/** Standalone gear (its own <svg>). */
export const Gear: React.FC<{ size: number; color: string; rot?: number; hole?: string }> = ({ size, color, rot = 0, hole }) => (
  <svg width={size} height={size} viewBox="-50 -50 100 100" style={{ overflow: "visible" }}>
    <GearG r={46} color={color} rot={rot} hole={hole} />
  </svg>
);
