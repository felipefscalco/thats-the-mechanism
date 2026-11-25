import React from "react";
import { useVideoConfig } from "remotion";
import words from "../01-qr-code.captions.json";
import qr from "../qr-matrix.json";
import { C, EpisodeShell, GearG, Label, LOOP_FRAMES, MONO, PILLARS, Pill, Shot, Stage, cue, ease, makeAt, pop, useG } from "../brand";

const P = PILLARS.tech;
const N = qr.n;
const isFinder = (r: number, c: number) => (r < 7 && c < 7) || (r < 7 && c >= N - 7) || (r >= N - 7 && c < 7);

/** Real level-H QR for youtube.com/@thatsthemechanism (it actually scans in the render). */
const QRCard: React.FC<{ cx: number; cy: number; size: number; logo?: number; finderGlow?: number; coverTL?: number; glare?: number; shake?: number; rot?: number }> =
  ({ cx, cy, size, logo = 0, finderGlow = 0, coverTL = 0, glare = 0, shake = 0, rot = 0 }) => {
    const f = useG();
    const pad = size * 0.08, m = (size - 2 * pad) / N;
    const logoW = Math.sqrt(logo) * (size - 2 * pad);
    const sx = shake * Math.sin(f * 2.1) * 14;
    return (
      <g transform={`translate(${cx - size / 2 + sx} ${cy - size / 2})`}>
        <rect x={6} y={14} width={size} height={size} rx={28} fill="#000" opacity={0.35} />
        <rect width={size} height={size} rx={28} fill={C.paper} />
        <g transform={`translate(${pad} ${pad})`}>
          {qr.rows.map((row, r) => row.split("").map((v, c) => v === "1" ? (
            <rect key={`${r}-${c}`} x={c * m} y={r * m} width={m + 0.6} height={m + 0.6} fill={isFinder(r, c) && finderGlow > 0 ? P.color : C.ink} />
          ) : null))}
          {finderGlow > 0 && [[0, 0], [0, N - 7], [N - 7, 0]].map(([r, c], i) => (
            <rect key={i} x={c * m - 10} y={r * m - 10} width={7 * m + 20} height={7 * m + 20} rx={12} fill="none" stroke={P.color} strokeWidth={6} opacity={finderGlow * (0.6 + 0.4 * Math.sin(f / 4))} />
          ))}
          {logo > 0 && (
            <g transform={`translate(${(N * m) / 2} ${(N * m) / 2})`}>
              <rect x={-logoW / 2} y={-logoW / 2} width={logoW} height={logoW} rx={logoW * 0.18} fill={C.ink} stroke={C.paper} strokeWidth={8} />
              <GearG r={logoW * 0.34} color={C.amber} rot={rot} />
            </g>
          )}
          {coverTL > 0 && <rect x={-pad} y={-pad} width={(9 * m + pad) * coverTL} height={9 * m + pad} rx={18} fill="#2B2F3A" />}
          {glare > 0 && (
            <g opacity={glare}>
              <rect x={-60} y={N * m * 0.62} width={N * m + 120} height={70} fill="white" opacity={0.85} transform={`rotate(-24 ${N * m / 2} ${N * m / 2})`} />
              {Array.from({ length: 22 }).map((_, i) => (
                <circle key={i} cx={((i * 137) % 100) / 100 * N * m} cy={((i * 71 + 13) % 100) / 100 * N * m} r={6 + (i % 4) * 3} fill={i % 2 ? "white" : "#7A7F8C"} />
              ))}
            </g>
          )}
        </g>
      </g>
    );
  };

const Viewfinder: React.FC<{ cx: number; cy: number; size: number; color: string; o: number; jitter?: number }> = ({ cx, cy, size, color, o, jitter = 0 }) => {
  const f = useG();
  const h = size / 2 + 30 + Math.sin(f / 3) * jitter * 20, L = 70;
  return (
    <g transform={`translate(${cx + jitter * Math.sin(f * 1.7) * 30} ${cy + jitter * Math.cos(f * 1.3) * 20})`} opacity={o}>
      {[[-1, -1], [1, -1], [-1, 1], [1, 1]].map(([dx, dy], i) => (
        <path key={i} d={`M${dx * h} ${dy * (h - L)} L${dx * h} ${dy * h} L${dx * (h - L)} ${dy * h}`} stroke={color} strokeWidth={10} fill="none" strokeLinecap="round" />
      ))}
    </g>
  );
};

