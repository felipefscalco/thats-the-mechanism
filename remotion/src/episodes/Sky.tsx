import React from "react";
import { Img, staticFile, useVideoConfig } from "remotion";
import words from "../03-sky.captions.json";
import { C, EpisodeShell, FlatPlanet, LabeledBox, Label, MONO, PILLARS, Pill, Shot, Stage, TagLabel, cue, ease, makeAt, pop, reveal, squash, useG } from "../brand";

/**
 * Sky v7 — one continuous sky world (plan: episodes/03-sky/VIDEO.md).
 * No cards, no split panels, no backdrop photo skyline. The Sun disc and the blue spark stream are the two persistent subjects;
 * every shot is full-bleed sky art drawn from the global frame `f`, so frame 0 is a rest frame and LoopEnd (the shell's hook lock)
 * lands on the identical composition.
 */
const P = PILLARS.sci;
const SPECTRUM = ["#8F5BFF", "#3D7BFF", "#2EC4F0", "#3DDC97", "#F5E14B", "#FF9F2E", "#FF4D3D"];
const RED = "#FF5A4E";
const HZ = 880; // horizon y of the sunset world

const rnd = (i: number, k = 0) => { const v = Math.sin(i * 127.1 + k * 311.7) * 43758.5453; return v - Math.floor(v); };
const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const hex = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const mix = (a: string, b: string, t: number) => { const A = hex(a), B = hex(b); return "#" + A.map((v, i) => Math.round(v + (B[i] - v) * t).toString(16).padStart(2, "0")).join(""); };
const wave = (x0: number, y0: number, len: number, lambda: number, amp: number, phase: number) => {
  const pts: string[] = [];
  for (let x = 0; x <= Math.max(0, len); x += 4) pts.push(`${x0 + x},${y0 + Math.sin((x / lambda) * Math.PI * 2 - phase) * amp}`);
  return `M${pts.join("L")}`;
};

/** Shared gradients: every shot draws from the same palette so the sky reads as one world. */
const Defs: React.FC = () => (
  <defs>
    <linearGradient id="sk-dusk" gradientUnits="userSpaceOnUse" x1={0} y1={0} x2={0} y2={HZ}>
      <stop offset="0" stopColor="#2B5FD6" /><stop offset="0.3" stopColor="#6F86E4" /><stop offset="0.62" stopColor="#F08FA0" /><stop offset="0.86" stopColor="#FFB347" /><stop offset="1" stopColor="#FFD27A" />
    </linearGradient>
    <linearGradient id="sk-noon" gradientUnits="userSpaceOnUse" x1={0} y1={0} x2={0} y2={HZ}>
      <stop offset="0" stopColor="#1B52D0" /><stop offset="0.6" stopColor="#3F86EC" /><stop offset="1" stopColor="#8CC8FF" />
    </linearGradient>
    <linearGradient id="sk-ground" gradientUnits="userSpaceOnUse" x1={0} y1={HZ} x2={0} y2={1920}>
      <stop offset="0" stopColor="#5A2A58" /><stop offset="0.12" stopColor="#2A1838" /><stop offset="0.4" stopColor="#140F22" /><stop offset="1" stopColor="#0B0912" />
    </linearGradient>
    <linearGradient id="sk-open" gradientUnits="userSpaceOnUse" x1={0} y1={0} x2={0} y2={1920}>
      <stop offset="0" stopColor="#1F5FD8" /><stop offset="0.55" stopColor="#5CA4F2" /><stop offset="1" stopColor="#25449F" />
    </linearGradient>
    <linearGradient id="sk-deep" gradientUnits="userSpaceOnUse" x1={0} y1={0} x2={0} y2={1920}>
      <stop offset="0" stopColor="#1A46B4" /><stop offset="0.5" stopColor="#3A75E6" /><stop offset="1" stopColor="#2257CC" />
    </linearGradient>
    <linearGradient id="sk-dark" gradientUnits="userSpaceOnUse" x1={0} y1={0} x2={0} y2={1920}>
      <stop offset="0" stopColor="#050E3C" /><stop offset="0.5" stopColor="#0B2276" /><stop offset="1" stopColor="#06124A" />
    </linearGradient>
    <linearGradient id="sk-dome" gradientUnits="userSpaceOnUse" x1={0} y1={0} x2={0} y2={1040}>
      <stop offset="0" stopColor="#15399E" /><stop offset="1" stopColor="#4C8EE8" />
    </linearGradient>
    <linearGradient id="sk-earthsky" gradientUnits="userSpaceOnUse" x1={0} y1={0} x2={0} y2={1920}>
      <stop offset="0" stopColor="#3A6FE0" /><stop offset="0.35" stopColor="#2A4BB8" /><stop offset="0.65" stopColor="#1A2A7A" /><stop offset="1" stopColor="#10185A" />
    </linearGradient>
    <linearGradient id="sk-scrim" gradientUnits="userSpaceOnUse" x1={0} y1={250} x2={0} y2={590}>
      <stop offset="0" stopColor="#0D0E12" stopOpacity={0} /><stop offset="0.3" stopColor="#0D0E12" stopOpacity={0.62} /><stop offset="0.72" stopColor="#0D0E12" stopOpacity={0.62} /><stop offset="1" stopColor="#0D0E12" stopOpacity={0} />
    </linearGradient>
    <linearGradient id="sk-beam" gradientUnits="userSpaceOnUse" x1={540} y1={0} x2={40} y2={0}>
      <stop offset="0" stopColor="#FFF2C0" /><stop offset="0.5" stopColor="#FFA040" /><stop offset="1" stopColor="#FF8A2E" stopOpacity={0} />
    </linearGradient>
    <radialGradient id="sk-sun"><stop offset="0" stopColor="#FFFBE6" /><stop offset="0.6" stopColor="#FFE08A" /><stop offset="1" stopColor="#FFB347" /></radialGradient>
    <radialGradient id="sk-glow"><stop offset="0" stopColor="#FFC866" stopOpacity={0.85} /><stop offset="1" stopColor="#FF8A2E" stopOpacity={0} /></radialGradient>
    <radialGradient id="sk-spark"><stop offset="0" stopColor="#9FE4FF" stopOpacity={1} /><stop offset="0.5" stopColor="#2E8CFF" stopOpacity={0.7} /><stop offset="1" stopColor="#1E6BFF" stopOpacity={0} /></radialGradient>
    <radialGradient id="sk-bloom"><stop offset="0" stopColor="#FFF0B8" stopOpacity={0.95} /><stop offset="0.45" stopColor="#FFA040" stopOpacity={0.55} /><stop offset="1" stopColor="#FF5A3A" stopOpacity={0} /></radialGradient>
    <radialGradient id="sk-flood"><stop offset="0" stopColor="#8FE0FF" stopOpacity={0.95} /><stop offset="0.6" stopColor="#3D8BFF" stopOpacity={0.7} /><stop offset="1" stopColor="#2A6BFF" stopOpacity={0} /></radialGradient>
    <clipPath id="sk-above"><rect x={0} y={0} width={1080} height={HZ} /></clipPath>
  </defs>
);

