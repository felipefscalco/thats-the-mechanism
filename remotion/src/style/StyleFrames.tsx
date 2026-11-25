import React from "react";
import { AbsoluteFill, Img, getInputProps, staticFile, useCurrentFrame } from "remotion";
import { C, DISPLAY, MONO, SANS, LAYOUT, PILLARS, Pillar, Background, BrandChip, Gear, Pill } from "../brand";
import { Check } from "lucide-react";

/** Round-4 style frames (stills for approval before animating). Props: ep (qr|elevator|sky), kind (hook|mechanism|proof|end), look (A|B).
 *  A = current brand refined (dark ink stage, line art, fixed contrast, title-as-hook + scale reveal, photo proof card).
 *  B = richer illustrated look: claude-drawing-skill FlatVector backdrops + assets/library SVGs (lit/shade faces, soft drop shadows). */
type Ep = "qr" | "elevator" | "sky"; type Kind = "hook" | "mechanism" | "proof" | "end"; type Look = "A" | "B";
const lib = (n: string) => staticFile(`library/${n}`);
const PIL: Record<Ep, Pillar> = { qr: PILLARS.tech, elevator: PILLARS.eng, sky: PILLARS.sci };
const META: Record<Ep, { ep: string; src: string; title: [string, string, string]; chapters: number }> = {
  qr: { ep: "001", src: "DENSO WAVE", title: ["THE CODE THAT", "REPAIRS", "ITSELF"], chapters: 5 },
  elevator: { ep: "002", src: "TK ELEVATOR", title: ["THE ELEVATOR THAT", "BARELY LIFTS", "YOU"], chapters: 5 },
  sky: { ep: "003", src: "MET OFFICE · NOAA", title: ["THE SUNSET MADE OF", "SOMEONE ELSE'S", "BLUE SKY"], chapters: 5 },
};
const CAPTION: Record<Ep, Record<Kind, [string, number]>> = {
  qr: { hook: ["This code repairs", 1], mechanism: ["extra bytes rebuild", 1], proof: ["survive damage", 0], end: ["its own spare parts", 3] },
  elevator: { hook: ["This elevator barely", 1], mechanism: ["fights the difference", 2], proof: ["hangs a counterweight", 2], end: ["a scale, not", 1] },
  sky: { hook: ["This sunset is", 1], mechanism: ["blue gets bounced", 1], proof: ["dozens of times more air", 3], end: ["someone else's blue", 2] },
};