const W = 1080, CY = 700;
const bytesOf = "youtube.com/@thatsthemechanism".split("").slice(0, 12).map((ch) => ch.charCodeAt(0).toString(16).toUpperCase());

/** Shot 1 = the hook. Also rendered frozen at frame 0 by the loop-back, so it must depend only on useG(). */
const Hook: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const cam = at("Your camera");
  return (
    <Stage>
      <QRCard cx={W / 2} cy={CY} size={640} logo={0.11 * ease(f, 0, 12)} rot={f * 2} />
      <Viewfinder cx={W / 2} cy={CY} size={640} color={f > cam ? C.green : C.paper} o={ease(f, cam - 8, cam)} />
      {f > cam && <rect x={W / 2 - 350} y={CY - 350 + ((f - cam) * 28) % 700} width={700} height={6} fill={C.green} opacity={0.8} />}
    </Stage>
  );
};

/** Screen-space verdict pills (outside the camera). */
const Verdict: React.FC<{ phrase: string; until?: string; text: string; color: string; textColor?: string; w?: number }> = ({ phrase, until, text, color, textColor, w = 420 }) => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const a = at(phrase), u = until ? at(until) : 1e9;
  return <Stage><Pill x={W / 2} y={1150} w={w} text={text} color={color} textColor={textColor} s={pop(f, a, fps) * ease(f, u, u + 6, 1, 0)} /></Stage>;
};

const Bytes: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const cut = at("cut into bytes"), adds = at("adds extra bytes"), rs = at("That's Reed-Solomon"), cd = at("scratched CDs");
  return (
    <Stage>
      <Label x={W / 2} y={400} text={"youtube.com/@thatsthemechanism".slice(0, Math.round(ease(f, at("When the code"), at("your link") + 6, 1, 30))) + (f % 16 < 8 ? "▌" : " ")} font={MONO} size={40} o={ease(f, at("When the code") - 4, at("When the code") + 2)} />
      {bytesOf.map((b, i) => {
        const s = pop(f, cut + i * 2, fps), x = 202 + (i % 6) * 135, y = 490 + Math.floor(i / 6) * 135;
        return (
          <g key={i} transform={`translate(${x} ${y}) scale(${s})`} opacity={Math.min(1, s)}>
            <rect x={-55} y={0} width={110} height={110} rx={16} fill={C.ink3} stroke={P.color} strokeWidth={4} />
            <text y={70} fill={P.color} fontFamily={MONO} fontWeight={700} fontSize={40} textAnchor="middle">{b}</text>
          </g>
        );
      })}
      {Array.from({ length: 12 }).map((_, i) => {
        const s = pop(f, adds + i * 2, fps), x = 202 + (i % 6) * 135, y = 790 + Math.floor(i / 6) * 135;
        return (
          <g key={i} transform={`translate(${x} ${y}) scale(${s})`} opacity={Math.min(1, s)}>
            <rect x={-55} y={0} width={110} height={110} rx={16} fill={C.amber} />
            <text y={74} fill={C.ink} fontFamily={MONO} fontWeight={700} fontSize={48} textAnchor="middle">+</text>
          </g>
        );
      })}
      <Label x={147} y={475} text="DATA" anchor="start" size={32} color={P.color} o={ease(f, cut, cut + 8)} />
      <Label x={147} y={775} text="REPAIR BYTES" anchor="start" size={32} color={C.amber} o={ease(f, adds, adds + 8)} />
      <g transform={`translate(${W - 80} 775) scale(${pop(f, makeAt(words, fps)("data itself."), fps)})`}><Label x={0} y={0} text="= f(DATA)" anchor="end" size={34} color={C.amber} font={MONO} /></g>
      <Label x={W / 2} y={1130} text="REED–SOLOMON (1960)" size={54} color={C.amber} o={ease(f, rs, rs + 8)} />
      {f > cd - 8 && (
        <g transform={`translate(${W / 2} 760) scale(${pop(f, cd - 6, fps)})`}>
          <rect x={-470} y={-400} width={940} height={800} rx={40} fill={C.ink} opacity={0.95} />
          <g transform={`rotate(${f * 6})`}>
            <circle r={270} fill="url(#cdgrad)" />
            <circle r={72} fill={C.ink} /><circle r={30} fill={C.ink3} />
            <path d="M-200 -60 L120 -150" stroke={C.ink} strokeWidth={8} strokeLinecap="round" />
            <path d="M-140 110 L190 30" stroke={C.ink} strokeWidth={5} strokeLinecap="round" />
          </g>
          <defs>
            <linearGradient id="cdgrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stopColor="#D9DDE6" /><stop offset="0.4" stopColor={P.color} /><stop offset="0.6" stopColor="#F2C6FF" /><stop offset="1" stopColor="#C8CCD6" />
            </linearGradient>
          </defs>
          <Label x={0} y={350} text="▶ STILL PLAYING" size={46} color={C.green} />
        </g>
      )}
    </Stage>
  );
};