/** The Sun: same disc + gradient in every shot (clip = half-set on the horizon). */
const Sun: React.FC<{ f: number; cx: number; cy: number; r: number; clip?: boolean }> = ({ f, cx, cy, r, clip }) => {
  const k = 1 + 0.035 * Math.sin(f / 7);
  return (
    <g>
      <circle cx={cx} cy={cy} r={r * 2.6 * k} fill="url(#sk-glow)" opacity={0.8} />
      <g clipPath={clip ? "url(#sk-above)" : undefined}><circle cx={cx} cy={cy} r={r} fill="url(#sk-sun)" /></g>
    </g>
  );
};

/** The persistent blue-spark particle system (same system carried shot to shot; `pos` sets where it flows). */
const Sparks: React.FC<{ f: number; n: number; pos: (i: number, u: number) => [number, number]; speed?: number; r?: number; o?: number; col?: (i: number) => string }> =
  ({ f, n, pos, speed = 0.012, r = 9, o = 1, col }) => (
    <g>
      {Array.from({ length: n }).map((_, i) => {
        const u = (f * speed + i / n + rnd(i, 9) * 0.05) % 1;
        const [x, y] = pos(i, u);
        const env = Math.pow(Math.sin(Math.PI * u), 0.6) * o, rr = r * (0.7 + 0.6 * rnd(i, 5));
        return (
          <g key={i} opacity={env}>
            {col ? <circle cx={x} cy={y} r={rr * 2.6} fill={col(i)} opacity={0.35} /> : <circle cx={x} cy={y} r={rr * 3.2} fill="url(#sk-spark)" />}
            <circle cx={x} cy={y} r={rr} fill={col ? col(i) : "#DDF5FF"} />
          </g>
        );
      })}
    </g>
  );

/** Hook flow: blue sparks peel sideways off the sunset beam and rise into the upper sky. */
const hookPos = (i: number, u: number): [number, number] => {
  const bx = 130 + 360 * rnd(i, 1), by = 866 - (540 - bx) * (96 / 500);
  return [bx + (rnd(i, 3) - 0.35) * 170 * u + 26 * Math.sin(u * 6 + i), by - 20 - (300 + 190 * rnd(i, 2)) * u];
};

/** Sunset world: dusk sky, optional noon-blue wipe rising from the horizon, ground, half-set sun, orange beam and sparks. */
const SunsetWorld: React.FC<{ f: number; blue: number; sunY: number; n: number }> = ({ f, blue, sunY, n }) => {
  const wy = HZ - blue * (HZ + 170);
  return (
    <>
      <rect x={0} y={0} width={1080} height={HZ + 2} fill="url(#sk-dusk)" />
      {blue > 0.001 && (
        <>
          <linearGradient id="sk-wipe" gradientUnits="userSpaceOnUse" x1={0} y1={wy} x2={0} y2={wy + 170}><stop offset="0" stopColor="#000" /><stop offset="1" stopColor="#fff" /></linearGradient>
          <mask id="sk-wm" maskUnits="userSpaceOnUse" x={0} y={-200} width={1080} height={2400}><rect x={0} y={-200} width={1080} height={2400} fill="url(#sk-wipe)" /></mask>
          <rect x={0} y={0} width={1080} height={HZ + 2} fill="url(#sk-noon)" mask="url(#sk-wm)" />
        </>
      )}
      <rect x={0} y={HZ} width={1080} height={1040} fill="url(#sk-ground)" />
      <ellipse cx={540} cy={HZ} rx={560} ry={130} fill="url(#sk-glow)" opacity={0.7} />
      <ellipse cx={540} cy={HZ + 130} rx={140} ry={190} fill="url(#sk-glow)" opacity={0.35} />
      {[0, 1, 2, 3].map((k) => (
        <line key={k} x1={300 + k * 40} y1={HZ + 60 + k * 46} x2={780 - k * 40} y2={HZ + 60 + k * 46} stroke="#FFB070" strokeWidth={4} strokeLinecap="round" strokeDasharray="60 44" strokeDashoffset={-f * (2 + k) } opacity={0.25 - k * 0.04} />
      ))}
      <line x1={540} y1={866} x2={40} y2={770} stroke="#FF8A2E" strokeWidth={70} strokeLinecap="round" opacity={0.22} />
      <line x1={540} y1={866} x2={40} y2={770} stroke="url(#sk-beam)" strokeWidth={30} strokeLinecap="round" />
      <line x1={520} y1={862} x2={80} y2={778} stroke="#FFF6D8" strokeWidth={7} strokeLinecap="round" strokeDasharray="50 70" strokeDashoffset={-f * 10} opacity={0.6} />
      <Sun f={f} cx={540} cy={sunY} r={170} clip />
      <Sparks f={f} n={n} pos={hookPos} r={15} />
    </>
  );
};

