import React from "react";
import { useVideoConfig } from "remotion";
import words from "../03-sky.captions.json";
import { C, EpisodeShell, Label, LOOP_FRAMES, MONO, PILLARS, Pill, Shot, Stage, cue, ease, makeAt, pop, useG } from "../brand";

const P = PILLARS.sci;
const SPECTRUM = ["#8F5BFF", "#3D7BFF", "#2EC4F0", "#3DDC97", "#F5E14B", "#FF9F2E", "#FF4D3D"];
const BLUE = "#3D8BFF", ORANGE = "#FF8A2E", RED = "#FF4D3D";
const wave = (x0: number, y0: number, len: number, lambda: number, amp: number, phase: number) => {
  const pts: string[] = [];
  for (let x = 0; x <= len; x += 4) pts.push(`${x0 + x},${y0 + Math.sin((x / lambda) * Math.PI * 2 - phase) * amp}`);
  return `M${pts.join("L")}`;
};

/** Hook + loop target: noon above, sunset below, the same sun. */
const Split: React.FC<{ tag?: string }> = ({ tag = "SAME TRICK" }) => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const tagAt = tag === "SAME TRICK" ? at("same trick") : at("leftovers");
  const sunDrop = ease(f, 0, 40, -70, 0) + 20 * Math.sin(f / 25);
  return (
    <Stage>
      <defs>
        <linearGradient id="noon" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#1F5FD8" /><stop offset="1" stopColor="#8CC8FF" /></linearGradient>
        <linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#2A2350" /><stop offset="0.45" stopColor="#C2456B" /><stop offset="0.8" stopColor="#FF8A2E" /><stop offset="1" stopColor="#FFC25A" /></linearGradient>
        <clipPath id="top"><rect x={80} y={300} width={920} height={420} rx={36} /></clipPath>
        <clipPath id="bot"><rect x={80} y={740} width={920} height={420} rx={36} /></clipPath>
      </defs>
      <g clipPath="url(#top)">
        <rect x={80} y={300} width={920} height={420} fill="url(#noon)" />
        <circle cx={780} cy={410 + sunDrop * 0.3} r={58} fill="#FFF6D8" /><circle cx={780} cy={410 + sunDrop * 0.3} r={96} fill="#FFF6D8" opacity={0.25} />
        {Array.from({ length: 7 }).map((_, i) => { const a = (i / 7) * Math.PI * 2 + f / 20; return <line key={i} x1={780} y1={410} x2={780 + Math.cos(a) * 150} y2={410 + Math.sin(a) * 150} stroke={BLUE} strokeWidth={6} opacity={0.5} />; })}
        <rect x={80} y={660} width={920} height={60} fill="#2F6B3A" />
      </g>
      <g clipPath="url(#bot)">
        <rect x={80} y={740} width={920} height={420} fill="url(#dusk)" />
        <circle cx={420} cy={1075 + sunDrop} r={74} fill="#FFD27A" /><circle cx={420} cy={1075 + sunDrop} r={136} fill="#FF9F2E" opacity={0.3} />
        <rect x={80} y={1100} width={920} height={60} fill="#1B1530" />
      </g>
      <Label x={120} y={364} text="NOON" anchor="start" size={40} color="white" />
      <Label x={120} y={804} text="SUNSET" anchor="start" size={40} color="white" />
      <g transform={`translate(540 730) scale(${pop(f, tagAt, fps)})`}>
        <rect x={-230} y={-40} width={460} height={80} rx={40} fill={C.ink} stroke={C.amber} strokeWidth={4} />
        <Label x={0} y={15} text={tag} size={42} color={C.amber} />
      </g>
    </Stage>
  );
};