const Repair: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s3 = at("Those extra bytes"), reb = at("rebuilding"), hi = at("At the highest"), rest = at("restore");
  return (
    <Stage>
      {Array.from({ length: 10 }).map((_, i) => {
        const broken = i === 2 || i === 5 || i === 7, tBreak = s3 + 8, fixed = f > reb + i;
        const x = 200 + (i % 5) * 170, y = 330 + Math.floor(i / 5) * 150;
        const gone = broken && f > tBreak && !fixed;
        return (
          <g key={i} transform={`translate(${x} ${y}) scale(${broken && f > rest ? 1 + 0.25 * Math.max(0, 1 - Math.abs(f - rest - 4 - i) / 6) : 1})`}>
            <rect x={-60} y={0} width={120} height={120} rx={16} fill={gone ? "transparent" : broken && fixed ? C.amber : C.ink3}
              stroke={gone ? C.red : P.color} strokeWidth={4} strokeDasharray={gone ? "10 8" : "0"} />
            {gone && <text y={80} fill={C.red} fontSize={64} fontFamily="sans-serif" fontWeight={700} textAnchor="middle">✕</text>}
          </g>
        );
      })}
      <Label x={W / 2} y={665} text={f > reb ? "MISSING BYTES → REBUILT" : "BYTES GO MISSING"} size={46} color={f > reb ? C.amber : C.red} />
      {[["L", 7], ["M", 15], ["Q", 25], ["H", 30]].map(([lv, pct], i) => {
        const t = hi + i * 4, grow = ease(f, t, t + 14), isH = lv === "H", h = (pct as number) * 9 * grow, x = 240 + i * 200;
        return (
          <g key={lv as string} opacity={ease(f, t - 4, t + 4)}>
            <rect x={x - 60} y={1110 - h} width={120} height={h} rx={10} fill={isH ? C.amber : C.ink3} stroke={isH ? C.amber : C.line} strokeWidth={3} />
            <Label x={x} y={1110 - h - 18} text={`${Math.round((pct as number) * grow)}%`} size={42} color={isH ? C.amber : C.dim} />
            <Label x={x} y={1165} text={lv as string} size={46} color={isH ? C.amber : C.paper} />
          </g>
        );
      })}
    </Stage>
  );
};