/* ---------- Shot 1 / hook (also the frozen loop target) ---------- */
const sunY1 = (f: number) => 850 + ease(f, 0, 125, 0, 28);
const Hook: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const b2 = makeAt(words, fps)("the same");
  const o = ease(f, b2 - 10, b2 - 3, 1, 0);
  return (
    <Stage>
      <Defs />
      <SunsetWorld f={f} blue={0} sunY={sunY1(f)} n={8} />
      <rect x={0} y={250} width={1080} height={340} fill="url(#sk-scrim)" opacity={o} />
      <Label x={115} y={375} text="SOMEONE ELSE'S" anchor="start" size={80} o={o} />
      <Label x={115} y={470} text="BLUE SKY" anchor="start" size={96} o={o} />
      <Label x={115} y={1020} text="SUNSET" anchor="start" size={40} o={o} />
    </Stage>
  );
};

/* ---------- Shot 2: the sky turns noon-blue from the horizon up ---------- */
const SameTrick: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const b2 = at("the same"), same = at("same trick");
  return (
    <Stage>
      <Defs />
      <SunsetWorld f={f} blue={ease(f, b2 + 6, b2 + 48)} sunY={878} n={14} />
      <Pill x={540} y={1040} w={460} text="SAME TRICK" color={C.amber} s={pop(f, same, fps)} />
    </Stage>
  );
};

/* ---------- Shot 3: sunlight enters a prism drawn in the air ---------- */
const PX = 470, PY = 730;
const Prism: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const b3 = at("Sunlight is every"), col = at("every color");
  const g = ease(f, b3, b3 + 14), SX = 770, SY = 520;
  const rayEnd = (i: number, k: number): [number, number] => [PX - 45 - 600 * k, PY + 10 + ((i - 3) * 70 + 110) * k];
  return (
    <Stage>
      <Defs />
      <rect x={0} y={0} width={1080} height={1920} fill="url(#sk-open)" />
      <Sun f={f} cx={SX} cy={SY} r={95} />
      <line x1={SX - 70} y1={SY + 45} x2={SX - 70 + (PX + 55 - SX + 70) * g} y2={SY + 45 + (PY - 15 - SY - 45) * g} stroke="#fff" strokeWidth={20} strokeLinecap="round" />
      <g opacity={ease(f, b3 + 6, b3 + 16)}>
        <polygon points={`${PX},${PY - 130} ${PX + 110},${PY + 60} ${PX - 110},${PY + 60}`} fill="rgba(255,255,255,0.2)" stroke={C.paper} strokeWidth={5} />
      </g>
      {SPECTRUM.map((c, i) => {
        const k = ease(f, col + i * 2, col + i * 2 + 14), [x2, y2] = rayEnd(i, k);
        return (
          <g key={i}>
            <line x1={PX - 45} y1={PY + 10} x2={x2} y2={y2} stroke={c} strokeWidth={14} strokeLinecap="round" />
            <line x1={PX - 45} y1={PY + 10} x2={x2} y2={y2} stroke="#fff" strokeWidth={4} strokeLinecap="round" strokeDasharray="26 60" strokeDashoffset={-f * 9} opacity={0.55 * k} />
          </g>
        );
      })}
      <Sparks f={f} n={14} speed={0.014} r={8} o={ease(f, col + 8, col + 22)} col={(i) => SPECTRUM[i % 7]}
        pos={(i, u) => { const [x, y] = rayEnd(i % 7, u * 1.05); return [x, y]; }} />
      <TagLabel x={450} y={470} text="SUNLIGHT" size={40} o={f < col ? ease(f, b3 + 4, b3 + 12) : 0} />
      <TagLabel x={450} y={470} text="EVERY COLOR" size={40} color={C.amber} o={ease(f, col, col + 8)} />
    </Stage>
  );
};

