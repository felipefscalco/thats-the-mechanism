import React from "react";
import { useVideoConfig } from "remotion";
import words from "../../../episodes/01-qr-code/captions.json";
import qr from "../qr-matrix.json";
import { ScanLine } from "lucide-react";
import { Badge, C, Enter, EpisodeShell, GearG, Label, LOOP_FRAMES, MONO, PILLARS, Pill, ProofCard, Shot, Stage, TagLabel, TitleHook, cue, ease, makeAt, pop, useG } from "../brand";

const P = PILLARS.tech;
const N = qr.n;
const W = 1080, CY = 790;
const isFinder = (r: number, c: number) => (r < 7 && c < 7) || (r < 7 && c >= N - 7) || (r >= N - 7 && c < 7);
/** Data/EC module: never a finder, separator, format strip, timing line or the logo box. */
const isDataMod = (r: number, c: number) =>
  !((r < 9 && c < 9) || (r < 9 && c >= N - 8) || (r >= N - 8 && c < 9)) && r !== 6 && c !== 6 && !(r > 10 && r < 26 && c > 10 && c < 26);

type Fx = (r: number, c: number, dark: boolean) => 0 | 1 | 2; // 1 = punched-out hole (red hatch), 2 = amber flip

/** Real level-H QR for youtube.com/@thatsthemechanism (it actually scans in the render). */
const QRCard: React.FC<{
  cx: number; cy: number; size: number; logo?: number; finderGlow?: number; coverTL?: number; shake?: number; rot?: number;
  fx?: Fx; overlay?: (g: { m: number }) => React.ReactNode; tilt?: number; zoom?: number;
}> = ({ cx, cy, size, logo = 0, finderGlow = 0, coverTL = 0, shake = 0, rot = 0, fx, overlay, tilt = 0, zoom = 1 }) => {
  const f = useG();
  const pad = size * 0.08, m = (size - 2 * pad) / N;
  const logoW = Math.sqrt(logo) * (size - 2 * pad);
  const sx = shake * Math.sin(f * 2.1) * 14;
  return (
    <g transform={`translate(${cx + sx} ${cy}) rotate(${tilt}) scale(${zoom}) translate(${-size / 2} ${-size / 2})`}>
      <rect x={6} y={14} width={size} height={size} rx={28} fill="#000" opacity={0.35} />
      <rect width={size} height={size} rx={28} fill={C.paper} />
      <g transform={`translate(${pad} ${pad})`}>
        {fx && (
          <defs>
            <pattern id="qrhatch" width={10} height={10} patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
              <rect width={10} height={10} fill="#F6D9D4" /><rect width={5} height={10} fill={C.red} />
            </pattern>
          </defs>
        )}
        {qr.rows.map((row, r) => row.split("").map((v, c) => {
          const dark = v === "1", s = fx ? fx(r, c, dark) : 0;
          if (s === 1) return <rect key={`${r}-${c}`} x={c * m} y={r * m} width={m + 0.6} height={m + 0.6} fill="url(#qrhatch)" />;
          if (s === 2 && dark) return <rect key={`${r}-${c}`} x={c * m} y={r * m} width={m + 0.6} height={m + 0.6} fill={C.amber} />;
          return dark ? <rect key={`${r}-${c}`} x={c * m} y={r * m} width={m + 0.6} height={m + 0.6} fill={isFinder(r, c) && finderGlow > 0 ? P.color : C.ink} /> : null;
        }))}
        {finderGlow > 0 && [[0, 0], [0, N - 7], [N - 7, 0]].map(([r, c], i) => (
          <rect key={i} x={c * m - 10} y={r * m - 10} width={7 * m + 20} height={7 * m + 20} rx={12} fill="none" stroke={P.color} strokeWidth={6} opacity={finderGlow * (0.6 + 0.4 * Math.sin(f / 4))} />
        ))}
        {overlay && overlay({ m })}
        {logo > 0 && (
          <g transform={`translate(${(N * m) / 2} ${(N * m) / 2})`}>
            <rect x={-logoW / 2} y={-logoW / 2} width={logoW} height={logoW} rx={logoW * 0.18} fill={C.ink} stroke={C.paper} strokeWidth={8} />
            <GearG r={logoW * 0.34} color={C.amber} rot={rot} />
          </g>
        )}
        {coverTL > 0 && <rect x={-pad} y={-pad} width={(9 * m + pad) * coverTL} height={9 * m + pad} rx={18} fill="#2B2F3A" />}
      </g>
    </g>
  );
};