const Budget: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s4 = at("So a logo"), safe = at("is safe."), gl = at("Glare");
  const dmg = at("damage the code"), real = at("In real tests"), p15 = at("15%");
  const logo = 0.15 * ease(f, s4 + 4, safe + 4), glare = ease(f, gl, gl + 10);
  return (
    <Stage>
      <QRCard cx={W / 2} cy={660} size={580} logo={logo} rot={f * 2} glare={glare} />
      <Pill x={W / 2} y={330} w={520} text="= PLANNED-FOR DAMAGE" color={C.green} s={pop(f, dmg, fps) * ease(f, gl, gl + 6, 1, 0)} />
      <g transform="translate(140 1040)">
        <rect width={800} height={44} rx={22} fill={C.ink3} />
        <rect width={800 * (logo / 0.3)} height={44} rx={22} fill={C.green} />
        <rect x={800 * (logo / 0.3)} width={800 * 0.33 * glare} height={44} fill={C.amber} />
        <line x1={800 * (0.17 / 0.3)} x2={800 * (0.17 / 0.3)} y1={-14} y2={58} stroke={C.red} strokeWidth={5} transform={`translate(0 ${-30 * (1 - pop(f, p15, fps))})`} opacity={ease(f, real, real + 6)} />
        <Label x={0} y={-22} text={`LOGO ≈ ${Math.round(logo * 100)}% OF AREA`} size={36} anchor="start" color={C.green} />
        <Label x={800} y={104} text={glare > 0.1 ? "+ GLARE & SCRATCHES" : "REPAIR BUDGET"} size={34} anchor="end" color={glare > 0.1 ? C.amber : C.dim} />
      </g>
    </Stage>
  );
};

const Finders: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const corner = at("three big corner"), over = at("it's over"), notData = at("Those aren't data"), how = at("They are how");
  return (
    <Stage>
      <QRCard cx={W / 2} cy={CY} size={640} logo={0.11} rot={f * 2} finderGlow={ease(f, corner, corner + 8)}
        coverTL={ease(f, over - 6, over + 3)} shake={f > over && f < over + 12 ? 1 : 0} />
      <Viewfinder cx={W / 2} cy={CY} size={640} color={C.red} o={ease(f, how, how + 6)} jitter={1} />
      <Label x={W / 2} y={CY - 400} text="FINDER PATTERNS ≠ DATA" size={46} color={P.color} o={ease(f, notData, notData + 8)} />
    </Stage>
  );
};

const Final: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const sp = at("carries"), lab = at("own spare");
  return (
    <Stage>
      <QRCard cx={W / 2} cy={CY} size={640} logo={0.11} rot={f * 2} />
      {/* spare parts = repair bytes orbiting the code */}
      {Array.from({ length: 8 }).map((_, i) => {
        const a = (i / 8) * Math.PI * 2 + f / 25, r = 420 * ease(f, sp - 6 + i, sp + 10 + i);
        return <rect key={i} x={W / 2 + Math.cos(a) * r - 26} y={CY + Math.sin(a) * r * 0.9 - 26} width={52} height={52} rx={10} fill={C.amber} opacity={ease(f, sp - 6 + i, sp + 2 + i)} />;
      })}
      <Label x={W / 2} y={CY + 450} text="SPARE PARTS INCLUDED" size={46} color={C.amber} o={ease(f, lab, lab + 6)} />
    </Stage>
  );
};