/* ---------- Shots 4-5: the molecule and the strike ---------- */
const MX = 620, MY = 750;
const Dust: React.FC<{ f: number }> = ({ f }) => (
  <g>{Array.from({ length: 30 }).map((_, i) => (
    <circle key={i} cx={((rnd(i, 1) * 1200 + f * (0.4 + rnd(i, 2) * 0.7)) % 1180) - 50} cy={330 + rnd(i, 3) * 880 + 12 * Math.sin(f / 25 + i)} r={3 + rnd(i, 4) * 4} fill="#CFE4FF" opacity={0.35} />
  ))}</g>
);
const Mol: React.FC<{ f: number; kx?: number; ky?: number; sx?: number; sy?: number; flash?: number }> = ({ f, kx = 0, ky = 0, sx = 1, sy = 1, flash = 0 }) => (
  <g transform={`translate(${MX + kx} ${MY + ky + 3 * Math.sin(f / 9)}) scale(${sx} ${sy})`}>
    {flash > 0.02 && <circle r={70 + 40 * (1 - flash)} fill="#fff" opacity={0.75 * flash} />}
    <line x1={-26} y1={0} x2={26} y2={0} stroke="#DCD3FF" strokeWidth={10} />
    <circle cx={-26} r={24} fill="#B7A9FF" stroke="#fff" strokeWidth={3} /><circle cx={26} r={24} fill="#B7A9FF" stroke="#fff" strokeWidth={3} />
  </g>
);

const MolIntro: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const mol = at("Air molecules"), th = at("thousand");
  const frontB = ease(f, mol, mol + 45, 0, 470), frontR = ease(f, mol + 8, mol + 60, 0, 440);
  return (
    <Stage>
      <Defs />
      <rect x={0} y={0} width={1080} height={1920} fill="url(#sk-dark)" />
      <Dust f={f} />
      <path d={wave(-20, 690, frontB + 20, 190, 34, f / 2.5)} stroke="#6CB4FF" strokeWidth={9} fill="none" strokeLinecap="round" />
      <path d={wave(-20, 810, frontR + 20, 380, 34, f / 4)} stroke={RED} strokeWidth={9} fill="none" strokeLinecap="round" />
      <Mol f={f} />
      <TagLabel x={MX} y={575} text="N₂ / O₂ MOLECULE" size={36} color="#D8CEFF" o={ease(f, mol + 12, mol + 22)} />
      <TagLabel x={MX} y={960} text="~1000× SMALLER" size={36} color={C.amber} o={ease(f, th, th + 8)} />
    </Stage>
  );
};

const MolHit: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const b5 = at("tiny things"), imp = at("scatter"), far = at("far more");
  const tt = f - imp, hit = tt >= 0;
  const blueEnd = ease(f, b5, imp, 0, MX - 56 + 20), blueOp = f < imp ? 1 : 1 - ease(f, imp, imp + 14);
  const redEnd = ease(f, far - 4, far + 44, 0, 1120);
  const wob = clamp((redEnd - (MX - 100)) / 200) * (1 - clamp((redEnd - (MX + 200)) / 300));
  const [sx, sy] = squash(f, imp, 0.28);
  const flow = ease(f, imp + 6, imp + 16) * (1 - ease(f, imp + 44, imp + 70));
  return (
    <Stage>
      <Defs />
      <rect x={0} y={0} width={1080} height={1920} fill="url(#sk-deep)" />
      <Dust f={f} />
      <path d={wave(-20, MY, blueEnd, 190, 34, f / 2.5)} stroke="#6CB4FF" strokeWidth={9} fill="none" strokeLinecap="round" opacity={blueOp} />
      <path d={wave(-20, MY, redEnd, 380, 30, f / 4)} stroke={RED} strokeWidth={9} fill="none" strokeLinecap="round" opacity={0.9} />
      {hit && Array.from({ length: 14 }).map((_, i) => {
        const a = (i / 14) * Math.PI * 2 + 0.2, c = Math.cos(a), s = Math.sin(a);
        const len = ease(f, imp, imp + 10, 0, 150), op = 0.9 * (1 - ease(f, imp + 8, imp + 30));
        const u = (tt / 24 + i * 0.11) % 1, r0 = 70 + 130 * u, r1 = r0 + 44 * (1 - u);
        return (
          <g key={i}>
            <line x1={MX + c * 40} y1={MY + s * 40} x2={MX + c * (40 + len)} y2={MY + s * (40 + len)} stroke="#6CC8FF" strokeWidth={7} strokeLinecap="round" opacity={op} />
            <line x1={MX + c * r0} y1={MY + s * r0} x2={MX + c * r1} y2={MY + s * r1} stroke="#BFEFFF" strokeWidth={6} strokeLinecap="round" opacity={flow * (1 - u)} />
          </g>
        );
      })}
      <Mol f={f} kx={hit ? 18 * Math.exp(-tt / 6) * Math.cos(tt / 2.5) : 0} ky={4 * Math.sin(f * 1.1) * wob} sx={sx} sy={sy} flash={hit ? Math.exp(-tt / 8) : 0} />
      <TagLabel x={MX} y={440} text="SHORT WAVES SCATTER" size={36} color="#CFEBFF" o={ease(f, b5 + 4, b5 + 12)} />
    </Stage>
  );
};