const Viewfinder: React.FC<{ cx: number; cy: number; size: number; color: string; o: number; jitter?: number }> = ({ cx, cy, size, color, o, jitter = 0 }) => {
  const f = useG();
  const h = size / 2 + 26 + Math.sin(f / 3) * jitter * 20, L = 64;
  return (
    <g transform={`translate(${cx + jitter * Math.sin(f * 1.7) * 30} ${cy + jitter * Math.cos(f * 1.3) * 20})`} opacity={o}>
      {[[-1, -1], [1, -1], [-1, 1], [1, 1]].map(([dx, dy], i) => (
        <path key={i} d={`M${dx * h} ${dy * (h - L)} L${dx * h} ${dy * h} L${dx * (h - L)} ${dy * h}`} stroke={color} strokeWidth={10} fill="none" strokeLinecap="round" />
      ))}
    </g>
  );
};

const bytesOf = "youtube.com/@thatsthemechanism".split("").slice(0, 12).map((ch) => ch.charCodeAt(0).toString(16).toUpperCase());

/** Shot 1 = scale reveal (frame 0 is zoomed 2.0x into the bright QR + gear; LoopBack freezes this at frame 0). */
const HookTitle: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  return <TitleHook t={["THE CODE THAT", "REPAIRS", "ITSELF"]} top={280} o={f < at("When the code") - 3 ? 1 : 0} />;
};
const Hook: React.FC<{ title?: boolean }> = ({ title = false }) => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const cam = at("Your camera"), rep = at("repairs"), its = at("itself.");
  const z = ease(f, 3, 62, 2.0, 1.0);
  const cx = W / 2, cy = CY;
  // three module patches blink out on "repairs" and snap back amber -> ink on "itself." (never finders, logo, timing)
  const patch = (r: number, c: number) =>
    (r >= 12 && r <= 14 && c >= 8 && c <= 11) || (r >= 26 && r <= 28 && c >= 25 && c <= 28) || (r >= 3 && r <= 5 && c >= 15 && c <= 20);
  const fx: Fx = (r, c) => {
    if (!patch(r, c) || f < rep) return 0;
    if (f < its) return 1;
    return f < its + 9 ? 2 : 0;
  };
  return (
    <>
      <Stage>
        <g transform={`translate(${cx} ${cy}) scale(${z}) translate(${-cx} ${-cy})`}>
          <QRCard cx={cx} cy={cy} size={500} logo={0.12} rot={f * 2} fx={fx} />
          <Viewfinder cx={cx} cy={cy} size={500} color={f > cam ? C.green : C.paper} o={ease(f, cam - 6, cam + 2)} />
          {f > cam && <rect x={cx - 270} y={cy - 270 + ((f - cam) * 28) % 540} width={540} height={6} fill={C.green} opacity={0.85} />}
        </g>
      </Stage>
      {title && <HookTitle />}
    </>
  );
};

/** Screen-space verdict pill (outside the camera). */
const Verdict: React.FC<{ phrase: string; text: string; color: string; w?: number }> = ({ phrase, text, color, w = 420 }) => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const a = at(phrase);
  if (f < a) return null;
  return <Stage><Pill x={W / 2} y={1152} w={w} text={text} color={color} icon={ScanLine} s={pop(f, a, fps)} /></Stage>;
};

/** A hex/plus chip: backing + text drawn as one unit (scale only, always opaque). */
const Chip: React.FC<{ x: number; y: number; sc?: number; fill: string; stroke?: string; text: string; tc: string; size?: number }> = ({ x, y, sc = 1, fill, stroke, text, tc, size = 34 }) => (
  <g transform={`translate(${x + 50} ${y + 40}) scale(${sc})`}>
    <rect x={-50} y={-40} width={100} height={80} rx={14} fill={fill} stroke={stroke} strokeWidth={stroke ? 4 : 0} />
    <Label x={0} y={size * 0.35} color={tc} font={MONO} size={size} weight={700} anchor="middle" text={text} outline={false} />
  </g>
);

