import React from "react";
import { useVideoConfig } from "remotion";
import words from "../01-qr-code.captions.json";
import qr from "../qr-matrix.json";
import { ScanLine, X, type LucideIcon } from "lucide-react";
import { C, EpisodeShell, GearG, Label, LOOP_FRAMES, MONO, PILLARS, Pill, ProofCard, Shot, Stage, TitleHook, cue, ease, makeAt, pop, popOpacity, popScale, useG } from "../brand";

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
  const h = size / 2 + 26 + Math.sin(f / 3) * jitter * 20, L = 64;
  return (
    <g transform={`translate(${cx + jitter * Math.sin(f * 1.7) * 30} ${cy + jitter * Math.cos(f * 1.3) * 20})`} opacity={o}>
      {[[-1, -1], [1, -1], [-1, 1], [1, 1]].map(([dx, dy], i) => (
        <path key={i} d={`M${dx * h} ${dy * (h - L)} L${dx * h} ${dy * h} L${dx * (h - L)} ${dy * h}`} stroke={color} strokeWidth={10} fill="none" strokeLinecap="round" />
      ))}
    </g>
  );
};

const W = 1080, CY = 815;
const bytesOf = "youtube.com/@thatsthemechanism".split("").slice(0, 12).map((ch) => ch.charCodeAt(0).toString(16).toUpperCase());

/** Shot 1 = title-as-hook + scale reveal (also frozen at frame 0 by LoopBack: f=0 is zoomed 2.3x into the bright QR + gear). */
const Hook: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const cam = at("Your camera");
  const z = ease(f, 3, 34, 2.35, 1.0); // scale reveal: detail -> whole code
  const cx = W / 2, cy = CY;
  return (
    <>
      <Stage>
        <g transform={`translate(${cx} ${cy}) scale(${z}) translate(${-cx} ${-cy})`}>
          <QRCard cx={cx} cy={cy} size={560} logo={0.12} rot={f * 2} />
          <Viewfinder cx={cx} cy={cy} size={560} color={f > cam ? C.green : C.paper} o={ease(f, cam - 6, cam + 2)} />
          {f > cam && <rect x={cx - 300} y={cy - 300 + ((f - cam) * 28) % 600} width={600} height={6} fill={C.green} opacity={0.85} />}
        </g>
      </Stage>
      {/* r5: title leaves before the push-out so the transition never flings it into the platform UI zone */}
      <TitleHook t={["THE CODE THAT", "REPAIRS", "ITSELF"]} top={280} o={ease(f, at("When the code") - 9, at("When the code") - 3, 1, 0)} />
    </>
  );
};

/** Screen-space verdict pills (outside the camera). */
const Verdict: React.FC<{ phrase: string; until?: string; text: string; color: string; textColor?: string; w?: number; icon?: LucideIcon }> = ({ phrase, until, text, color, textColor, w = 420, icon }) => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const a = at(phrase), u = until ? at(until) : 1e9;
  if (f < a || f > u + 6) return null;
  return <Stage><Pill x={W / 2} y={1152} w={w} text={text} color={color} textColor={textColor} icon={icon} s={pop(f, a, fps) * ease(f, u, u + 6, 1, 0)} /></Stage>;
};