/* ---------- Shot 6: blue sprays 4 bursts, red sprays 1 ---------- */
const Burst: React.FC<{ f: number; t0: number; x: number; y: number; color: string }> = ({ f, t0, x, y, color }) => {
  if (f < t0) return null;
  const u = ease(f, t0, t0 + 16), life = clamp(1 - (f - t0) / 40);
  return (
    <g opacity={life}>
      {Array.from({ length: 8 }).map((_, i) => {
        const a = (i / 8) * Math.PI * 2 + 0.3, r0 = 12 + u * 40, r1 = r0 + 26 * (1 - u * 0.5);
        return <line key={i} x1={x + Math.cos(a) * r0} y1={y + Math.sin(a) * r0} x2={x + Math.cos(a) * r1} y2={y + Math.sin(a) * r1} stroke={color} strokeWidth={7} strokeLinecap="round" />;
      })}
      <circle cx={x} cy={y} r={u * 34} fill="none" stroke="#fff" strokeWidth={4} opacity={1 - u} />
    </g>
  );
};
const Ratio: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const b6 = at("Blue gets bounced"), bt = at("bounced"), red = at("than red");
  const blueT = [0, 1, 2, 3].map((k) => bt + 4 + k * 14), nBlue = blueT.filter((t) => f >= t).length, nRed = f >= red ? 1 : 0;
  const L = ease(f, b6, b6 + 12, 0, 1080);
  return (
    <Stage>
      <Defs />
      <rect x={0} y={0} width={1080} height={1920} fill="url(#sk-dark)" />
      {Array.from({ length: 40 }).map((_, i) => (
        <circle key={i} cx={330 + rnd(i, 1) * 430 + 14 * Math.sin(f / 30 + i)} cy={540 + rnd(i, 2) * 420 + 10 * Math.cos(f / 26 + i)} r={6 + rnd(i, 3) * 3} fill="#CFE4FF" opacity={0.45} />
      ))}
      <line x1={0} y1={640} x2={L} y2={640} stroke="#59C2FF" strokeWidth={14} strokeLinecap="round" />
      <line x1={0} y1={640} x2={L} y2={640} stroke="#fff" strokeWidth={4} strokeDasharray="30 60" strokeDashoffset={-f * 8} opacity={0.6} />
      <line x1={0} y1={860} x2={L} y2={860} stroke="#FF6B5E" strokeWidth={14} strokeLinecap="round" />
      <line x1={0} y1={860} x2={L} y2={860} stroke="#fff" strokeWidth={4} strokeDasharray="30 60" strokeDashoffset={-f * 8} opacity={0.6} />
      {[380, 470, 560, 650].map((x, k) => <Burst key={k} f={f} t0={blueT[k]} x={x} y={640} color="#8FE0FF" />)}
      <Burst f={f} t0={red} x={560} y={860} color="#FF9C8E" />
      <TagLabel x={150} y={560} text={`BLUE ${nBlue}×`} size={40} color="#9FDCFF" anchor="start" o={ease(f, b6 + 6, b6 + 14)} />
      <TagLabel x={150} y={780} text={`RED ${nRed}×`} size={40} color="#FFB0A6" anchor="start" o={ease(f, b6 + 10, b6 + 18)} />
    </Stage>
  );
};

/* ---------- Shot 7: noon dome ---------- */
const OX = 440, GY = 1040, DCY = 1000, EYE: [number, number] = [446, 985];
const Dome: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const b7 = at("At noon"), scb = at("scattered blue"), sky = at("That's the sky");
  const g = ease(f, b7 + 6, b7 + 20);
  const arrows = Array.from({ length: 18 }).map((_, i) => {
    const th = ((195 + i * (150 / 17)) * Math.PI) / 180, S: [number, number] = [OX + 430 * Math.cos(th), DCY + 430 * Math.sin(th)];
    const sg = Math.cos(th) < 0 ? 1 : -1, Cc: [number, number] = [OX + 300 * Math.cos(th + sg * 0.2), DCY + 300 * Math.sin(th + sg * 0.2)];
    const start = scb + i * 2;
    if (f < start) return null;
    const u = ((f - start) * 0.017) % 1, B = (t: number): [number, number] => [(1 - t) ** 2 * S[0] + 2 * (1 - t) * t * Cc[0] + t * t * EYE[0], (1 - t) ** 2 * S[1] + 2 * (1 - t) * t * Cc[1] + t * t * EYE[1]];
    const t0 = Math.max(0, u - 0.28), pts = Array.from({ length: 7 }).map((_, k) => B(t0 + ((u - t0) * k) / 6));
    const hd = pts[6], pv = pts[5], an = Math.atan2(hd[1] - pv[1], hd[0] - pv[0]);
    const tri = [[0, 0], [-20, -10], [-20, 10]].map(([a, b]) => `${hd[0] + a * Math.cos(an) - b * Math.sin(an)},${hd[1] + a * Math.sin(an) + b * Math.cos(an)}`).join(" ");
    return (
      <g key={i} opacity={Math.pow(Math.sin(Math.PI * u), 0.5)}>
        <path d={`M${pts.map((p) => p.join(",")).join("L")}`} stroke="#9FDCFF" strokeWidth={8} fill="none" strokeLinecap="round" />
        <polygon points={tri} fill="#DDF5FF" />
      </g>
    );
  });
  return (
    <Stage>
      <Defs />
      <rect x={0} y={0} width={1080} height={GY + 2} fill="url(#sk-dome)" />
      <rect x={0} y={GY} width={1080} height={900} fill="#16202E" />
      <rect x={0} y={GY} width={1080} height={5} fill="#2F4260" />
      <path d={`M${OX - 430},${DCY} A430,430 0 0 1 ${OX + 430},${DCY}`} fill="none" stroke="#fff" strokeWidth={3} strokeDasharray="10 14" strokeDashoffset={-f / 2} opacity={0.35} />
      <Sun f={f} cx={760} cy={400} r={80} />
      <line x1={715} y1={460} x2={715 - 105 * g} y2={460 + 180 * g} stroke="#fff" strokeWidth={14} strokeLinecap="round" />
      {arrows}
      <g transform={`translate(${OX} ${GY})`}><rect x={-9} y={-44} width={18} height={38} rx={7} fill={C.paper} /><circle cy={-58} r={12} fill={C.paper} /></g>
      <Pill x={OX} y={1110} w={460} text="YOU, AT NOON" color={C.amber} s={pop(f, b7 + 14, fps)} />
      <TagLabel x={OX} y={500} text="THAT'S THE SKY" size={40} color="#DDF5FF" o={ease(f, sky, sky + 8)} />
    </Stage>
  );
};