const Scatter: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s2 = at("Sunlight is every"), mol = at("Air molecules"), sc = at("tiny things scatter"), col = at("every color");
  return (
    <Stage>
      {f < mol + 4 && (
        <g opacity={ease(f, mol - 4, mol + 4, 1, 0)}>
          <line x1={80} y1={720} x2={ease(f, s2, s2 + 12, 80, 470)} y2={720} stroke="white" strokeWidth={22} strokeLinecap="round" />
          <Label x={140} y={670} text="SUNLIGHT" anchor="start" size={42} />
          {SPECTRUM.map((c, i) => { const g = ease(f, col + i * 2, col + i * 2 + 12); return <line key={i} x1={470} y1={720} x2={470 + 520 * g} y2={720 + (i - 3) * 80 * g} stroke={c} strokeWidth={14} strokeLinecap="round" />; })}
          <polygon points="470,620 570,810 370,810" fill="none" stroke={C.paper} strokeWidth={4} opacity={0.6} />
        </g>
      )}
      {f >= mol - 4 && (
        <g opacity={ease(f, mol - 4, mol + 6)}>
          <g transform={`translate(540 660) scale(${pop(f, mol, fps) * (1 + 0.08 * Math.sin(f / 4))})`}>
            <circle cx={-30} r={40} fill={P.color} /><circle cx={30} r={40} fill={P.color} />
          </g>
          <Label x={540} y={570} text="N₂ / O₂ MOLECULE" size={36} color={P.color} />
          <path d={wave(60, 840, ease(f, mol, mol + 20, 0, 470), 46, 22, f / 2)} stroke={BLUE} strokeWidth={8} fill="none" />
          <path d={wave(60, 940, ease(f, mol, mol + 20, 0, 980), 110, 22, f / 3)} stroke={RED} strokeWidth={8} fill="none" />
          <Label x={540} y={1060} text="~1000× SMALLER THAN A LIGHT WAVE" size={36} o={ease(f, at("a thousand times"), at("a thousand times") + 8)} />
          {f > sc && Array.from({ length: 12 }).map((_, i) => {
            const a = (i / 12) * Math.PI * 2 + 0.3, len = ease(f, sc + i, sc + i + 14, 0, 230);
            return <line key={i} x1={540} y1={660} x2={540 + Math.cos(a) * len} y2={660 + Math.sin(a) * len} stroke={BLUE} strokeWidth={7} strokeLinecap="round" />;
          })}
        </g>
      )}
    </Stage>
  );
};

const Ratio: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const four = makeAt(words, fps)("Blue gets bounced");
  return (
    <Stage>
      {([["BLUE · 450 nm", 4.4, BLUE], ["RED · 650 nm", 1, RED]] as const).map(([lab, v, c], i) => {
        const g = ease(f, four + i * 4, four + i * 4 + 16), w = v * 160 * g;
        return (
          <g key={i} transform={`translate(110 ${520 + i * 210})`}>
            <Label x={0} y={-26} text={lab} anchor="start" size={40} color={c} />
            <rect width={w} height={90} rx={14} fill={c} />
            <Label x={w + 20} y={62} text={`${(v * g).toFixed(1)}×`} anchor="start" size={50} />
          </g>
        );
      })}
      <Label x={540} y={980} text="SCATTERING ∝ 1 / λ⁴" size={58} color={C.amber} font={MONO} o={ease(f, four + 10, four + 20)} />
      <Label x={540} y={1050} text="Rayleigh scattering" size={36} color={C.dim} weight={500} o={ease(f, four + 14, four + 24)} />
    </Stage>
  );
};