const Bytes: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s2 = at("When the code"), cut = at("cut into bytes"), adds = at("adds extra bytes"), calc = at("calculated"),
    dat = at("data itself."), rs = at("Reed-Solomon"), cd = at("scratched CDs");
  const url = "youtube.com/@thatsthemechanism";
  const typeStart = s2 + 2, step = 2.3;
  const typed = Math.max(0, Math.min(url.length, Math.floor((f - typeStart) / step)));
  const cursor = Math.floor(f / 8) % 2 === 0 ? "_" : " ";
  const colX = (i: number) => 130 + (i % 6) * 120;
  const dY = (i: number) => 455 + Math.floor(i / 6) * 100, rY = (i: number) => 770 + Math.floor(i / 6) * 100;
  const sweep = f > cut + 10 ? (f * 0.3) % 14 : -9;
  return (
    <Stage>
      {f >= s2 + 2 && <Label x={130} y={340} color={C.paper} font={MONO} size={36} weight={700} anchor="start" text={url.slice(0, typed) + (typed < url.length || f < cut + 20 ? cursor : "")} />}
      {f >= dat && <Label x={130} y={430} text="DATA" anchor="start" size={30} color={P.color} o={ease(f, dat, dat + 6)} />}
      {/* arcs data -> repair */}
      {f >= adds + 6 && Array.from({ length: 6 }).map((_, i) => {
        const x1 = colX(i) + 50, x2 = colX((i + 1) % 6) + 50, y1 = dY(6) + 80, y2 = rY(0);
        const p = ease(f, adds + 6 + i * 3, adds + 22 + i * 3);
        return <path key={i} d={`M${x1} ${y1} C${x1} ${y1 + 70} ${x2} ${y2 - 70} ${x2} ${y2}`} fill="none" stroke={C.amber} strokeWidth={f >= calc ? 7 : 4}
          strokeDasharray="14 12" strokeDashoffset={-f * 4} strokeLinecap="round" opacity={p > 0 ? 0.55 + 0.45 * (f >= calc ? 1 : 0) : 0} />;
      })}
      {bytesOf.map((b, i) => {
        const land = typeStart + i * step + 14, spawn = typeStart + i * step;
        if (f < spawn) return null;
        const x = colX(i), y = dY(i);
        if (f < land) {
          const t = ease(f, spawn, land), sx = 130 + i * 21.6 - 40;
          const t2 = 0.6 + 0.4 * t;
          return <rect key={i} x={sx + (x - sx) * t + 50 - 50 * t2} y={300 + (y - 300) * t - Math.sin(t * Math.PI) * 24 + 40 - 40 * t2} width={100 * t2} height={80 * t2} rx={14} fill={C.ink2} stroke={P.color} strokeWidth={4} />;
        }
        const pl = f > cut ? Math.max(0, Math.sin((f - cut) * 0.22 - i * 0.55)) : 0;
        const sw = Math.max(0, 1 - Math.abs(((i % 6) - sweep)) / 1.6) * (f > cut + 10 ? 1 : 0);
        const hot = pl > 0.7 || sw > 0.5;
        return <Chip key={i} x={x} y={y} sc={(1 + 0.08 * Math.max(pl, sw)) * (f < land + 8 ? 1 + 0.12 * Math.sin((f - land) / 8 * Math.PI) : 1)}
          fill={hot ? "#233648" : C.ink2} stroke={hot ? C.amber : P.color} text={b} tc={C.paper} />;
      })}
      {f >= adds && f < cd && <Label x={130} y={1005} text="REPAIR BYTES" anchor="start" size={30} color={C.amber} o={ease(f, adds, adds + 6)} />}
      {f >= dat && f < cd && <Label x={830} y={1005} text="= f(DATA)" anchor="end" size={30} color={C.amber} o={ease(f, dat, dat + 6)} />}
      {Array.from({ length: 12 }).map((_, i) => {
        const t0 = adds + i * 1.6;
        if (f < t0) return null;
        const k = ease(f, t0, t0 + 10), drop = (1 - k) * -60;
        return <Chip key={i} x={colX(i)} y={rY(i) + drop} sc={0.62 + 0.38 * k} fill={C.amber} text="+" tc={C.ink} size={40} />;
      })}
      {f >= rs && f < cd && <Label x={W / 2} y={1110} text="REED-SOLOMON (1960)" size={40} color={C.paper} o={ease(f, rs, rs + 6)} />}
      {f >= rs && f < rs + 120 && (
        <circle cx={130 + ((f - rs) * 14) % 700} cy={f % 2 ? dY(0) + 40 : rY(0) + 40} r={10} fill={C.amber} />
      )}
      {f >= cd && (
        <Badge x={W / 2} y={1060} o={ease(f, cd, cd + 8)} text="STILL PLAYING" tx={-150} ty={14} size={44} color={C.amber} anchor="start">
          <rect x={-320} y={-68} width={640} height={136} rx={24} fill={C.ink2} stroke={C.amber} strokeWidth={4} />
          <g transform={`translate(-230 0) rotate(${f * 8})`}>
            <circle r={48} fill={C.paper} opacity={0.9} /><circle r={15} fill={C.ink} />
            <line x1={-36} y1={-16} x2={36} y2={16} stroke={C.red} strokeWidth={5} />
          </g>
        </Badge>
      )}
    </Stage>
  );
};