/* ---------- Shots 8, 10, 11: Earth cross-section (one continuous diagram) ---------- */
const EX = 330, EY = 850, ER = 250, AR = 272, YB = EY - ER, SUNX = 840, OBX = EX + ER;
const arcPos = (i: number, u: number): [number, number] => {
  const sx = 345 + 90 * rnd(i, 1), th0 = ((-90 + 16 * rnd(i, 2)) * Math.PI) / 180, R = AR + 34;
  const a0: [number, number] = [EX + R * Math.cos(th0), EY + R * Math.sin(th0)];
  if (u < 0.2) { const k = 1 - (1 - u / 0.2) ** 2; return [sx + (a0[0] - sx) * k, YB + (a0[1] - YB) * k]; }
  const w = (u - 0.2) / 0.8, th = th0 * (1 - w), r = R - (R - ER - 8) * w ** 3 + 14 * Math.sin(w * Math.PI) * (rnd(i, 3) - 0.3);
  return [EX + r * Math.cos(th), EY + r * Math.sin(th)];
};
const Earth: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s4 = at("At sunset"), dz = at("dozens"), b9 = at("Along the way"), b10 = at("beam"), pillT = at("someone else's afternoon"), b11 = at("What survives"), surv = at("survives");
  const phase8 = f < b9, hero = f >= b10 && f < b11, land = f >= b11;
  const g = ease(f, s4 + 4, dz + 4), xHead = 780 + (EX - 780) * g;
  const warm = ease(f, b10, b10 + 40), red = ease(f, b11 - 6, b11 + 20);
  const flood = ease(f, b10 + 38, b10 + 84), bloom = ease(f, b11, b11 + 16);
  const c0 = mix("#FFFFFF", "#FFF0C8", warm), c1 = mix("#FFFFFF", "#FFA23C", warm), c2 = mix("#FFF3C8", "#FF4D3D", red);
  const bw = 16 + 6 * bloom;
  const NS = 20, sparkO = land ? 0.4 : 1;
  return (
    <Stage>
      <Defs />
      <linearGradient id="sk-beamE" gradientUnits="userSpaceOnUse" x1={780} y1={0} x2={EX} y2={0}><stop offset="0" stopColor={c0} /><stop offset="0.45" stopColor={c1} /><stop offset="1" stopColor={c2} /></linearGradient>
      <rect x={0} y={0} width={1080} height={1920} fill="url(#sk-earthsky)" />
      <circle cx={OBX + 10} cy={EY} r={200} fill="#0A1450" opacity={0.55 * (1 - flood)} />
      <circle cx={OBX + 10} cy={EY} r={210 * (0.6 + 0.4 * flood)} fill="url(#sk-flood)" opacity={flood} />
      {f > b10 + 38 && [0, 1, 2].map((k) => {
        const r = ((f - b10 - 38) * 3 + k * 64) % 192;
        return <circle key={k} cx={OBX} cy={EY} r={r} fill="none" stroke="#CFF1FF" strokeWidth={4} opacity={(1 - r / 192) * 0.75 * flood} />;
      })}
      <Sun f={f} cx={SUNX} cy={YB} r={70} />
      <circle cx={EX} cy={EY} r={AR} fill="#7FC8FF" opacity={0.12} />
      <FlatPlanet x={EX} y={EY} r={ER} f={f} id="sk" />
      <circle cx={EX} cy={EY} r={AR} fill="none" stroke="#9FE0FF" strokeWidth={18} opacity={0.5 + 0.1 * Math.sin(f / 9)} />
      <circle cx={EX} cy={EY} r={AR + 12} fill="none" stroke="#fff" strokeWidth={3} opacity={0.35} />
      {land && <circle cx={EX} cy={YB} r={(190 + 14 * Math.sin(f / 6)) * bloom} fill="url(#sk-bloom)" />}
      <line x1={780} y1={YB} x2={xHead} y2={YB} stroke="url(#sk-beamE)" strokeWidth={bw + 26} strokeLinecap="round" opacity={0.28 + 0.2 * bloom} />
      <line x1={780} y1={YB} x2={xHead} y2={YB} stroke="url(#sk-beamE)" strokeWidth={bw} strokeLinecap="round" />
      <line x1={760} y1={YB} x2={xHead} y2={YB} stroke="#fff" strokeWidth={4} strokeDasharray="28 60" strokeDashoffset={-f * 9} opacity={0.5 * g} />
      {phase8 && (
        <g opacity={ease(f, dz, dz + 8)}>
          <g stroke={C.amber} strokeWidth={4}>
            <line x1={EX} y1={548} x2={EX + 107} y2={548} /><line x1={EX} y1={534} x2={EX} y2={562} /><line x1={EX + 107} y1={534} x2={EX + 107} y2={562} />
            <line x1={OBX + 24} y1={EY + 60} x2={OBX + 46} y2={EY + 60} /><line x1={OBX + 24} y1={EY + 46} x2={OBX + 24} y2={EY + 74} /><line x1={OBX + 46} y1={EY + 46} x2={OBX + 46} y2={EY + 74} />
          </g>
        </g>
      )}
      {f >= b10 && (
        <g>
          {Array.from({ length: NS }).map((_, i) => {
            const act = f - b10 - i * 2.7;
            if (act < 0) return null;
            const u = (act / 54 + (1 - i / NS) ) % 1, env = Math.min(1, u / 0.06, (1 - u) / 0.06) * sparkO;
            const p = arcPos(i, u), pts = Array.from({ length: 7 }).map((_, k) => arcPos(i, Math.max(0, u - 0.14 + (0.14 * k) / 6)));
            return (
              <g key={i} opacity={env}>
                <path d={`M${pts.map((q) => q.join(",")).join("L")}`} stroke="#7FD8FF" strokeWidth={6} fill="none" strokeLinecap="round" opacity={0.55} />
                <circle cx={p[0]} cy={p[1]} r={20} fill="url(#sk-spark)" />
                <circle cx={p[0]} cy={p[1]} r={7} fill="#E8F8FF" />
              </g>
            );
          })}
        </g>
      )}
      <g transform={`translate(${EX} ${YB})`}><circle r={14} fill={C.paper} /><circle r={26 + 4 * Math.sin(f / 5)} fill="none" stroke={C.paper} strokeWidth={3} opacity={0.5} /></g>
      <g transform={`translate(${OBX} ${EY})`}><circle r={14} fill={C.paper} /></g>
      {phase8 && <TagLabel x={EX} y={470} text="DOZENS × MORE AIR" size={40} color={C.amber} o={ease(f, dz, dz + 8)} />}
      {(hero || land) && <LabeledBox box={{ x: EX - 14, y: YB - 14, w: 28, h: 28 }} side="bottom" label="YOU, AT SUNSET" size={34} color={land ? "#FFD27A" : C.paper} o={ease(f, hero ? b10 + 6 : b11, (hero ? b10 + 6 : b11) + 8)} />}
      {hero && <TagLabel x={500} y={1110} text="SOMEONE ELSE'S AFTERNOON" size={34} color="#CFEBFF" o={ease(f, pillT - 2, pillT + 6)} />}
      {land && <Pill x={470} y={1110} w={620} text="ORANGE + RED SURVIVE" color={C.ink} textColor={C.amber} s={pop(f, surv, fps)} />}
    </Stage>
  );
};