const Bytes: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s2 = at("When the code"), cut = at("cut into bytes"), adds = at("adds extra bytes"), rs = at("error correction"), cd = at("scratched CDs");
  const k = ease(f, s2, s2 + 12), split = ease(f, cut, cut + 14), cdShow = ease(f, cd - 6, cd + 6);
  const url = "youtube.com/@thatsthemechanism";
  const typed = Math.min(url.length, Math.floor(ease(f, s2 + 2, cut, 0, url.length)));
  return (
    <Stage>
      <text x={W / 2} y={370} fill={C.paper} fontFamily={MONO} fontSize={36} fontWeight={700} textAnchor="middle" opacity={k}
        style={{ paintOrder: "stroke", stroke: C.ink, strokeWidth: 6 }}>{url.slice(0, typed)}</text>
      <Label x={115} y={445} text="DATA" anchor="start" size={30} color={P.color} o={split} />
      {bytesOf.map((b, i) => {
        const s = pop(f, cut + i * 1.4, fps), x = 115 + (i % 6) * 145, y = 470 + Math.floor(i / 6) * 116;
        const pulse = f > adds ? Math.max(0, Math.sin((f - adds) * 0.22 - i * 0.55)) : 0;
        return (
          <g key={i} transform={`translate(${x + 60} ${y + 44}) scale(${popScale(s) * (1 + 0.06 * pulse)})`} opacity={popOpacity(s)}>
            <rect x={-60} y={-44} width={120} height={88} rx={14} fill={pulse > 0.6 ? "#233648" : C.ink2} stroke={pulse > 0.6 ? C.amber : P.color} strokeWidth={4} />
            <text y={12} fill={C.paper} fontFamily={MONO} fontSize={34} fontWeight={700} textAnchor="middle">{b}</text>
          </g>
        );
      })}
      <Label x={115} y={740} text="REPAIR BYTES" anchor="start" size={30} color={C.amber} o={ease(f, adds, adds + 6)} />
      <Label x={965} y={740} text="= f(DATA)" anchor="end" size={30} color={C.amber} o={ease(f, at("calculated"), at("calculated") + 10)} />
      {Array.from({ length: 12 }).map((_, i) => {
        const s = pop(f, adds + i * 1.6, fps), x = 115 + (i % 6) * 145, y = 766 + Math.floor(i / 6) * 116;
        return (
          <g key={i} transform={`translate(${x + 60} ${y + 44}) scale(${popScale(s)})`} opacity={popOpacity(s)}>
            <rect x={-60} y={-44} width={120} height={88} rx={14} fill={C.amber} opacity={0.82 + 0.18 * Math.sin(f * 0.2 - i * 0.5)} />
            <text y={13} fill={C.ink} fontFamily={MONO} fontSize={40} fontWeight={700} textAnchor="middle">+</text>
          </g>
        );
      })}
      <Label x={W / 2} y={1075} text="REED-SOLOMON (1960)" size={40} color={C.paper} o={ease(f, rs, rs + 10)} />
      {cdShow > 0 && (
        <g transform={`translate(${W / 2} 1080) scale(${cdShow})`}>
          <rect x={-430} y={-68} width={860} height={136} rx={24} fill={C.ink2} stroke={C.amber} strokeWidth={4} />
          <g transform={`translate(-310 0) rotate(${f * 8})`}>
            <circle r={48} fill={C.paper} opacity={0.9} /><circle r={15} fill={C.ink} />
            <line x1={-36} y1={-16} x2={36} y2={16} stroke={C.red} strokeWidth={5} />
          </g>
          <Label x={-230} y={14} text="STILL PLAYING" anchor="start" size={44} color={C.amber} />
        </g>
      )}
    </Stage>
  );
};