/** Hero blobs: [row, col] centres of punched-out areas (data/EC modules only), radius in modules. */
const BLOBS: [number, number][] = [[3, 14], [3, 23], [14, 4], [14, 32], [27, 12], [28, 26]];
const BR = 3.8;

const Repair: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s3 = at("Those extra bytes"), rec = at("recipe"), reb = at("rebuilding"), hi = at("At the highest"), lvl = at("H,"),
    scn = at("scanner"), rest = at("restore about 30%"), p30 = at("30%"), s4 = at("So a logo");
  const mode = f < hi ? 0 : 1;
  const dead = [2, 5, 7];
  const cellPos = (i: number) => [115 + (i % 5) * 172, 370 + Math.floor(i / 5) * 145] as const;
  const punch = (i: number) => scn + i * 4;
  const fix = (i: number) => rest + 6 + i * 13;

  const fx: Fx = (r, c, dark) => {
    if (!isDataMod(r, c)) return 0;
    for (let i = 0; i < BLOBS.length; i++) {
      const d = Math.hypot(r - BLOBS[i][0], c - BLOBS[i][1]);
      if (d > BR) continue;
      if (f < punch(i)) return 0;
      if (f < punch(i) + 6 && (f % 2 === 0)) return 0; // glitch flicker as it is punched out
      const t = fix(i) + d * 1.2;
      if (f < t) return 1;
      return f < t + 7 && dark ? 2 : 0;
    }
    return 0;
  };
  const overlay = ({ m }: { m: number }) => {
    const g = (N * m) / 2;
    const bc = (i: number) => [BLOBS[i][1] * m + m / 2, BLOBS[i][0] * m + m / 2] as const;
    return (
      <g>
        {BLOBS.map((_, i) => {
          if (f < punch(i) + 4 || f > fix(i) + 18) return null;
          const [bx, by] = bc(i);
          const qx = (g + bx) / 2 - (by - g) * 0.3, qy = (g + by) / 2 + (bx - g) * 0.3;
          const path = `M${g} ${g} Q${qx} ${qy} ${bx} ${by}`;
          const sh = f >= fix(i) ? ease(f, fix(i), fix(i) + 14) : 0;
          return (
            <g key={i}>
              <path d={path} fill="none" stroke={C.amber} strokeWidth={7} strokeDasharray="16 12" strokeDashoffset={-f * 3} strokeLinecap="round" opacity={0.95} />
              {[0, 1, 2].map((k) => {
                const t0 = fix(i) - 18 + k * 5, t = (f - t0) / 14;
                if (t <= 0 || t >= 1) return null;
                const u = ease(f, t0, t0 + 14), px = (1 - u) * (1 - u) * g + 2 * (1 - u) * u * qx + u * u * bx, py = (1 - u) * (1 - u) * g + 2 * (1 - u) * u * qy + u * u * by;
                return <rect key={k} x={px - 15} y={py - 15} width={30} height={30} rx={7} fill={C.amber} stroke={C.ink} strokeWidth={3} transform={`rotate(${f * 12} ${px} ${py})`} />;
              })}
              {sh > 0 && sh < 1 && <circle cx={bx} cy={by} r={BR * m * (0.4 + sh * 0.9)} fill="none" stroke={C.amber} strokeWidth={8 * (1 - sh) + 1} />}
            </g>
          );
        })}
        {[[0, 0], [0, N - 7], [N - 7, 0]].map(([r, c], i) => (
          f >= scn && <rect key={i} x={c * m - m} y={r * m - m} width={9 * m} height={9 * m} rx={10} fill="none" stroke={P.color} strokeWidth={6} />
        ))}
      </g>
    );
  };
  const hs = f - hi;
  const zoom = (0.88 + 0.12 * ease(f, hi, hi + 14)) * (1 + 0.06 * ease(f, rest, s4));
  const tilt = 2 * Math.sin(hs / 16);
  const qcy = 720, qs = 640;
  const beam = ((f - scn) * 11) % qs;

  return (
    <Stage>
      {mode === 0 && (
        <g transform={`translate(${44 * Math.sin((f - s3) / 13)} ${20 * Math.sin((f - s3) / 8)})`}>
          {Array.from({ length: 10 }).map((_, i) => {
            const [x, y] = cellPos(i), isDead = dead.includes(i), k = dead.indexOf(i);
            const rebuilt = isDead && f >= reb + k * 12 + 14;
            const gl = isDead && !rebuilt && f % 4 < 2 ? ((i % 3) - 1) * 6 : 0;
            const pulse = rebuilt ? 1 + 0.05 * Math.sin((f - reb) / 3 + i) : 1;
            return (
              <g key={i} transform={`translate(${x + gl + 72} ${y + 58}) scale(${pulse}) translate(-72 -58)`}>
                <rect width={144} height={116} rx={16} fill={rebuilt ? C.amber : isDead ? C.ink : C.ink2} stroke={isDead && !rebuilt ? C.red : rebuilt ? C.amber : P.color} strokeWidth={4} strokeDasharray={isDead && !rebuilt ? "12 10" : undefined} />
                {isDead && !rebuilt && <path d="M46 30 L98 86 M98 30 L46 86" stroke={C.red} strokeWidth={6} strokeLinecap="round" />}
              </g>
            );
          })}
          {/* amber tray + recipe ring */}
          <rect x={440} y={800} width={200} height={90} rx={22} fill={C.amber} />
          <circle cx={540} cy={845} r={30} fill="none" stroke={C.ink} strokeWidth={6} />
          {f >= rec && [0, 1].map((k) => {
            const t = ((f - rec + k * 20) % 40) / 40;
            return <circle key={k} cx={540} cy={845} r={40 + t * 60} fill="none" stroke={C.amber} strokeWidth={8 * (1 - t) + 1} />;
          })}
          {dead.map((d, k) => {
            const [x, y] = cellPos(d), t0 = reb + k * 12, u = ease(f, t0, t0 + 14);
            if (f < t0 || f >= t0 + 14) return null;
            const ex = x + 72, ey = y + 58, qx = (540 + ex) / 2 + (k - 1) * 120, qy = 600;
            const px = (1 - u) * (1 - u) * 540 + 2 * (1 - u) * u * qx + u * u * ex, py = (1 - u) * (1 - u) * 845 + 2 * (1 - u) * u * qy + u * u * ey;
            return <rect key={k} x={px - 24} y={py - 24} width={48} height={48} rx={10} fill={C.amber} stroke={C.ink} strokeWidth={4} transform={`rotate(${f * 14} ${px} ${py})`} />;
          })}
          {f < reb && <Label x={W / 2} y={700} text="BYTES GO MISSING" size={46} color={C.red} o={ease(f, s3, s3 + 6)} />}
          {f >= reb && <Label x={W / 2} y={700} text="MISSING BYTES: REBUILT" size={46} color={C.amber} o={ease(f, reb, reb + 6)} />}
        </g>
      )}
      {mode === 1 && (
        <g>
          <Enter p={pop(f, hi, fps)} cx={W / 2} cy={qcy}>
            <QRCard cx={W / 2} cy={qcy} size={qs} logo={0.12} rot={f * 1.8} fx={fx} overlay={overlay} tilt={tilt} zoom={zoom} />
          </Enter>
          {f >= scn && <Viewfinder cx={W / 2} cy={qcy} size={qs} color={C.green} o={ease(f, scn, scn + 6)} />}
          {f >= scn && <rect x={W / 2 - qs / 2 + 20} y={qcy - qs / 2 + 20 + (beam < qs - 40 ? beam : qs - 40)} width={qs - 40} height={6} rx={3} fill={C.green} opacity={0.8} />}
          {f >= lvl && <TagLabel x={W / 2} y={335} text="LEVEL H" size={36} color={C.amber} o={ease(f, lvl, lvl + 8)} />}
          {f >= p30 && <Label x={W / 2} y={1150} text="30% REBUILDABLE" size={42} color={C.amber} o={ease(f, p30, p30 + 8)} />}
        </g>
      )}
    </Stage>
  );
};