/* ---------- Shot 9: the real ISS photo as a full-bleed window (no card, no diagram behind) ---------- */
const IssWindow: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const along = makeAt(words, fps)("Along the way");
  const xs = -700 + (((f - along) * 22) % 1800);
  return (
    <>
      <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 1920, background: "#0B0A0D" }} />
      <Img src={staticFile("photos/03-sky--earth-observation.jpg")} style={{ position: "absolute", left: -996, top: -268, width: 3072, height: 2040 }} />
      <Stage>
        <defs>
          <linearGradient id="sk-sweep" gradientUnits="userSpaceOnUse" x1={xs} y1={0} x2={xs + 700} y2={0}>
            <stop offset="0" stopColor="#3D8BFF" stopOpacity={0} /><stop offset="0.3" stopColor="#59C2FF" /><stop offset="0.7" stopColor="#FF5A3A" /><stop offset="1" stopColor="#FF5A3A" stopOpacity={0} />
          </linearGradient>
        </defs>
        <rect x={0} y={1014} width={1080} height={9} fill="url(#sk-sweep)" />
        <TagLabel x={400} y={430} text="SEEN FROM THE ISS" size={40} o={ease(f, along + 8, along + 18)} />
        <Label x={100} y={1100} text="NASA ISS028-E-007274" anchor="start" size={32} font={MONO} weight={500} o={ease(f, along + 14, along + 22)} />
        <Label x={100} y={1146} text="PUBLIC DOMAIN" anchor="start" size={32} font={MONO} weight={500} o={ease(f, along + 14, along + 22)} />
      </Stage>
    </>
  );
};

/* ---------- Shots 12-13: end-card world and the callback that settles into the hook ---------- */
const CardSky: React.FC = () => {
  const f = useG();
  return <Stage><Defs /><SunsetWorld f={f} blue={0.6} sunY={878} n={10} /></Stage>;
};
const Callback: React.FC = () => {
  const f = useG();
  const { fps, durationInFrames: D } = useVideoConfig();
  const at = makeAt(words, fps);
  const fin = at("Your sunset is"), loop = D - 14;
  const blue = 1 - ease(f, fin + 34, loop - 24);
  const o = ease(f, fin + 8, fin + 16) * ease(f, fin + 44, fin + 52, 1, 0);
  return (
    <Stage>
      <Defs />
      <SunsetWorld f={f} blue={blue} sunY={878 + ease(f, fin + 34, loop - 24, 0, -28)} n={14} />
      <TagLabel x={540} y={480} text="SAME LIGHT, LATER" size={40} color={C.amber} o={o} />
    </Stage>
  );
};