export const QRVideo: React.FC = () => {
  const { fps, durationInFrames: D } = useVideoConfig();
  const at = makeAt(words, fps);
  const s2 = at("When the code"), s3 = at("Those extra bytes"), s4 = at("So a logo"), s5 = at("But cover"),
    card = at("That's the mechanism"), fin = at("A QR code carries"), loop = D - LOOP_FRAMES;
  const cut = at("cut into bytes"), adds = at("adds extra bytes"), cd = at("scratched CDs"), reb = at("rebuilding"), hi = at("At the highest"),
    over = at("it's over"), corner = at("three big corner"), gl = at("Glare"), sp = at("spare parts");
  const cues = [
    cue(4, "pop", 0.8), cue(at("Your camera"), "tick", 0.8), cue(at("anyway."), "confirm", 0.9),
    cue(s2 - 5, "whoosh"), ...Array.from({ length: 6 }, (_, i) => cue(cut + i * 4, "tick", 0.6)), cue(adds, "pop"), cue(adds + 12, "pop", 0.7),
    cue(at("data itself."), "tick", 0.7), cue(at("That's Reed-Solomon"), "click"), cue(cd - 6, "whoosh", 0.7), cue(cd, "clank", 0.6),
    cue(s3 - 5, "whoosh"), cue(s3 + 8, "glitch", 0.8), cue(reb + 2, "confirm", 0.7), cue(hi, "tick", 0.6), cue(hi + 4, "tick", 0.6), cue(hi + 8, "tick", 0.6), cue(hi + 12, "pop", 0.9),
    cue(s4 - 5, "whoosh"), cue(at("damage the code"), "pop", 0.8), cue(at("15%"), "tick", 0.8), cue(at("is safe."), "confirm", 0.7), cue(at("30%"), "pop", 0.8), cue(at("same math"), "tick", 0.6), cue(gl, "glitch", 0.7),
    cue(s5 - 5, "whoosh", 0.8), cue(corner, "pop", 0.8), cue(over, "thud", 1), cue(over + 2, "error", 0.8),
    cue(sp, "pop", 0.8),
  ];
  return (
    <EpisodeShell audio="01-qr-code.wav" words={words} pillar={P} ep="001" source="DENSO WAVE" cardAt={card} cardUntil={fin} cues={cues} hook={<Hook />}
      chapters={[{ at: 0, label: "A LOGO ON A QR" }, { at: s2, label: "BYTES + REPAIR BYTES" }, { at: s3, label: "REBUILDING" }, { at: s4, label: "THE LOGO BUDGET" }, { at: s5, label: "THE CORNERS" }]}>
      <Shot from={0} to={s2} inT="none" outT="push" cam={[{ at: at("Your camera"), kind: "push", s: 1.06 }, { at: at("anyway."), kind: "punch", s: 1.2, y: -60 }]} hud={<Verdict phrase="anyway." text="✓ LINK OPENS" color={C.green} />}><Hook /></Shot>
      <Shot from={s2} to={s3} inT="push" outT="whip" cam={[{ at: 0, kind: "settle", s: 1.0, y: 90, dur: 1 }, { at: adds, kind: "glide", s: 1.04, y: 40 }, { at: at("calculated"), kind: "glide", s: 1.07, x: 20, y: 60 }, { at: at("error correction"), kind: "glide", s: 1.06, x: -30, y: 50 }, { at: at("same math"), kind: "push", s: 1.12, x: 0, y: 30 }, { at: cd - 6, kind: "pull", s: 0.96, y: 0 }]}><Bytes /></Shot>
      <Shot from={s3} to={s4} inT="whip" outT="push" cam={[{ at: reb, kind: "punch", s: 1.18, y: 80 }, { at: hi - 4, kind: "glide", s: 1.0, y: -40 }, { at: hi + 14, kind: "punch", s: 1.12, x: -90, y: 20 }, { at: at("a scanner"), kind: "glide", s: 1.07, x: -40, y: 10 }, { at: at("30%"), kind: "glide", s: 1.0, x: 0, y: 0 }]}><Repair /></Shot>
      <Shot from={s4} to={s5} inT="push" outT="whipUp" cam={[{ at: s4, kind: "push", s: 1.05, dur: 45 }, { at: at("In real tests"), kind: "glide", s: 1.08, y: -60 }, { at: gl, kind: "punch", s: 1.14, y: 0 }]}><Budget /></Shot>
      <Shot from={s5} to={card} inT="whipUp" outT="push" cam={[{ at: corner, kind: "push", s: 1.08 }, { at: over, kind: "punch", s: 1.2, x: 170, y: 100 }, { at: at("Those aren't data"), kind: "pull", s: 1.0, x: 0, y: 0 }]} hud={<Verdict phrase="it's over" until="Those aren't data" text="✕ NO SCAN" color={C.red} textColor="white" w={400} />}><Finders /></Shot>
      <Shot from={fin} to={loop} inT="push" outT="whip" cam={[{ at: sp, kind: "pull", s: 0.94 }]}><Final /></Shot>
    </EpisodeShell>
  );
};