/** Shot 4: logo budget bar (ripple repair), then real torn-QR ProofCard with GLARE + SCRATCHES eating the same 30 % bar. */
const Budget: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s4 = at("So a logo"), dmg = at("damage the code"), p15 = at("15%"), safe = at("is safe."), gl = at("Glare"), sc = at("scratches"), same = at("same budget"), s5 = at("But cover");
  const showPhoto = f >= gl;
  const g15 = ease(f, p15 - 6, p15 + 10);
  const logoA = 0.04 + 0.11 * ease(f, s4, s4 + 18) + 0.03 * g15;
  // ring of data modules around the logo flips amber then repairs itself, ripple travelling outward
  const fx: Fx = (r, c, dark) => {
    if (!dark || !isDataMod(r, c) && !(r > 10 && r < 26 && c > 10 && c < 26)) return 0;
    const d = Math.hypot(r - 18, c - 18);
    if (d < 7 || d > 13) return 0;
    const w = ((f - s4) * 0.18 - d * 0.35) % 2.4;
    return w >= 0 && w < 0.5 ? 2 : 0;
  };
  const barX = 110, barW = 860, barY = 1040;
  const ring = f >= safe ? ease(f, safe, safe + 20) : 0;
  const pb = 1070;
  const segG = 200 * ease(f, gl, gl + 12), segS = 180 * ease(f, sc, sc + 12);
  return (
    <>
      {!showPhoto && (
        <Stage>
          <QRCard cx={W / 2} cy={650} size={580} logo={logoA} rot={f * 1.4} fx={fx} tilt={1.5 * Math.sin((f - s4) / 20)} />
          {ring > 0 && ring < 1 && <circle cx={W / 2} cy={650} r={60 + ring * 300} fill="none" stroke={C.green} strokeWidth={10 * (1 - ring) + 2} />}
          {f >= dmg && f < p15 && <Label x={W / 2} y={1000} text="PLANNED-FOR DAMAGE" size={42} color={C.amber} o={ease(f, dmg, dmg + 6)} />}
          {f >= p15 && <Label x={W / 2} y={1000} text="LOGO ≈ 15% OF AREA" size={42} color={C.green} o={ease(f, p15, p15 + 6)} />}
          <rect x={barX} y={barY} width={barW} height={42} rx={21} fill={C.ink2} stroke={C.line} strokeWidth={4} />
          <rect x={barX + 4} y={barY + 4} width={Math.max(0, (barW - 8) * (logoA / 0.3))} height={34} rx={17} fill={C.green} />
          <Label x={barX} y={barY + 86} text="REPAIR BUDGET: 30%" anchor="start" size={32} color={C.paper} />
        </Stage>
      )}
      {showPhoto && (
        <>
          <ProofCard src="photos/01-qr-code--qr-code-damaged.jpg" tag="TORN, STILL A CODE"
            credit="PHOTO: BOBMATH (WIKIMEDIA COMMONS) · CC0" aspect={1.8}
            focus={[0.58, 0.52, 0.96, 0.96]} focusLabel="MISSING CHUNK" y={390}
            startFrame={gl} duration={Math.max(45, s5 - gl)} />
          <Stage>
            <rect x={barX} y={pb} width={barW} height={42} rx={21} fill={C.ink2} stroke={C.line} strokeWidth={4} />
            <rect x={barX + 4} y={pb + 4} width={segG} height={34} rx={17} fill={C.red} />
            <rect x={barX + 4 + 200} y={pb + 4} width={segS} height={34} rx={17} fill={C.amber} />
            <TagLabel x={128} y={pb - 34} text="GLARE" size={30} color={C.paper} anchor="start" o={ease(f, gl, gl + 8)} />
            {f >= sc && <TagLabel x={326} y={pb - 34} text="SCRATCHES" size={30} color={C.paper} anchor="start" o={ease(f, sc, sc + 8)} />}
            {f >= same && <TagLabel x={598} y={pb - 34} text="SAME 30% BUDGET" size={30} color={C.amber} anchor="start" o={ease(f, same, same + 8)} />}
          </Stage>
        </>
      )}
    </>
  );
};

