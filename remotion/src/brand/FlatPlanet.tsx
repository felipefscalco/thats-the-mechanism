import React from "react";

/** r5 flat 2D planet (replaces the three.js Planet in Sky: ~3x faster render, matches the flat Look A / mg Flat Vector bar).
 *  Land strips scroll inside a circular clip (classic flat-vector globe), slight horizontal squeeze near the limb fakes curvature;
 *  a flat night half (sun on the right) and a thin atmosphere rim. Pure function of `f`. */
const BLOBS: [number, number, number, number][] = [ // [x, y, w, h] in units of r (strip width 4r)
  [0.1, -0.55, 0.9, 0.5], [0.35, 0.05, 0.55, 0.75], [1.4, -0.7, 1.1, 0.45], [1.6, -0.2, 0.5, 0.9], [2.55, 0.1, 0.8, 0.5],
  [2.9, -0.6, 0.6, 0.35], [3.3, 0.45, 0.45, 0.3], [1.1, 0.6, 0.4, 0.22],
];
// organic continent: 14 radial vertices with seeded noise, joined by quadratic midpoints (smooth, flat-vector friendly)
const rnd = (k: number) => { const x = Math.sin(k * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const blobPath = (x: number, y: number, w: number, h: number, seed = 1) => {
  const cx = x + w / 2, cy = y + h / 2, n = 14;
  const pts = Array.from({ length: n }, (_, i) => {
    const a = (i / n) * Math.PI * 2, k = 0.72 + 0.42 * rnd(seed * 31 + i) + 0.18 * Math.sin(a * 3 + seed);
    return [cx + Math.cos(a) * (w / 2) * k, cy + Math.sin(a) * (h / 2) * k] as const;
  });
  const mid = (a: readonly [number, number], b: readonly [number, number]) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  const m0 = mid(pts[n - 1], pts[0]);
  let d = `M${m0[0]},${m0[1]}`;
  for (let i = 0; i < n; i++) { const m = mid(pts[i], pts[(i + 1) % n]); d += ` Q${pts[i][0]},${pts[i][1]} ${m[0]},${m[1]}`; }
  return d + " Z";
};

export const FlatPlanet: React.FC<{ x: number; y: number; r: number; f: number; land?: string; sea?: string; speed?: number; id?: string }> =
  ({ x, y, r, f, land = "#6CC47F", sea = "#2D7FB0", speed = 0.9, id = "fp" }) => {
    const strip = 4 * r;
    const off = -((f * speed) % strip);
    return (
      <g transform={`translate(${x} ${y})`}>
        <defs><clipPath id={`${id}-c`}><circle r={r} /></clipPath></defs>
        <circle r={r + 16} fill="#7FC8FF" opacity={0.18} />
        <g clipPath={`url(#${id}-c)`}>
          <circle r={r} fill={sea} />
          {[0, 1].map((k) => (
            <g key={k} transform={`translate(${off + k * strip - r} 0) scale(${r} ${r})`}>
              {BLOBS.map((b, i) => <path key={i} d={blobPath(b[0], b[1], b[2], b[3], i + 1)} fill={land} />)}
              <rect x={0} y={-1.02} width={4} height={0.16} fill="#EAF6FF" opacity={0.9} /><rect x={0} y={0.88} width={4} height={0.16} fill="#EAF6FF" opacity={0.9} />
            </g>
          ))}
          <circle r={r} fill="none" stroke="#0D0E12" strokeOpacity={0.18} strokeWidth={r * 0.22} />
          {/* night side: flat shape, sun to the right */}
          <path d={`M0,${-r} A${r},${r} 0 0 0 0,${r} A${r * 0.42},${r} 0 0 1 0,${-r} Z`} fill="#0D0E12" opacity={0.42} />
          {/* flat highlight */}
          <ellipse cx={r * 0.38} cy={-r * 0.42} rx={r * 0.22} ry={r * 0.12} fill="white" opacity={0.18} transform={`rotate(-30 ${r * 0.38} ${-r * 0.42})`} />
        </g>
      </g>
    );
  };