export const SkyVideo: React.FC = () => {
  const { fps, durationInFrames: D } = useVideoConfig();
  const at = makeAt(words, fps);
  const b2 = at("the same"), same = at("same trick"), b3 = at("Sunlight is every"), col = at("every color"), mol = at("Air molecules"), th = at("thousand"),
    b5 = at("tiny things"), imp = at("scatter"), b6 = at("Blue gets bounced"), bt = at("bounced"), red = at("than red"),
    b7 = at("At noon"), scb = at("scattered blue"), sky = at("That's the sky"), b8 = at("At sunset"), dz = at("dozens"),
    b9 = at("Along the way"), b10 = at("beam"), pillT = at("someone else's afternoon"), b11 = at("What survives"), orr = at("orange and red"),
    card = at("That's the mechanism"), fin = at("Your sunset is"), loop = D - 14;
  const cues = [
    cue(4, "swish", 0.91), cue(at("blue"), "tick", 0.98), cue(same, "pop", 0.9), cue(at("two places"), "tick", 0.91),
    cue(col, "glint", 1.0), cue(mol, "pop", 0.9), cue(th, "count", 1.0), cue(imp, "glitch", 0.91), cue(at("short waves"), "pop", 1.0),
    ...[0, 1, 2, 3].map((k) => cue(bt + 4 + k * 14, "tick", 0.98)), cue(red, "tick", 1.0), cue(at("four times"), "thud", 0.91),
    cue(scb, "tick", 1.0), cue(sky, "confirm", 0.85),
    cue(dz, "pop", 0.85), cue(b9, "pop3", 0.85), cue(b10, "riser", 0.78), cue(pillT, "pop", 1.0),
    cue(b11 + 2, "thud", 0.78), ...reveal(orr, 0.9), cue(at("leftovers"), "pop", 0.9),
  ];
  return (
    <EpisodeShell audio="03-sky.wav" words={words} pillar={P} ep="003" source="MET OFFICE · NOAA" microGap={13}
      cardAt={card} cardUntil={fin} cues={cues} hook={<Hook />}
      chapters={[{ at: 0, label: "SAME TRICK?" }, { at: b3, label: "WHAT AIR DOES" }, { at: b6, label: "BLUE VS RED" }, { at: b7, label: "NOON" }, { at: b8, label: "SUNSET" }]}>
      <Shot from={0} to={b2} inT="none" outT="cut" cam={[{ at: 0, kind: "glide", s: 1.06, y: 12, dur: b2 }]}><Hook /></Shot>
      <Shot from={b2} to={b3} inT="cut" outT="cut" depth={false} cam={[{ at: same, kind: "punch", s: 1.05, y: 20 }]}><SameTrick /></Shot>
      <Shot from={b3} to={mol} inT="cut" outT="push" depth={false} cam={[{ at: b3, kind: "glide", s: 1.05, x: 30, y: -10, dur: 30 }]}><Prism /></Shot>
      <Shot from={mol} to={b5} inT="push" outT="cut" depth={false} cam={[{ at: mol, kind: "push", s: 1.15, y: 10, dur: 60 }, { at: at("light wave"), kind: "glide", s: 1.15, x: 30, dur: 24 }]}><MolIntro /></Shot>
      <Shot from={b5} to={b6} inT="cut" outT="cut" depth={false} cam={[{ at: imp - 7, kind: "punch", s: 1.08, y: 8 }, { at: imp + 22, kind: "pull", s: 1.0, y: 0 }]}><MolHit /></Shot>
      <Shot from={b6} to={b7} inT="cut" outT="whipUp" depth={false} cam={[{ at: b6 + 10, kind: "push", s: 1.06, dur: 40 }, { at: at("four times"), kind: "punch", s: 1.08 }]}><Ratio /></Shot>
      <Shot from={b7} to={b8} inT="whipUp" outT="cut" depth={false} cam={[{ at: b7, kind: "glide", s: 1.04, y: -10, dur: 30 }, { at: scb, kind: "push", s: 1.1, x: 30, y: 10, dur: 36 }]}><Dome /></Shot>
      <Shot from={b8} to={b9} inT="cut" outT="cut" depth={false} cam={[{ at: b8, kind: "glide", s: 1.14, y: 60, dur: 1 }, { at: b8 + 3, kind: "pull", s: 1.0, y: 0, dur: 40 }]}><Earth /></Shot>
      <Shot from={b9} to={b10} inT="cut" outT="cut" depth={false} cam={[{ at: b9, kind: "glide", s: 1.04, dur: 12 }, { at: b9 + 12, kind: "push", s: 1.12, dur: 52 }]}><IssWindow /></Shot>
      <Shot from={b10} to={b11} inT="cut" outT="cut" depth={false} cam={[{ at: b10, kind: "glide", s: 1.1, x: -60, y: 40, dur: 40 }, { at: pillT, kind: "pull", s: 1.0, x: 0, y: 0 }]}><Earth /></Shot>
      <Shot from={b11} to={card} inT="cut" outT="push" depth={false} cam={[{ at: b11, kind: "push", s: 1.06, y: 20, dur: 80 }]}><Earth /></Shot>
      <Shot from={card} to={fin} inT="cut" outT="none" depth={false}><CardSky /></Shot>
      <Shot from={fin} to={loop} inT="push" outT="whip" cam={[{ at: fin, kind: "glide", s: 1.06, dur: 1 }, { at: fin + 2, kind: "pull", s: 1.0, dur: loop - fin - 24 }]}><Callback /></Shot>
    </EpisodeShell>
  );
};
