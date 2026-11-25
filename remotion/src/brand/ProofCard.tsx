import React from "react";
import { Img, staticFile } from "remotion";
import { C, DISPLAY, MONO } from "./tokens";
import { PROBE, PROBE_KEY } from "./Kit";
import { EASE, ease } from "./timing";
import { useG } from "./frame";

/** Look A real-photo proof card: amber brand border, Ken Burns pan/zoom, dashed focus box, >= 30 px credit. */
export const ProofCard: React.FC<{
  src: string;
  tag: string;
  credit: string;
  aspect?: number;
  focus?: [number, number, number, number];
  focusLabel?: string;
  startFrame: number;
  duration?: number;
  y?: number;
  /** r5: CSS filter for dark archival photos, e.g. "brightness(1.35) contrast(1.15)" */
  treat?: string;
}> = ({ src, tag, credit, aspect = 1, focus, focusLabel, startFrame, duration = 66, y = 450, treat }) => {
  const f = useG();
  // r5 (Emil): ease-out entry from 0.94 + 40 px rise over 12 f, no spring wobble on a large card; inner photo lags 3 f (stagger)
  const sOut = EASE.OUT(Math.min(1, Math.max(0, (f - startFrame) / 12)));
  const sPhoto = EASE.OUT(Math.min(1, Math.max(0, (f - startFrame - 3) / 12)));
  const kb = 1.0 + 0.07 * ease(f, startFrame, startFrame + duration);
  const panX = (ease(f, startFrame, startFrame + duration) - 0.5) * -14;
  const dash = ease(f, startFrame + 6, startFrame + 22);
  // r5 Shorts safe zone: keep the whole card (incl. credit + backing) left of the right-hand button column (x <= 900)
  const W = 760;
  const H = Math.min(540, Math.round(W / aspect));
  const x = 100;
  return (
    <div style={{ position: "absolute", left: x, top: y, width: W, transform: `scale(${0.94 + 0.06 * sOut}) translateY(${(1 - sOut) * 40}px)`, opacity: Math.min(1, sOut * 1.6) }}>
      <div style={{ position: "absolute", left: -24, top: -96, width: W + 48, height: H + 210, borderRadius: 34, background: "rgba(13,14,18,0.88)" }} />
      <div style={{ position: "absolute", left: 0, top: -76, display: "flex", gap: 16, alignItems: "center", whiteSpace: "nowrap" }}>
        <div style={{ background: C.amber, color: PROBE ? PROBE_KEY : C.ink, fontFamily: DISPLAY, fontWeight: 700, fontSize: 36, padding: "6px 24px", borderRadius: 40 }}>REAL PHOTO</div>
        <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 38, color: PROBE ? PROBE_KEY : C.paper }}>{tag}</div>
      </div>
      <div style={{ position: "relative", width: W, height: H, borderRadius: 24, overflow: "hidden", border: `6px solid ${C.amber}`, background: C.ink2, boxShadow: "0 20px 52px rgba(0,0,0,0.65)" }}>
        <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${kb * (1.04 - 0.04 * sPhoto)}) translateX(${panX}px)`, transformOrigin: "55% 55%", filter: treat, opacity: sPhoto }} />
        {focus && (
          <svg width={W} height={H} style={{ position: "absolute", left: 0, top: 0 }}>
            <rect x={focus[0] * W} y={focus[1] * H} width={(focus[2] - focus[0]) * W} height={(focus[3] - focus[1]) * H}
              rx={14} fill="none" stroke={C.amber} strokeWidth={8} strokeDasharray="24 14" opacity={dash} />
          </svg>
        )}
      </div>
      {focusLabel && focus && (
        <div style={{
          position: "absolute",
          left: Math.min(focus[0] * W, W - focusLabel.length * 22 - 44),
          top: Math.max(8, focus[1] * H - 62),
          fontFamily: DISPLAY, fontWeight: 700, fontSize: 34,
          color: PROBE ? PROBE_KEY : C.ink, background: C.amber, padding: "4px 18px", borderRadius: 28,
          opacity: ease(f, startFrame + 10, startFrame + 18),
        }}>{focusLabel}</div>
      )}
      <div style={{ position: "relative", marginTop: 18, width: W, fontFamily: MONO, fontWeight: 500, fontSize: 30, color: PROBE ? PROBE_KEY : C.paper, lineHeight: 1.25 }}>{credit}</div>
    </div>
  );
};