const Repair: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s3 = at("Those extra bytes"), reb = at("rebuilding"), hi = at("At the highest"), p30 = at("30%");
  const mode = f < hi ? 0 : 1;
  const fix = ease(f, reb, reb + 16), g30 = ease(f, p30, p30 + 16);
  const missing = [2, 5, 7];
  return (
    <Stage>
      {mode === 0 && (
        <g>
          {Array.from({ length: 10 }).map((_, i) => {
            const x = 115 + (i % 5) * 172, y = 370 + Math.floor(i / 5) * 145, dead = missing.includes(i), rebuilt = dead && fix > (i === 2 ? 0.2 : i === 5 ? 0.5 : 0.8);
            return (
              <g key={i} transform={`translate(${x} ${y})`}>
                <rect width={144} height={116} rx={16} fill={rebuilt ? C.amber : dead ? C.ink : C.ink2} stroke={dead && !rebuilt ? C.red : rebuilt ? C.amber : P.color} strokeWidth={4} strokeDasharray={dead && !rebuilt ? "12 10" : undefined} />
                {dead && !rebuilt && <X x={44} y={30} width={56} height={56} color={C.red} strokeWidth={4} />}
              </g>
            );
          })}
          <Label x={W / 2} y={715} text={f > reb ? "MISSING BYTES: REBUILT" : "BYTES GO MISSING"} size={46} color={f > reb ? C.amber : C.red} />
        </g>
      )}
      {mode === 1 && (
        <g>
          <QRCard cx={W / 2} cy={700} size={580} logo={0.12} rot={f * 1.8} />
          <rect x={W / 2 - 245} y={700 - 245} width={490} height={490 * 0.3 * g30} rx={18} fill={C.amber} opacity={0.28 + 0.14 * Math.sin(f / 4)} stroke={C.amber} strokeWidth={5} />
          <rect x={W / 2 - 255} y={700 - 245 + ((f * 18) % 490)} width={510} height={6} rx={3} fill={C.amber} opacity={0.65} />
          <Label x={W / 2} y={1080} text={`${Math.round(30 * g30)}% REBUILDABLE (LEVEL H)`} size={42} color={C.amber} />
        </g>
      )}
      {f > s3 + 4 && mode === 0 && (
        <path d="M540,940 C380,940 340,760 440,580" fill="none" stroke={C.amber} strokeWidth={8} strokeDasharray="16 14" strokeDashoffset={-f * 4} strokeLinecap="round" />
      )}
    </Stage>
  );
};

/** Shot 4: Logo budget bar, then Real Photo ProofCard of a real torn QR code ("Glare and scratches..."). */
const Budget: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s4 = at("So a logo"), p15 = at("15%"), gl = at("Glare"), s5 = at("But cover");
  const showPhoto = f >= gl;
  const g15 = ease(f, p15 - 6, p15 + 10);
  const logoA = 0.04 + 0.11 * ease(f, s4, s4 + 18) + 0.03 * g15;
  const barX = 110, barW = 860, barY = 1040;
  return (
    <>
      {!showPhoto && (
        <Stage>
          <QRCard cx={W / 2} cy={650} size={580} logo={logoA} rot={f * 1.4} />
          <Label x={W / 2} y={1000} text={f >= p15 ? "LOGO ≈ 15% OF AREA" : "PLANNED-FOR DAMAGE"} size={42} color={f >= p15 ? C.green : C.amber} />
          <rect x={barX} y={barY} width={barW} height={42} rx={21} fill={C.ink2} stroke={C.line} strokeWidth={4} />
          <rect x={barX + 4} y={barY + 4} width={(barW - 8) * (logoA / 0.3)} height={34} rx={17} fill={C.green} />
          <Label x={barX} y={barY + 86} text="REPAIR BUDGET: 30%" anchor="start" size={32} color={C.paper} />
        </Stage>
      )}
      {showPhoto && (
        <ProofCard src="photos/01-qr-code--qr-code-damaged.jpg" tag="TORN, STILL A CODE"
          credit="PHOTO: BOBMATH (WIKIMEDIA COMMONS) · CC0" aspect={1}
          focus={[0.58, 0.52, 0.96, 0.96]} focusLabel="MISSING CHUNK"
          startFrame={gl} duration={Math.max(45, s5 - gl)} />
      )}
    </>
  );
};

const Finders: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const corner = at("three big corner"), over = at("it's over"), notData = at("Those aren't data");
  const cov = ease(f, corner, corner + 12), shk = f >= over && f < over + 16 ? 1 : 0;
  return (
    <Stage>
      <QRCard cx={W / 2} cy={700} size={620} logo={0.13} finderGlow={ease(f, notData, notData + 8)} coverTL={cov} shake={shk} rot={f} />
      <Viewfinder cx={W / 2} cy={700} size={620} color={f >= over ? C.red : C.paper} o={1} jitter={shk} />
      {f >= notData && <Label x={W / 2} y={345} text="FINDER PATTERNS ≠ DATA" size={46} color={P.color} o={ease(f, notData, notData + 8)} />}
    </Stage>
  );
};