const Finders: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const three = at("three big"), corner = at("corner squares"), over = at("it's over"), notData = at("Those aren't data"), dat = at("data.", 1) ,
    hop1 = at("They're"), hop2 = at("your camera", 1), hop3 = at("finds");
  const cov = f < dat ? ease(f, three, three + 12) : ease(f, dat, dat + 10, 1, 0);
  const shk = f >= over && f < over + 26 ? 1 - (f - over) / 26 : 0;
  const qs = 520, pad = qs * 0.08, m = (qs - 2 * pad) / N, cx = W / 2, cy = 740;
  const fc = (r: number, c: number) => [cx - qs / 2 + pad + (c + 3.5) * m, cy - qs / 2 + pad + (r + 3.5) * m] as const;
  const spots = [fc(0, 0), fc(0, N - 7), fc(N - 7, 0)];
  const hopT = f >= hop3 ? 2 : f >= hop2 ? 1 : 0;
  const tgt = spots[hopT], prevSpot = spots[Math.max(0, hopT - 1)];
  const lastHop = hopT === 2 ? hop3 : hopT === 1 ? hop2 : hop1;
  const hk = ease(f, lastHop, lastHop + 6);
  const rx = prevSpot[0] + (tgt[0] - prevSpot[0]) * hk, ry = prevSpot[1] + (tgt[1] - prevSpot[1]) * hk;
  const rh = 3.5 * m + 22;
  const wob = 1 + 0.04 * Math.sin(f / 2);
  return (
    <Stage>
      <QRCard cx={cx} cy={cy} size={qs} logo={0.13} finderGlow={ease(f, notData, notData + 8)} coverTL={cov} shake={shk} rot={f} tilt={f > notData ? 1.2 * Math.sin(f / 14) : 0} />
      {f < over && <Viewfinder cx={cx} cy={cy} size={qs} color={C.paper} o={1} />}
      {f >= over && <Enter p={pop(f, over, fps)} cx={cx} cy={cy}><Viewfinder cx={cx} cy={cy} size={qs} color={C.red} o={1} jitter={shk} /></Enter>}
      {f >= hop1 && (
        <g transform={`translate(${rx} ${ry}) scale(${wob})`}>
          {[[-1, -1], [1, -1], [-1, 1], [1, 1]].map(([dx, dy], i) => (
            <path key={i} d={`M${dx * rh} ${dy * (rh - 26)} L${dx * rh} ${dy * rh} L${dx * (rh - 26)} ${dy * rh}`} stroke={C.green} strokeWidth={8} fill="none" strokeLinecap="round" />
          ))}
        </g>
      )}
      {f >= corner && f < over && <TagLabel x={W / 2} y={400} text="CORNER SQUARE = FINDER" size={36} color={C.paper} o={ease(f, corner, corner + 8)} />}
      {f >= over && f < dat - 6 && (
        <Badge x={W / 2} y={395} o={ease(f, over, over + 8)} text="NO SCAN" tx={0} ty={22} size={64} color={C.ink}>
          <rect x={-280} y={-60} width={560} height={120} rx={24} fill={C.red} />
        </Badge>
      )}
      {f >= dat && <TagLabel x={W / 2} y={400} text="FINDER PATTERNS ≠ DATA" size={36} color={P.color} o={ease(f, dat, dat + 8)} />}
    </Stage>
  );
};