const Caption: React.FC<{ text: string; hi: number }> = ({ text, hi }) => (
  <div style={{ position: "absolute", left: LAYOUT.safeLeft, width: LAYOUT.safeRight - LAYOUT.safeLeft, top: LAYOUT.captionTop, display: "flex", justifyContent: "center", flexWrap: "wrap" }}>
    <div style={{ textAlign: "center", fontFamily: SANS, fontWeight: 900, fontSize: 84, lineHeight: 1.12 }}>
      {text.split(" ").map((w, i) => <span key={i} style={{ color: i === hi ? C.amber : "white", WebkitTextStroke: "14px #000", paintOrder: "stroke fill", textShadow: "0 8px 24px rgba(0,0,0,0.6)", display: "inline-block", margin: "0 0.13em" }}>{w}</span>)}
    </div>
  </div>
);
const DeckStatic: React.FC<{ pillar: Pillar; idx: number; n: number; label: string; prog: number }> = ({ pillar, idx, n, label, prog }) => {
  const W = LAYOUT.safeRight - LAYOUT.safeLeft, x0 = LAYOUT.safeLeft, y = LAYOUT.deckTop;
  return (<>
    <div style={{ position: "absolute", left: x0, top: y, display: "flex", gap: 18, fontFamily: MONO, fontWeight: 700, fontSize: 30 }}>
      <span style={{ color: pillar.color }}>{String(idx).padStart(2, "0")}/{String(n).padStart(2, "0")}</span><span style={{ color: C.paper, letterSpacing: 2 }}>{label}</span>
    </div>
    <svg width={1080} height={120} style={{ position: "absolute", top: y + 50 }}>
      <rect x={x0} y={18} width={W} height={8} rx={4} fill={C.ink3} /><rect x={x0} y={18} width={W * prog} height={8} rx={4} fill={C.amber} />
      <g transform={`translate(${x0 + W * prog} 22)`}><circle r={24} fill={C.ink} /><circle r={14} fill={C.amber} /></g>
    </svg>
  </>);
};
/** Title-as-hook (The Why Side grammar): "THE X THAT Y", key words big, inside the stage top. */
const TitleHook: React.FC<{ t: [string, string, string]; look: Look; y?: number }> = ({ t, look, y = 300 }) => (
  <div style={{ position: "absolute", top: y, left: 60, width: 840, fontFamily: DISPLAY, fontWeight: 700, lineHeight: 0.98, letterSpacing: -1 }}>
    <div style={{ fontSize: 40, color: C.paper, letterSpacing: 2, opacity: 0.95, textShadow: "0 4px 16px rgba(0,0,0,0.6)" }}>{t[0]}</div>
    <div style={{ fontSize: 88, color: C.amber, textShadow: look === "B" ? "0 6px 0 #00000055" : "0 6px 24px rgba(0,0,0,0.5)" }}>{t[1]}</div>
    <div style={{ fontSize: 88, color: C.paper, textShadow: look === "B" ? "0 6px 0 #00000055" : "0 6px 24px rgba(0,0,0,0.5)" }}>{t[2]}</div>
  </div>
);
/** Scale-reveal guide: the bracket the camera starts in (tiny detail), drawn where the pull-out began. */
const ZoomBracket: React.FC<{ x: number; y: number; w: number; h: number; label: string }> = ({ x, y, w, h, label }) => {
  const k = 26, s = { stroke: C.amber, strokeWidth: 7, fill: "none", strokeLinecap: "round" as const };
  return (<g>
    <path d={`M${x},${y + k}V${y}H${x + k}M${x + w - k},${y}H${x + w}V${y + k}M${x + w},${y + h - k}V${y + h}H${x + w - k}M${x + k},${y + h}H${x}V${y + h - k}`} {...s} />
    {label && <g transform={`translate(${x + w / 2} ${y - 22})`}><rect x={-(label.length * 19 + 28) / 2} y={-26} width={label.length * 19 + 28} height={44} rx={22} fill={C.amber} />
      <text y={8} fill={C.ink} fontFamily={MONO} fontWeight={700} fontSize={30} textAnchor="middle">{label}</text></g>}
  </g>);
};
const Lbl: React.FC<{ x: number; y: number; t: string; c?: string; s?: number; a?: "start" | "middle" | "end" }> = ({ x, y, t, c = C.paper, s = 40, a = "middle" }) => (
  <text x={x} y={y} fill={c} fontFamily={DISPLAY} fontWeight={700} fontSize={s} textAnchor={a} style={{ paintOrder: "stroke", stroke: C.ink, strokeWidth: 6, strokeLinejoin: "round" }}>{t}</text>
);
/** Look B label: paper tag with ink text (contrast >= 12:1 on any illustration behind it). */
const Tag: React.FC<{ x: number; y: number; t: string; c?: string; s?: number; a?: "start" | "middle" | "end"; bg?: string }> = ({ x, y, t, c = C.ink, s = 36, a = "middle", bg = C.paper }) => {
  const w = t.length * s * 0.6 + 32, x0 = a === "start" ? x : a === "end" ? x - w : x - w / 2;
  return (<g><rect x={x0 + 4} y={y - s - 2} width={w} height={s + 22} rx={(s + 22) / 2} fill="#000" opacity={0.3} />
    <rect x={x0} y={y - s - 6} width={w} height={s + 22} rx={(s + 22) / 2} fill={bg} />
    <text x={x0 + w / 2} y={y + 2} fill={c} fontFamily={DISPLAY} fontWeight={700} fontSize={s} textAnchor="middle">{t}</text></g>);
};
const Pic: React.FC<{ n: string; x: number; y: number; w: number; rot?: number; o?: number }> = ({ n, x, y, w, rot = 0, o = 1 }) => (
  <Img src={lib(n)} style={{ position: "absolute", left: x, top: y, width: w, transform: `rotate(${rot}deg)`, opacity: o, filter: "drop-shadow(6px 10px 8px rgba(5,6,10,0.45))" }} />
);
const Backdrop: React.FC<{ n: string; dim?: number; y?: number; h?: number }> = ({ n, dim = 0.25, y = 0, h = 1920 }) => (
  <div style={{ position: "absolute", left: 0, top: y, width: 1080, height: h, overflow: "hidden" }}>
    <Img src={lib(n)} style={{ width: 1080, height: 1920, objectFit: "cover", position: "absolute", top: -y }} />
    <div style={{ position: "absolute", inset: 0, background: `linear-gradient(180deg, rgba(13,14,18,${dim + 0.35}) 0%, rgba(13,14,18,${dim}) 30%, rgba(13,14,18,${dim}) 60%, rgba(13,14,18,0.85) 66%, rgba(13,14,18,0.96) 100%)` }} />
  </div>
);