/** Final shot: repair blocks pop in and SETTLE into a neat orbital ring >= 1.5 s before loop whip (L-16). */
const Final: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const fin = at("A QR code carries"), lab = at("own");
  const settleEnd = fin + 14;
  const rotSlow = f * 1.6;
  return (
    <Stage>
      <QRCard cx={W / 2} cy={CY - 40} size={540} logo={0.13} rot={rotSlow} />
      {Array.from({ length: 8 }).map((_, i) => {
        const a = (i / 8) * Math.PI * 2 + 0.35;
        const r = 385 * ease(f, fin + i, fin + 14 + i);
        const bob = f > settleEnd ? Math.sin((f - settleEnd) / 7 + i) * 8 : 0;
        return <rect key={i} x={W / 2 + Math.cos(a) * r - 24} y={CY - 40 + Math.sin(a) * r * 0.9 - 24 + bob} width={48} height={48} rx={10} fill={C.amber} opacity={ease(f, fin + i, fin + 6 + i)} />;
      })}
      <Label x={W / 2} y={CY + 410} text="SPARE PARTS INCLUDED" size={46} color={C.amber} o={ease(f, lab - 12, lab - 4)} />
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
      cardAt={card} cardUntil={fin} cues={cues} hook={<Hook />}
      chapters={[{ at: 0, label: "A LOGO ON A QR" }, { at: s2, label: "BYTES + REPAIR BYTES" }, { at: s3, label: "REBUILDING" }, { at: s4, label: "THE LOGO BUDGET" }, { at: s5, label: "THE CORNERS" }]}>
      <Shot from={0} to={s2} inT="none" outT="push" cam={[{ at: at("Your camera"), kind: "push", s: 1.05 }, { at: at("anyway."), kind: "punch", s: 1.14, y: -30 }]} hud={<Verdict phrase="anyway." text="LINK OPENS" color={C.green} icon={ScanLine} w={460} />}><Hook /></Shot>
      <Shot from={s2} to={s3} inT="push" outT="whip" cam={[{ at: 0, kind: "settle", s: 1.0, y: 90, dur: 1 }, { at: at("cut into bytes"), kind: "punch", s: 1.1, y: 70 }, { at: adds, kind: "glide", s: 1.04, y: 40 }, { at: at("error correction"), kind: "glide", s: 1.06, x: -30, y: 50 }, { at: at("same math"), kind: "push", s: 1.1, x: 0, y: 30 }, { at: cd - 6, kind: "pull", s: 0.96, y: 0 }]}><Bytes /></Shot>
      <Shot from={s3} to={s4} inT="whip" outT="push" cam={[{ at: reb, kind: "punch", s: 1.16, y: 70 }, { at: hi - 4, kind: "glide", s: 1.0, y: -40 }, { at: hi + 14, kind: "push", s: 1.1, x: -70, y: 20 }, { at: at("30%"), kind: "pull", s: 1.0, x: 0, y: 0 }]}><Repair /></Shot>
      <Shot from={s4} to={s5} inT="push" outT="whipUp" cam={[{ at: s4, kind: "push", s: 1.05, dur: 45 }, { at: at("In real tests"), kind: "glide", s: 1.08, y: -40 }, { at: gl, kind: "pull", s: 1.0, y: 0 }]}><Budget /></Shot>
      <Shot from={s5} to={card} inT="whipUp" outT="push" cam={[{ at: corner, kind: "push", s: 1.08 }, { at: over, kind: "punch", s: 1.18, x: 160, y: 90 }, { at: at("Those aren't data"), kind: "pull", s: 1.0, x: 0, y: 0 }]} hud={<Verdict phrase="it's over" until="Those aren't data" text="NO SCAN" color={C.red} textColor={C.ink} w={400} icon={X} />}><Finders /></Shot>
      <Shot from={fin} to={loop} inT="push" outT="whip" cam={[{ at: fin, kind: "pull", s: 0.96, dur: 12 }]}><Final /></Shot>
    </EpisodeShell>
  );
};