/** Final shot: repair blocks fly in and DOCK in a settled ring well before the payoff freeze. */
const Final: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const car = at("carries"), own = at("own"), lab = at("spare");
  const wave = ease(f, own, own + 22);
  return (
    <Stage>
      <QRCard cx={W / 2} cy={CY - 40} size={540} logo={0.13} rot={f * 1.6} />
      {wave > 0 && wave < 1 && <circle cx={W / 2} cy={CY - 40} r={40 + wave * 330} fill="none" stroke={C.amber} strokeWidth={22 * (1 - wave) + 2} />}
      {Array.from({ length: 8 }).map((_, i) => {
        const a = (i / 8) * Math.PI * 2 + 0.35, t0 = car + i * 3;
        if (f < t0) return null;
        const u = ease(f, t0, t0 + 14), rr = 900 - 550 * u;
        const x = W / 2 + Math.cos(a) * rr, y = CY - 40 + Math.sin(a) * rr * 0.92;
        const d = f > t0 + 14 ? 1 + 0.25 * Math.max(0, 1 - (f - t0 - 14) / 6) : 1;
        return <rect key={i} x={x - 24} y={y - 24} width={48} height={48} rx={10} fill={C.amber} transform={`rotate(${(1 - u) * 180} ${x} ${y}) translate(${x} ${y}) scale(${d}) translate(${-x} ${-y})`} />;
      })}
      <TagLabel x={W / 2} y={1150} text="SPARE PARTS INCLUDED" size={40} color={C.amber} o={ease(f, lab, lab + 8)} />
    </Stage>
  );
};