const EX = 430, EY = 740, ER = 210, AR = 310;
/** Persistent world for noon + sunset: one Earth, one Sun; the camera glides between the two observers. */
const Earth: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s3 = at("At noon"), s4 = at("At sunset"), scb = at("scattered blue"), sky = at("That's the sky"), dz = at("dozens"), out = at("scattered out"), se = at("someone else's"), wv = at("What survives");
  const noon = f < s4;
  const yb = EY - ER, xStart = 898;
  const g = ease(f, s4 + 2, dz + 6), xHead = xStart + (EX - xStart) * g, red = ease(f, wv, wv + 12);
  const glowRight = noon ? ease(f, sky, sky + 10) : ease(f, se, se + 10);
  return (
    <Stage>
      <defs>
        <linearGradient id="beam" gradientUnits="userSpaceOnUse" x1={xStart} y1={yb} x2={EX} y2={yb}>
          <stop offset="0" stopColor="white" /><stop offset="0.55" stopColor="#FFD27A" /><stop offset="1" stopColor={RED} />
        </linearGradient>
      </defs>
      <circle cx={EX} cy={EY} r={AR} fill={BLUE} opacity={0.16} />
      <circle cx={EX} cy={EY} r={AR} fill="none" stroke={BLUE} strokeWidth={3} opacity={0.5} strokeDasharray="8 10" transform={`rotate(${f / 6} ${EX} ${EY})`} />
      <circle cx={EX} cy={EY} r={ER} fill="#1D3B2C" stroke="#3E7A57" strokeWidth={6} />
      <path d={`M${EX} ${EY - ER} A${ER} ${ER} 0 0 0 ${EX} ${EY + ER} Z`} fill="#000" opacity={0.45} />
      <g transform={`translate(${EX} ${EY - ER})`}><circle r={70 * red} fill={ORANGE} opacity={0.4 * red} /><circle r={14} fill={C.paper} /></g>
      <g transform={`translate(${EX + ER} ${EY})`}><circle r={70 * glowRight} fill={BLUE} opacity={0.45 * glowRight} /><circle r={14} fill={C.paper} /></g>
      <g transform={`translate(960 ${noon ? EY : yb})`}><circle r={110} fill="#FFF1C4" opacity={0.2} /><circle r={62} fill="#FFF1C4" /></g>
      {noon && (
        <>
          <line x1={898} y1={EY} x2={ease(f, s3, s3 + 14, 898, EX + ER + 16)} y2={EY} stroke="white" strokeWidth={14} strokeLinecap="round" />
          {f > scb && Array.from({ length: 9 }).map((_, i) => {
            const a = Math.PI + (i - 4) * 0.33, gg = ease(f, scb + i * 2, scb + i * 2 + 14), ox = EX + ER, oy = EY;
            const sx = ox + Math.cos(a + Math.PI) * 130 + 10, sy = oy + Math.sin(a + Math.PI) * 130;
            return <line key={i} x1={sx} y1={sy} x2={sx + (ox - sx) * gg * 0.85} y2={sy + (oy - sy) * gg * 0.85} stroke={BLUE} strokeWidth={8} strokeLinecap="round" />;
          })}
          <Label x={EX + ER + 20} y={EY + 100} text="YOU, AT NOON" size={36} o={ease(f, s3 + 6, s3 + 14)} />
        </>
      )}
      {!noon && (
        <>
          <line x1={xStart} y1={yb} x2={xHead} y2={yb} stroke="url(#beam)" strokeWidth={14} strokeLinecap="round" />
          <g opacity={ease(f, dz, dz + 8)}>
            <line x1={EX + 290} y1={yb - 60} x2={EX} y2={yb - 60} stroke={C.amber} strokeWidth={4} />
            <line x1={EX + 290} y1={yb - 75} x2={EX + 290} y2={yb - 45} stroke={C.amber} strokeWidth={4} />
            <line x1={EX} y1={yb - 75} x2={EX} y2={yb - 45} stroke={C.amber} strokeWidth={4} />
            <Label x={EX + 145} y={yb - 92} text="DOZENS × MORE AIR" size={40} color={C.amber} />
          </g>
          {f > out && Array.from({ length: 5 }).map((_, i) => {
            const x0 = 840 - i * 85, gg = ease(f, out + i * 3, out + i * 3 + 16);
            const tx = EX + ER * Math.cos(-0.25 - i * 0.18), ty = EY + ER * Math.sin(-0.25 - i * 0.18);
            return <line key={i} x1={x0} y1={yb} x2={x0 + (tx - x0) * 0.8 * gg} y2={yb + (ty - yb) * 0.8 * gg} stroke={BLUE} strokeWidth={7} strokeLinecap="round" />;
          })}
          <Label x={EX + ER + 40} y={EY + 110} text="SOMEONE ELSE'S AFTERNOON" size={36} color={BLUE} anchor="end" o={ease(f, se, se + 8)} />
          <Label x={EX - 40} y={yb - 30} text="YOU, AT SUNSET" anchor="end" size={36} color={red > 0.5 ? ORANGE : C.paper} o={ease(f, s4 + 6, s4 + 14)} />
        </>
      )}
    </Stage>
  );
};

/** Screen-space verdicts for the Earth world (outside the camera). */
const EarthHud: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s3 = at("At noon"), s4 = at("At sunset"), orr = at("orange and red");
  return (
    <Stage>
      {f < s4 && <Pill x={540} y={1150} w={600} text="SHORT PATH THROUGH AIR" color={BLUE} textColor="white" s={pop(f, s3 + 10, fps)} />}
      {f >= s4 && <Pill x={540} y={1150} w={620} text={f >= orr ? "ORANGE + RED SURVIVE" : "LONG PATH THROUGH AIR"} color={f >= orr ? ORANGE : C.amber} s={pop(f, s4 + 10, fps) * (f >= orr ? pop(f, orr, fps) : 1)} />}
    </Stage>
  );
};