/** Real-photo proof card: brand frame, ~1-2 s on screen, slow Ken Burns (scale 1.0 -> 1.08), credit line >= 30 px. */
const ProofCard: React.FC<{ src: string; tag: string; credit: string; look: Look; aspect: number; focus?: [number, number, number, number]; focusLabel?: string; kb?: number }> =
  ({ src, tag, credit, look, aspect, focus, focusLabel, kb = 1.05 }) => {
    const W = look === "A" ? 800 : 720, H = Math.min(look === "A" ? 610 : 580, W / aspect), x = (1080 - W) / 2, y = look === "A" ? 400 : 420;
    return (
      <div style={{ position: "absolute", left: x, top: y, width: W, transform: look === "B" ? "rotate(-2.2deg)" : undefined }}>
        <div style={{ position: "relative", width: W, height: H, borderRadius: look === "A" ? 28 : 6, overflow: "hidden",
          border: look === "A" ? `6px solid ${C.amber}` : `22px solid ${C.paper}`, boxShadow: "0 24px 60px rgba(0,0,0,0.55)", background: C.ink2, boxSizing: "content-box" }}>
          <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${kb})`, transformOrigin: "60% 55%" }} />
          {focus && <svg width={W} height={H} style={{ position: "absolute", left: 0, top: 0 }}>
            <rect x={focus[0] * W} y={focus[1] * H} width={(focus[2] - focus[0]) * W} height={(focus[3] - focus[1]) * H} rx={14} fill="none" stroke={C.amber} strokeWidth={8} strokeDasharray="26 14" />
          </svg>}
          {look === "B" && <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at 50% 40%, transparent 60%, rgba(0,0,0,0.35))" }} />}
        </div>
        {look === "B" && <div style={{ position: "absolute", left: W / 2 - 90, top: -34, width: 180, height: 56, background: "rgba(243,239,230,0.78)", transform: "rotate(3deg)", borderRadius: 4 }} />}
        <div style={{ position: "absolute", left: 0, top: -84, display: "flex", gap: 16, alignItems: "center", whiteSpace: "nowrap" }}>
          <div style={{ background: C.amber, color: C.ink, fontFamily: DISPLAY, fontWeight: 700, fontSize: 40, padding: "8px 26px", borderRadius: 40 }}>REAL PHOTO</div>
          <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 40, color: C.paper, textShadow: "0 3px 10px #000" }}>{tag}</div>
        </div>
        {focusLabel && focus && <div style={{ position: "absolute", left: Math.min(focus[0] * W, W - focusLabel.length * 24 - 40), top: Math.max(8, focus[1] * H - 64), fontFamily: DISPLAY, fontWeight: 700, fontSize: 36, color: C.ink, background: C.amber, padding: "4px 18px", borderRadius: 30 }}>{focusLabel}</div>}
        <div style={{ position: "absolute", left: 0, top: H + (look === "A" ? 30 : 60), width: W, fontFamily: MONO, fontWeight: 500, fontSize: 30, color: C.paper, opacity: 0.95, lineHeight: 1.25 }}>{credit}</div>
      </div>
    );
  };

const EndBrand: React.FC<{ line: string; pillar: Pillar }> = ({ line, pillar }) => (
  <div style={{ position: "absolute", top: 920, left: 70, width: 940, padding: "26px 0", borderRadius: 34, background: "rgba(13,14,18,0.86)", display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
    <div style={{ display: "flex", alignItems: "center", gap: 18 }}><Gear size={74} color={C.amber} rot={20} />
      <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 64, color: C.paper, letterSpacing: -0.5 }}>THAT'S THE MECHANISM.</div></div>
    <div style={{ width: 560, height: 10, borderRadius: 6, background: `linear-gradient(90deg, ${C.amber}, ${pillar.color})` }} />
    <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 46, color: C.amber, textAlign: "center", width: 860, textShadow: "0 3px 12px #000" }}>{line}</div>
  </div>
);

/* ------------------------------------------------------------------ ELEVATOR */
const ElevatorArt: React.FC<{ kind: Kind; look: Look }> = ({ kind, look }) => {
  const P = PILLARS.eng;
  if (kind === "hook" && look === "A") {
    // scale reveal end state: a bright 12-storey shaft, tiny car, big counterweight; the camera started inside the bracket (one rider)
    return (<svg width={1080} height={1920} style={{ position: "absolute" }}><g transform="translate(54 96) scale(0.9)">
      <rect x={250} y={560} width={580} height={640} rx={24} fill="#E9E3D6" />
      <rect x={540} y={560} width={290} height={640} rx={0} fill="#D9D1C1" />
      {Array.from({ length: 11 }).map((_, i) => <line key={i} x1={250} x2={830} y1={600 + i * 56} y2={600 + i * 56} stroke="#C4BBA9" strokeWidth={3} />)}
      <circle cx={540} cy={600} r={70} fill={C.ink3} /><circle cx={540} cy={600} r={26} fill={C.amber} />
      <line x1={470} y1={600} x2={470} y2={980} stroke={C.ink} strokeWidth={8} /><line x1={610} y1={600} x2={610} y2={760} stroke={C.ink} strokeWidth={8} />
      <rect x={390} y={980} width={160} height={190} rx={14} fill={C.amber} /><rect x={405} y={995} width={130} height={160} rx={8} fill="#FFE2A6" />
      <circle cx={445} cy={1060} r={12} fill={C.ink} /><rect x={433} y={1074} width={24} height={44} rx={10} fill={C.ink} />
      <rect x={580} y={760} width={110} height={210} rx={12} fill={P.color} /><rect x={635} y={760} width={55} height={210} rx={12} fill="#4E9A5C" />
      <ZoomBracket x={420} y={1030} w={60} h={100} label="START" />
      <text x={635} y={1010} fill={C.ink} fontFamily={DISPLAY} fontWeight={700} fontSize={32} textAnchor="middle">COUNTER-</text>
      <text x={635} y={1046} fill={C.ink} fontFamily={DISPLAY} fontWeight={700} fontSize={32} textAnchor="middle">WEIGHT</text>
    </g></svg>);
  }
  if (kind === "hook" && look === "B") {
    return (<>
      <Backdrop n="city_dusk.jpg" dim={0.1} />
      <div style={{ position: "absolute", left: 300, top: 560, width: 480, height: 640, background: "#F3EFE6", borderRadius: 18, boxShadow: "0 20px 50px rgba(0,0,0,0.5)" }} />
      <div style={{ position: "absolute", left: 540, top: 560, width: 240, height: 640, background: "#E1D9C9", borderRadius: "0 18px 18px 0" }} />
      <Pic n="traction_sheave.svg" x={455} y={540} w={170} />
      <Pic n="elevator_car.svg" x={335} y={930} w={210} />
      <Pic n="office_crowd.svg" x={360} y={1030} w={160} />
      <Pic n="counterweight.svg" x={600} y={740} w={120} />
      <svg width={1080} height={1920} style={{ position: "absolute" }}><line x1={470} y1={625} x2={470} y2={940} stroke={C.ink} strokeWidth={7} /><line x1={610} y1={625} x2={610} y2={745} stroke={C.ink} strokeWidth={7} />
        <ZoomBracket x={380} y={1030} w={64} h={100} label="START" /></svg>
    </>);
  }
  if (kind === "mechanism" && look === "B") {
    return (<>
      <Backdrop n="city_dusk.jpg" dim={0.45} />
      <div style={{ position: "absolute", left: 110, top: 330, width: 860, height: 860, borderRadius: 40, background: "rgba(243,239,230,0.96)", boxShadow: "0 24px 60px rgba(0,0,0,0.5)" }} />
      <Pic n="traction_motor.svg" x={600} y={350} w={300} />
      <Pic n="traction_sheave.svg" x={430} y={380} w={220} />
      <svg width={1080} height={1920} style={{ position: "absolute" }}><line x1={445} y1={490} x2={445} y2={700} stroke={C.ink} strokeWidth={8} /><line x1={635} y1={490} x2={635} y2={640} stroke={C.ink} strokeWidth={8} /></svg>
      <Pic n="elevator_car.svg" x={300} y={690} w={290} />
      <Pic n="office_crowd.svg" x={330} y={820} w={230} />
      <Pic n="counterweight.svg" x={590} y={630} w={150} />
      <svg width={1080} height={1920} style={{ position: "absolute" }}>
        <Tag x={860} y={1000} t="= EMPTY CAR" s={34} a="end" bg={PILLARS.eng.color} /><Tag x={860} y={1066} t="+ 40-50% LOAD" s={34} a="end" bg={C.amber} />
        <rect x={160} y={1000} width={50} height={140} rx={8} fill={C.paper} stroke={C.ink} strokeWidth={4} /><rect x={225} y={1040} width={50} height={100} rx={8} fill={P.color} /><rect x={160} y={1000} width={50} height={40} rx={8} fill={C.amber} />
      </svg>
      <svg width={1080} height={1920} style={{ position: "absolute" }}><Pill x={540} y={1150} w={580} text="MOTOR = DIFFERENCE" color={C.amber} s={1} /></svg>
    </>);
  }
  if (kind === "proof") {
    return (<>
      {look === "B" && <Backdrop n="city_dusk.jpg" dim={0.5} />}
      <ProofCard look={look} src="photos/02-elevator--elevator-counterweight-washington-monument-high-gr.jpg" aspect={look === "A" ? 0.95 : 0.95} kb={1.06}
        tag="WASHINGTON MONUMENT" focus={[0.47, 0.5, 0.75, 0.96]} focusLabel="THE COUNTERWEIGHT"
        credit="PHOTO: JACK E. BOUCHER, HABS / LIBRARY OF CONGRESS · PUBLIC DOMAIN" />
      {look === "B" && <Pic n="counterweight.svg" x={860} y={1010} w={110} rot={8} />}
    </>);
  }
  if (kind === "end" && look === "B") {
    return (<>
      <Backdrop n="city_dusk.jpg" dim={0.5} />
      <div style={{ position: "absolute", left: 80, top: 360, width: 440, height: 520, borderRadius: 34, background: "#F3EFE6", boxShadow: `0 0 0 8px ${C.green}, 0 24px 60px rgba(0,0,0,0.5)` }} />
      <div style={{ position: "absolute", left: 560, top: 360, width: 440, height: 520, borderRadius: 34, background: "#2A3142", boxShadow: "0 24px 60px rgba(0,0,0,0.5)" }} />
      <Pic n="balance_scale.svg" x={110} y={520} w={380} />
      <Pic n="elevator_car.svg" x={130} y={430} w={120} rot={-4} /><Pic n="counterweight.svg" x={385} y={440} w={70} rot={-4} />
      <Pic n="tower_crane.svg" x={600} y={410} w={360} o={0.75} />
      <svg width={1080} height={1920} style={{ position: "absolute" }}>
        <line x1={600} y1={400} x2={960} y2={840} stroke={C.red} strokeWidth={18} strokeLinecap="round" />
        <Tag x={300} y={850} t="A SCALE" s={52} bg={C.green} /><Tag x={780} y={850} t="NOT A CRANE" s={46} bg={C.red} />
      </svg>
      <EndBrand line="AN ELEVATOR IS A SCALE" pillar={PILLARS.eng} />
    </>);
  }
  return null;
};

/* ------------------------------------------------------------------ QR */
const QRGeneric: React.FC<{ x: number; y: number; s: number; torn?: boolean; logo?: boolean }> = ({ x, y, s, torn, logo }) => (
  <div style={{ position: "absolute", left: x, top: y, width: s, height: s }}>
    <Img src={lib("qr_generic.svg")} style={{ width: s, height: s, clipPath: torn ? "polygon(0 0,100% 0,100% 58%,82% 66%,70% 100%,0 100%)" : undefined }} />
    {logo && <div style={{ position: "absolute", left: s * 0.39, top: s * 0.39, width: s * 0.22, height: s * 0.22, borderRadius: s * 0.04, background: C.ink, display: "flex", alignItems: "center", justifyContent: "center" }}><Gear size={s * 0.16} color={C.amber} rot={10} /></div>}
  </div>
);
const QRArt: React.FC<{ kind: Kind; look: Look }> = ({ kind, look }) => {
  if (kind === "hook" && look === "A") {
    return (<>
      <QRGeneric x={250} y={600} s={580} torn logo />
      <div style={{ position: "absolute", left: 760, top: 1000, width: 120, height: 150, background: C.paper, clipPath: "polygon(0 10%,100% 0,85% 100%,20% 80%)", transform: "rotate(18deg)" }} />
      <svg width={1080} height={1920} style={{ position: "absolute" }}><ZoomBracket x={318} y={668} w={48} h={48} label="START: 1 MODULE" />
        <Lbl x={540} y={1240 - 60} t="" /></svg>
      <svg width={1080} height={1920} style={{ position: "absolute" }}><Pill x={540} y={1150} w={520} text="STILL SCANS" color={C.green} s={1} icon={Check} /></svg>
    </>);
  }
  if (kind === "hook" && look === "B") {
    return (<>
      <Backdrop n="street_wall.jpg" dim={0.05} />
      <div style={{ position: "absolute", left: 140, top: 560, width: 520, height: 600, background: "#F3EFE6", borderRadius: 12, transform: "rotate(-3deg)", boxShadow: "0 20px 40px rgba(0,0,0,0.5)" }} />
      <QRGeneric x={190} y={620} s={420} torn logo />
      <Pic n="person_phone.svg" x={700} y={700} w={260} />
      <Pic n="smartphone.svg" x={640} y={760} w={150} rot={-12} />
      <svg width={1080} height={1920} style={{ position: "absolute" }}><ZoomBracket x={240} y={668} w={40} h={40} label="START" /></svg>
      <svg width={1080} height={1920} style={{ position: "absolute" }}><Pill x={540} y={1150} w={520} text="STILL SCANS" color={C.green} s={1} icon={Check} /></svg>
    </>);
  }
  if (kind === "mechanism" && look === "B") {
    const cells = Array.from({ length: 10 });
    return (<>
      <Backdrop n="street_wall.jpg" dim={0.35} />
      <div style={{ position: "absolute", left: 90, top: 330, width: 900, height: 860, borderRadius: 40, background: "rgba(243,239,230,0.96)" }} />
      {cells.map((_, i) => i === 6 ? null : <Pic key={i} n="byte_block.svg" x={130 + (i % 5) * 165} y={380 + Math.floor(i / 5) * 160} w={140} />)}
      <svg width={1080} height={1920} style={{ position: "absolute" }}>
        <rect x={130 + 165 + 10} y={540 + 10} width={120} height={120} rx={16} fill="none" stroke={C.red} strokeWidth={6} strokeDasharray="16 10" />
        <Tag x={540} y={745} t="DATA BYTES" s={36} bg={PILLARS.tech.color} />
        {cells.slice(0, 5).map((_, i) => <g key={i}><rect x={130 + i * 165 + 10} y={790} width={120} height={120} rx={16} fill={C.amber} /><text x={130 + i * 165 + 70} y={868} fill={C.ink} fontFamily={MONO} fontWeight={700} fontSize={48} textAnchor="middle">+</text></g>)}
        <Tag x={540} y={965} t="REPAIR BYTES = f(DATA)" s={36} bg={C.amber} />
        <path d="M370,780 C330,700 330,660 360,640" stroke={C.amber} strokeWidth={8} fill="none" strokeLinecap="round" markerEnd="" />
      </svg>
      <Pic n="magnifier.svg" x={360} y={520} w={150} />
      <Pic n="compact_disc.svg" x={760} y={960} w={180} />
      <svg width={1080} height={1920} style={{ position: "absolute" }}><Tag x={740} y={1060} t="SAME MATH AS CDs" s={32} a="end" bg={C.ink} c={C.paper} /><Pill x={540} y={1150} w={600} text="MISSING BYTES: REBUILT" color={C.amber} s={1} /></svg>
    </>);
  }
  if (kind === "proof") {
    return (<>
      {look === "B" && <Backdrop n="street_wall.jpg" dim={0.4} />}
      <ProofCard look={look} src="photos/01-qr-code--qr-code-damaged.jpg" aspect={1} kb={1.05} tag="TORN, STILL A CODE"
        focus={[0.6, 0.55, 0.98, 0.98]} focusLabel="MISSING CHUNK"
        credit="PHOTO: BOBMATH (WIKIMEDIA COMMONS) · CC0" />
    </>);
  }
  if (kind === "end" && look === "B") {
    return (<>
      <Backdrop n="street_wall.jpg" dim={0.4} />
      <QRGeneric x={270} y={360} s={540} logo />
      <Pic n="gear.svg" x={150} y={330} w={130} rot={-10} /><Pic n="byte_block.svg" x={830} y={420} w={110} rot={12} /><Pic n="byte_block.svg" x={800} y={760} w={90} rot={-8} />
      <svg width={1080} height={1920} style={{ position: "absolute" }}><Pill x={540} y={860} w={520} text="SPARE PARTS INSIDE" color={C.green} s={1} icon={Check} /></svg>
      <EndBrand line="A QR CODE CARRIES ITS OWN SPARE PARTS" pillar={PILLARS.tech} />
    </>);
  }
  return null;
};

/* ------------------------------------------------------------------ SKY */
const SkyArt: React.FC<{ kind: Kind; look: Look }> = ({ kind, look }) => {
  if (kind === "hook" && look === "A") {
    return (<svg width={1080} height={1920} style={{ position: "absolute" }}>
      <defs><radialGradient id="atm"><stop offset="0.82" stopColor="#6FB8FF" stopOpacity={0} /><stop offset="0.9" stopColor="#6FB8FF" stopOpacity={0.55} /><stop offset="1" stopColor="#6FB8FF" stopOpacity={0} /></radialGradient></defs>
      <g transform="translate(40 60) scale(0.92)"><circle cx={420} cy={860} r={330} fill="url(#atm)" />
      <circle cx={420} cy={860} r={280} fill="#2C6FB7" />
      <path d="M300,680 Q380,620 470,660 Q500,720 430,760 Q360,790 340,850 Q270,800 300,680Z" fill={PILLARS.eng.color} />
      <path d="M470,900 Q570,870 610,950 Q560,1060 480,1030 Q450,980 470,900Z" fill={PILLARS.eng.color} />
      <path d="M420,580 A280,280 0 0,0 420,1140 A160,280 0 0,1 420,580Z" fill={C.ink} opacity={0.6} /></g>
      <circle cx={920} cy={820} r={70} fill="#FFE7A8" /><circle cx={920} cy={820} r={115} fill="#FFB020" opacity={0.25} />
      {[770, 820, 870].map((y, i) => <line key={i} x1={840} y1={y} x2={760} y2={y + (i - 1) * 10} stroke="#FFE7A8" strokeWidth={8} strokeLinecap="round" />)}
      <circle cx={700} cy={760} r={10} fill={PILLARS.sci.color} />
      <ZoomBracket x={681} y={741} w={38} h={38} label="START: 1 MOLECULE" />
      <circle cx={690} cy={960} r={16} fill="#FF8A2E" /><circle cx={190} cy={920} r={16} fill="#6FB8FF" />
      <Lbl x={700} y={1020} t="SUNSET HERE" c="#FFB27A" s={34} a="start" /><Lbl x={120} y={1180} t="BLUE SKY HERE" c="#BFE0FF" s={34} a="start" />
    </svg>);
  }
  if (kind === "hook" && look === "B") {
    return (<>
      <div style={{ position: "absolute", left: 80, top: 560, width: 920, height: 300, borderRadius: 30, overflow: "hidden" }}><Img src={lib("sky_noon.jpg")} style={{ width: 920, height: 1636, objectFit: "cover", marginTop: -900 }} /></div>
      <div style={{ position: "absolute", left: 80, top: 880, width: 920, height: 300, borderRadius: 30, overflow: "hidden" }}><Img src={lib("sky_sunset.jpg")} style={{ width: 920, height: 1636, objectFit: "cover", marginTop: -760 }} /></div>
      <Pic n="earth_flat.svg" x={830} y={790} w={150} />
      <svg width={1080} height={1920} style={{ position: "absolute" }}>
        <Tag x={110} y={630} t="NOON" s={34} a="start" /><Tag x={110} y={950} t="SUNSET" s={34} a="start" />
        <ZoomBracket x={880} y={840} w={50} h={50} label="" />
      </svg>
    </>);
  }
  if (kind === "mechanism" && look === "B") {
    return (<>
      <Backdrop n="sky_noon.jpg" dim={0.15} />
      <Pic n="sun.svg" x={40} y={520} w={260} />
      <svg width={1080} height={1920} style={{ position: "absolute" }}>
        <rect x={250} y={640} width={290} height={22} rx={11} fill="#FFF4C8" />
        {[0, 1, 2, 3, 4, 5].map((i) => { const a = -0.9 + i * 0.36; return <line key={i} x1={600} y1={650} x2={600 + Math.cos(a) * 260} y2={650 + Math.sin(a) * 260} stroke="#2F7FD6" strokeWidth={10} strokeLinecap="round" />; })}
        <line x1={640} y1={650} x2={1000} y2={650} stroke={C.red} strokeWidth={10} strokeLinecap="round" />
        <Tag x={880} y={460} t="BLUE: SCATTERED" s={36} a="end" bg="#0F3E7A" c={C.paper} /><Tag x={880} y={740} t="RED: CARRIES ON" s={36} a="end" bg={C.red} />
      </svg>
      <Pic n="air_molecule.svg" x={530} y={590} w={130} />
      <Pic n="wave_blue_short.svg" x={140} y={860} w={400} /><Pic n="wave_red_long.svg" x={540} y={860} w={400} />
      <svg width={1080} height={1920} style={{ position: "absolute" }}><Tag x={340} y={1060} t="SHORT WAVE" s={32} bg="#0F3E7A" c={C.paper} /><Tag x={740} y={1060} t="LONG WAVE" s={32} bg={C.red} /></svg>
      <svg width={1080} height={1920} style={{ position: "absolute" }}><Pill x={540} y={1150} w={560} text="BLUE BOUNCES 4x MORE" color={C.paper} s={1} /></svg>
    </>);
  }
  if (kind === "proof") {
    return (<>
      {look === "B" && <Backdrop n="sky_sunset.jpg" dim={0.45} />}
      <ProofCard look={look} src="photos/03-sky--earth-observation.jpg" aspect={1920 / 1275} kb={1.04} tag="SEEN FROM THE ISS"
        focus={[0.02, 0.28, 0.98, 0.66]} focusLabel="BLUE ABOVE, RED BELOW"
        credit="PHOTO: NASA, ISS028-E-007274 (2011) · PUBLIC DOMAIN" />
    </>);
  }
  if (kind === "end" && look === "B") {
    return (<>
      <Backdrop n="sky_sunset.jpg" dim={0.2} />
      <Pic n="earth_flat.svg" x={330} y={380} w={420} />
      <svg width={1080} height={1920} style={{ position: "absolute" }}>
        <circle cx={400} cy={500} r={18} fill="#6FB8FF" /><circle cx={700} cy={640} r={18} fill="#FF8A2E" />
        <Tag x={380} y={470} t="BLUE SKY" s={34} a="end" bg="#6FB8FF" /><Tag x={720} y={720} t="YOUR SUNSET" s={34} a="start" bg="#FF8A2E" />
      </svg>
      <EndBrand line="YOUR SUNSET = SOMEONE ELSE'S BLUE SKY" pillar={PILLARS.sci} />
    </>);
  }
  return null;
};

const CHAPTER: Record<Ep, Record<Kind, [number, string, number]>> = {
  qr: { hook: [1, "A LOGO ON A QR", 0.02], mechanism: [2, "BYTES + REPAIR BYTES", 0.3], proof: [4, "THE LOGO BUDGET", 0.62], end: [5, "THE CORNERS", 0.98] },
  elevator: { hook: [1, "IT ALMOST BALANCES", 0.02], mechanism: [3, "ONLY THE DIFFERENCE", 0.45], proof: [2, "THE COUNTERWEIGHT", 0.25], end: [5, "WHY IT'S CHEAP", 0.98] },
  sky: { hook: [1, "SAME TRICK?", 0.02], mechanism: [2, "WHAT AIR DOES", 0.3], proof: [5, "SUNSET", 0.7], end: [5, "SUNSET", 0.98] },
};

export const StyleFrame: React.FC = () => {
  useCurrentFrame();
  const { ep = "elevator", kind = "hook", look = "A" } = getInputProps() as { ep?: Ep; kind?: Kind; look?: Look };
  const pillar = PIL[ep], m = META[ep], [ci, cl, prog] = CHAPTER[ep][kind], [cap, hi] = CAPTION[ep][kind];
  const Art = ep === "qr" ? QRArt : ep === "elevator" ? ElevatorArt : SkyArt;
  const isEndA = kind === "end" && look === "A";
  return (
    <AbsoluteFill style={{ background: C.ink }}>
      <Background pillar={pillar} />
      <Art kind={kind} look={look} />
      {kind === "hook" && <TitleHook t={m.title} look={look} />}
      {isEndA && null}
      <BrandChip pillar={pillar} ep={m.ep} source={m.src} />
      {kind !== "end" && <Caption text={cap} hi={hi} />}
      <DeckStatic pillar={pillar} idx={ci} n={m.chapters} label={cl} prog={prog} />
    </AbsoluteFill>
  );
};