export const QRVideo: React.FC = () => {
  const { fps, durationInFrames: D } = useVideoConfig();
  const at = makeAt(words, fps);
  const s2 = at("When the code"), s3 = at("Those extra bytes"), s4 = at("So a logo"), s5 = at("But cover"),
    card = at("That's the mechanism"), fin = at("A QR code carries"), loop = D - LOOP_FRAMES;
  const cut = at("cut into bytes"), adds = at("adds extra bytes"), cd = at("scratched CDs"), reb = at("rebuilding"), hi = at("At the highest"),
    over = at("it's over"), corner = at("three big corner"), gl = at("Glare");
  const cues = [
    cue(4, "swish", 0.92), cue(at("Your camera"), "click", 0.95), cue(at("anyway."), "confirm", 0.92),
    cue(s2 - 5, "whoosh", 0.95), cue(cut, "pop", 0.92), cue(cut + 12, "click", 0.95), cue(adds, "pop3", 0.92),
    cue(at("data itself."), "pop", 0.92), cue(at("error correction"), "click", 0.95), cue(cd, "clank", 0.92),
    cue(s3 - 5, "whoosh", 0.95), cue(s3 + 8, "glitch", 0.92), cue(reb + 2, "confirm", 0.92), cue(hi + 12, "pop", 0.92),
    cue(s4 - 5, "whoosh", 0.95), cue(at("damage the code"), "pop", 0.92), cue(at("15%"), "count", 0.95), cue(at("is safe."), "confirm", 0.92), cue(gl, "pop3", 0.9),
    cue(s5 - 5, "whoosh", 0.95), cue(corner, "pop", 0.92), cue(over, "thud", 0.92), cue(over + 3, "error", 0.9),
    cue(fin + 4, "pop", 0.92),
  ];
  return (
    <EpisodeShell audio="01-qr-code.wav" words={words} pillar={P} ep="001" source="DENSO WAVE"
      backdrop="library/street_wall.jpg" backdropDim={0.42} microGap={36}
      cardAt={card} cardUntil={fin} cues={cues} hook={<Hook title />}
      chapters={[{ at: 0, label: "A LOGO ON A QR" }, { at: s2, label: "BYTES + REPAIR BYTES" }, { at: s3, label: "REBUILDING" }, { at: s4, label: "THE LOGO BUDGET" }, { at: s5, label: "THE CORNERS" }]}>
      <Shot from={0} to={s2} inT="none" outT="push" cam={[{ at: at("Your camera"), kind: "push", s: 1.05 }, { at: at("anyway."), kind: "punch", s: 1.1, y: -30 }]} hud={<><HookTitle /><Verdict phrase="anyway." text="LINK OPENS" color={C.green} w={460} /></>}><Hook /></Shot>
      <Shot from={s2} to={s3} inT="push" outT="whip" cam={[{ at: 0, kind: "settle", s: 1.0, y: 90, dur: 1 }, { at: cut, kind: "punch", s: 1.08, y: 70 }, { at: adds, kind: "glide", s: 1.04, y: 40 }, { at: at("Reed-Solomon"), kind: "glide", s: 1.06, x: -30, y: 50 }, { at: at("same math"), kind: "push", s: 1.08, x: 0, y: 30 }, { at: cd - 6, kind: "pull", s: 0.96, y: 0 }]}><Bytes /></Shot>
      <Shot from={s3} to={s4} inT="whip" outT="push" cam={[{ at: reb, kind: "punch", s: 1.12, y: 40 }, { at: hi - 4, kind: "glide", s: 1.0, y: -40 }, { at: at("scanner"), kind: "push", s: 1.06, x: -30, y: 10 }, { at: at("30%"), kind: "glide", s: 1.0, x: 20, y: 0 }]}><Repair /></Shot>
      <Shot from={s4} to={s5} inT="push" outT="whipUp" cam={[{ at: s4, kind: "push", s: 1.05, dur: 45 }, { at: at("In real tests"), kind: "glide", s: 1.08, y: -40 }, { at: gl, kind: "pull", s: 1.0, y: 0 }]}><Budget /></Shot>
      <Shot from={s5} to={card} inT="whipUp" outT="push" cam={[{ at: corner, kind: "push", s: 1.06 }, { at: over, kind: "punch", s: 1.1, x: 60, y: 40 }, { at: at("Those aren't data"), kind: "pull", s: 1.0, x: 0, y: 0 }, { at: at("finds the code"), kind: "glide", s: 1.04, x: -20, y: -20 }]}><Finders /></Shot>
      <Shot from={fin} to={loop} inT="push" outT="whip" cam={[{ at: fin, kind: "pull", s: 0.96, dur: 12 }]}><Final /></Shot>
    </EpisodeShell>
  );
};