export const SkyVideo: React.FC = () => {
  const { fps, durationInFrames: D } = useVideoConfig();
  const at = makeAt(words, fps);
  const s2 = at("Sunlight is every"), four = at("Blue gets bounced"), s3 = at("At noon"), s4 = at("At sunset"),
    card = at("That's the mechanism"), fin = at("Your sunset is"), loop = D - LOOP_FRAMES;
  const mol = at("Air molecules"), sc = at("tiny things scatter"), scb = at("scattered blue"), dz = at("dozens"), out = at("scattered out"), wv = at("What survives"), orr = at("orange and red");
  const cues = [
    cue(at("same trick"), "pop", 0.9), cue(s2 - 5, "whoosh"), cue(at("every color"), "tick", 0.6), cue(mol, "pop", 0.8), cue(at("light wave"), "tick", 0.6), cue(sc, "glitch", 0.5), cue(at("short waves"), "pop", 0.6),
    cue(four, "thud", 0.6), cue(four + 4, "tick", 0.6), cue(four + 8, "tick", 0.6), cue(four + 16, "pop", 0.8), cue(at("four times"), "thud", 0.5),
    cue(s3 - 5, "whoosh"), cue(scb, "tick", 0.6), cue(at("That's the sky"), "confirm", 0.6),
    cue(s4 - 2, "whoosh", 0.7), cue(dz, "pop", 0.8), cue(at("Along the way"), "whoosh", 0.4), cue(out, "tick", 0.6), cue(at("afternoon"), "pop", 0.6), cue(out + 6, "tick", 0.6), cue(wv, "riser", 0.4), cue(orr, "pop", 0.9),
    cue(at("leftovers"), "pop", 0.8),
  ];
  return (
    <EpisodeShell audio="03-sky.wav" words={words} pillar={P} ep="003" source="MET OFFICE · NOAA" cardAt={card} cardUntil={fin} cues={cues} hook={<Split />}
      chapters={[{ at: 0, label: "SAME TRICK?" }, { at: s2, label: "WHAT AIR DOES" }, { at: four, label: "BLUE VS RED" }, { at: s3, label: "NOON" }, { at: s4, label: "SUNSET" }]}>
      <Shot from={0} to={s2} inT="none" outT="push" cam={[{ at: 0, kind: "push", s: 1.05, y: 10, dur: 40 }, { at: at("same trick"), kind: "punch", s: 1.08, y: 20 }]}><Split /></Shot>
      <Shot from={s2} to={four} inT="push" outT="cut" cam={[{ at: mol, kind: "push", s: 1.12, y: 50 }, { at: sc, kind: "punch", s: 1.2, y: 40 }, { at: at("short waves"), kind: "pull", s: 1.05, y: 20 }]}><Scatter /></Shot>
      <Shot from={four} to={s3} inT="cut" outT="whip" cam={[{ at: four + 16, kind: "push", s: 1.08, dur: 30 }, { at: at("four times"), kind: "punch", s: 1.16, x: 60, y: 60 }]}><Ratio /></Shot>
      <Shot from={s3} to={card} inT="whip" outT="push" cam={[
        { at: s3, kind: "glide", s: 1.1, x: -80, y: 0, dur: 20 },             // to the noon observer
        { at: scb, kind: "push", s: 1.2, x: -150, y: 0 },
        { at: s4, kind: "glide", s: 1.1, x: 0, y: 110, dur: 24 },             // glide up to the sunset observer
        { at: at("Along the way"), kind: "glide", s: 1.04, x: 30, y: 60 },
        { at: out, kind: "pull", s: 0.98, x: 0, y: 30 },
        { at: wv, kind: "punch", s: 1.2, x: 110, y: 150 },
      ]} hud={<EarthHud />}><Earth /></Shot>
      <Shot from={fin} to={loop} inT="push" outT="whip"><Split tag="SAME LIGHT, LATER" /></Shot>
    </EpisodeShell>
  );
};
