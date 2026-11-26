import React from "react";
import { Easing, interpolate, useVideoConfig } from "remotion";
import { Check, X } from "lucide-react";
import words from "../06-microwave-door.captions.json";
import {
  C, EpisodeShell, LOOP_FRAMES, MONO, PILLARS, Pill, Shot, Stage, TagLabel, TitleHook, Label,
  cue, ease, makeAt, pop, popOpacity, popScale, reveal, squash, useG,
} from "../brand";

/**
 * 005 Microwave — "You can see through the door; the microwaves stay in."
 * One persistent world: the microwave door. Front view (hook/final) -> magnified screen -> wave vs hole ->
 * cross-section of the screen (microwave bounces, light passes) -> legal leakage limit -> same door, two waves.
 */
const P = PILLARS.sci;
const MW = P.color;            // microwave = pillar violet
const LIGHT = "#FFE9A8";       // visible light = warm paper-yellow
const BODY = "#D9D4CA", BODY2 = "#B9B3A7", METAL = "#1B1E26";

const wave = (x0: number, y0: number, len: number, lambda: number, amp: number, phase: number) => {
  const pts: string[] = [];
  for (let x = 0; x <= Math.max(0, len); x += 4) pts.push(`${(x0 + x).toFixed(1)},${(y0 + Math.sin((x / lambda) * Math.PI * 2 - phase) * amp).toFixed(1)}`);
  return pts.length > 1 ? `M${pts.join("L")}` : "";
};
/** wave drawn right-to-left (reflected), starting at x0 and going left by len */
const waveL = (x0: number, y0: number, len: number, lambda: number, amp: number, phase: number) => {
  const pts: string[] = [];
  for (let x = 0; x <= Math.max(0, len); x += 4) pts.push(`${(x0 - x).toFixed(1)},${(y0 + Math.sin((x / lambda) * Math.PI * 2 - phase) * amp).toFixed(1)}`);
  return pts.length > 1 ? `M${pts.join("L")}` : "";
};
const Arrow: React.FC<{ x: number; y: number; dir: 1 | -1; color: string; o?: number; size?: number }> = ({ x, y, dir, color, o = 1, size = 26 }) => (
  <polygon points={`${x},${y} ${x - dir * size},${y - size * 0.7} ${x - dir * size},${y + size * 0.7}`} fill={color} opacity={o} />
);
const at0 = (fps: number) => makeAt(words, fps);

/* ---------------------------------------------------------------- front view: hook + final ---------------- */
const WX = 140, WY = 550, WW = 560, WH = 460; // door window
const Front: React.FC<{ final?: boolean }> = ({ final = false }) => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = at0(fps);
  const why = at("So why"), stay = at("stay in"), door = at("microwave door");
  const btn = final ? 0 : pop(f, door, fps, 12);
  // scale reveal: frame 0 is a bright close-up of the glowing window, pulling out to the whole oven by ~1 s
  const z = final ? 1 : interpolate(f, [2, 30], [1.5, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const cx = WX + WW / 2, cy = WY + WH / 2;
  const th = f / 22;
  const mugX = cx + 130 * Math.sin(th), mugS = 0.9 + 0.1 * Math.cos(th);
  const timer = Math.max(0, 30 - Math.floor(f / fps));
  // microwaves: rings from the centre, clipped to the window; they arrive on "So why", the frame flashes on "stay in"
  const ringsOn = final ? 1 : 0.35 + 0.65 * ease(f, why - 4, why + 8); // faint from frame 0 (no 1-3 s hold), full on "So why"
  const flash = final ? 0 : Math.max(0, 1 - Math.abs(f - stay - 4) / 10);
  return (
    <>
      <Stage>
        <defs>
          <radialGradient id="mwGlow" cx="50%" cy="55%" r="65%">
            <stop offset="0" stopColor="#FFE2A0" /><stop offset="0.55" stopColor="#F0A040" /><stop offset="1" stopColor="#6A3A12" />
          </radialGradient>
          <pattern id="mwMesh" width={24} height={24} patternUnits="userSpaceOnUse">
            <path d="M0 0H24V24H0Z M12 5a7 7 0 1 0 0.01 0Z" fill={METAL} fillRule="evenodd" opacity={0.62} />
          </pattern>
          <clipPath id="mwWin"><rect x={WX} y={WY} width={WW} height={WH} rx={18} /></clipPath>
        </defs>
        <g transform={`translate(${cx} ${cy}) scale(${z}) translate(${-cx} ${-cy})`}>
          {/* body */}
          <rect x={96} y={WY - 66} width={890} height={WH + 132} rx={40} fill={BODY2} />
          <rect x={90} y={WY - 74} width={890} height={WH + 132} rx={40} fill={BODY} />
          <rect x={740} y={WY - 40} width={210} height={WH + 70} rx={20} fill={BODY2} opacity={0.6} />
          {/* interior */}
          <g clipPath="url(#mwWin)">
            <rect x={WX} y={WY} width={WW} height={WH} fill="url(#mwGlow)" />
            <ellipse cx={cx} cy={WY + WH - 70} rx={230} ry={42} fill={C.paper} opacity={0.55} />
            <g transform={`translate(${mugX} ${WY + WH - 150}) scale(${mugS})`}>
              <rect x={-55} y={-60} width={110} height={130} rx={16} fill={C.paper} />
              <path d="M55 -30 q46 0 46 36 q0 36 -46 36" fill="none" stroke={C.paper} strokeWidth={14} />
              {[0, 1, 2].map((k) => (
                <path key={k} d={`M${-28 + k * 28} -80 q12 -22 0 -44 q-12 -22 0 -44`} fill="none" stroke="#FFF6E0" strokeWidth={7} strokeLinecap="round"
                  opacity={0.45 + 0.3 * Math.sin(f / 6 + k * 2)} transform={`translate(${4 * Math.sin(f / 8 + k)} 0)`} />
              ))}
            </g>
            {[0, 1, 2, 3].map((k) => {
              const r = ((f * 4 + k * 90) % 360) + 10;
              return <circle key={k} cx={cx} cy={cy - 20} r={r} fill="none" stroke={MW} strokeWidth={9} opacity={ringsOn * 0.75 * (1 - r / 380)} />;
            })}
            <rect x={WX} y={WY} width={WW} height={WH} fill="url(#mwMesh)" />
            <path d={`M${WX + 40} ${WY + 40} L${WX + 180} ${WY + 40} L${WX + 40} ${WY + 220} Z`} fill="white" opacity={0.12} />
          </g>
          <rect x={WX} y={WY} width={WW} height={WH} rx={18} fill="none" stroke={flash > 0 ? MW : "#2A2E3A"} strokeWidth={14 + 10 * flash} />
          {/* handle + panel */}
          <rect x={708} y={WY + 10} width={18} height={WH - 20} rx={9} fill={BODY2} />
          <rect x={762} y={WY + 4} width={168} height={84} rx={12} fill={C.ink} />
          <Label x={846} y={WY + 64} text={`0:${String(timer).padStart(2, "0")}`} size={46} color={C.amber} font={MONO} />
          {Array.from({ length: 9 }).map((_, i) => (
            <circle key={i} cx={790 + (i % 3) * 56} cy={WY + 150 + Math.floor(i / 3) * 60} r={20} fill={BODY2} />
          ))}
          <rect x={780} y={WY + 340} width={132} height={60} rx={30} fill={C.amber} opacity={0.9} />
          <rect x={780} y={WY + 340} width={132} height={60} rx={30} fill="none" stroke={C.amber} strokeWidth={6} opacity={btn * Math.max(0, 1 - (f - door) / 30)} transform={`translate(846 ${WY + 370}) scale(${1 + 0.5 * btn}) translate(-846 ${-(WY + 370)})`} />
        </g>
      </Stage>
      {!final && <TitleHook t={["YOU CAN SEE IN.", "THE WAVES", "CAN'T GET OUT."]} top={278} />}
    </>
  );
};

const FinalHud: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = at0(fps);
  const w = at("A wall for"), win = at("a window for you");
  return (
    <Stage>
      <Pill x={500} y={400} w={680} text="A WALL FOR MICROWAVES" color={MW} s={pop(f, w, fps)} icon={X} />
      <Pill x={500} y={1150} w={560} text="A WINDOW FOR YOU" color={C.green} s={pop(f, win, fps)} icon={Check} />
    </Stage>
  );
};

/* ---------------------------------------------------------------- magnified screen ---------------------- */
const Closer: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = at0(fps);
  const glass = at("Behind the glass"), metal = at("metal screen"), holes = at("tiny holes");
  const slide = ease(f, glass + 2, glass + 22);
  const X0 = 110, Y0 = 390, W = 860, H = 700, S = 96, R = 28;
  const cols = Math.floor(W / S), rows = Math.floor(H / S);
  return (
    <Stage>
      <defs>
        <radialGradient id="clGlow" cx="45%" cy="55%" r="70%"><stop offset="0" stopColor="#FFE2A0" /><stop offset="1" stopColor="#B4621E" /></radialGradient>
        <clipPath id="clClip"><rect x={X0} y={Y0} width={W} height={H} rx={30} /></clipPath>
        <mask id="clHoles">
          <rect x={X0} y={Y0} width={W} height={H} fill="white" />
          {Array.from({ length: cols * rows }).map((_, i) => {
            const c = i % cols, r = Math.floor(i / cols);
            return <circle key={i} cx={X0 + S / 2 + c * S + (W - cols * S) / 2} cy={Y0 + S / 2 + r * S + (H - rows * S) / 2} r={R} fill="black" />;
          })}
        </mask>
      </defs>
      <g clipPath="url(#clClip)">
        <rect x={X0} y={Y0} width={W} height={H} fill="url(#clGlow)" />
        <ellipse cx={440 + 40 * Math.sin(f / 20)} cy={820} rx={170} ry={210} fill={C.paper} opacity={0.35} />
        <rect x={X0} y={Y0} width={W} height={H} fill={METAL} mask="url(#clHoles)" />
        {/* amber ring pulse around every hole on "tiny holes", staggered from the centre out */}
        {Array.from({ length: cols * rows }).map((_, i) => {
          const c = i % cols, r = Math.floor(i / cols);
          const hx = X0 + S / 2 + c * S + (W - cols * S) / 2, hy = Y0 + S / 2 + r * S + (H - rows * S) / 2;
          const d = Math.hypot(c - cols / 2, r - rows / 2);
          const p = pop(f, holes + d * 2.2, fps, 12);
          return <circle key={i} cx={hx} cy={hy} r={R + 4} fill="none" stroke={C.amber} strokeWidth={6} opacity={popOpacity(p) * (1 - ease(f, holes + 40, holes + 60, 0, 0.6))} transform={`translate(${hx} ${hy}) scale(${popScale(p)}) translate(${-hx} ${-hy})`} />;
        })}
        {/* glass sheet slides off */}
        <g transform={`translate(${slide * 980} ${-slide * 60}) rotate(${slide * 8} ${X0 + W / 2} ${Y0 + H / 2})`} opacity={1 - slide * 0.3}>
          <rect x={X0} y={Y0} width={W} height={H} fill="#A9DCFF" opacity={0.34} />
          <path d={`M${X0 + 60} ${Y0} L${X0 + 260} ${Y0} L${X0 + 20} ${Y0 + H} L${X0 - 180} ${Y0 + H} Z`} fill="white" opacity={0.16} />
          <TagLabel x={X0 + W / 2} y={Y0 + H / 2 + 14} text="GLASS" size={48} />
        </g>
      </g>
      <rect x={X0} y={Y0} width={W} height={H} rx={30} fill="none" stroke="#2A2E3A" strokeWidth={10} />
      <TagLabel x={480} y={Y0 - 26} text="METAL SCREEN" size={44} color={C.amber} o={ease(f, metal, metal + 8)} />
    </Stage>
  );
};

/* ---------------------------------------------------------------- the wave ------------------------------ */
const WaveLen: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = at0(fps);
  const runs = at("The oven runs"), ghz = at("GHz"), each = at("Each wave"), twelve = at("twelve");
  const v = ease(f, runs + 20, ghz, 0, 2.45);
  const gp = pop(f, ghz, fps, 11);
  const LAM = 300, Y = 860;
  // the wave is on stage from the first frame of the shot (no empty half); "Each wave" brings the bracket, not the wave
  const len = ease(f, runs, runs + 40, 0, 900);
  const amp = 40 + 50 * ease(f, each, each + 14);
  const br = ease(f, twelve, twelve + 12);
  const hole = pop(f, twelve + 10, fps); // visible ~1.5 s before the whip (critic it3: "flashes < 0.5 s")
  return (
    <Stage>
      <Label x={540} y={390} text="MICROWAVE OVEN FREQUENCY" size={36} color={C.dim} />
      <g transform={`translate(540 560) scale(${1 + 0.08 * gp * Math.max(0, 1 - (f - ghz) / 12)})`}>
        <Label x={0} y={0} text={`${v.toFixed(2)} GHz`} size={120} color={C.amber} font={MONO} />
      </g>
      <path d={wave(90, Y, len, LAM, amp, f / 4)} stroke={MW} strokeWidth={14} fill="none" strokeLinecap="round" />
      <g opacity={br}>
        <line x1={240} y1={Y - 150} x2={240 + LAM * br} y2={Y - 150} stroke={C.amber} strokeWidth={6} />
        <line x1={240} y1={Y - 172} x2={240} y2={Y - 128} stroke={C.amber} strokeWidth={6} />
        <line x1={240 + LAM} y1={Y - 172} x2={240 + LAM} y2={Y - 128} stroke={C.amber} strokeWidth={6} opacity={br > 0.95 ? 1 : 0} />
        <Label x={240 + LAM / 2} y={Y - 180} text="≈ 12 cm" size={56} color={C.amber} font={MONO} />
      </g>
      <g opacity={popOpacity(hole)} transform={`translate(720 1060) scale(${popScale(hole)})`}>
        <rect x={-70} y={-70} width={140} height={140} rx={14} fill={METAL} stroke="#3A3F4E" strokeWidth={4} />
        <circle r={7} fill="#FFD27A" />
        <circle r={22} fill="none" stroke={C.amber} strokeWidth={4} strokeDasharray="6 6" />
      </g>
      <Label x={560} y={1080} text="ONE HOLE" size={40} anchor="end" o={popOpacity(hole)} />
    </Stage>
  );
};

/* ---------------------------------------------------------------- cross-section of the screen ----------- */
const WALL = 600, TOP = 400, BOT = 1100, PITCH = 54, BAR = 34;
const gapY = (k: number) => TOP + k * PITCH + BAR + (PITCH - BAR) / 2;
const Side: React.FC<{ mode: "story" | "both" }> = ({ mode }) => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = at0(fps);
  const both = mode === "both";
  const s = both ? at("Same door") - 30 : at("To a wave"), solid = at("solid metal"), bounce = at("bounces off"), food = at("your food");
  const li = both ? s - 60 : at("Light is different"), far = at("far smaller"), slip = at("slip right through");
  const wallSees = at("sees a wall"), lightSees = at("Light sees");
  const hitAt = s + 28;
  const head = ease(f, s, hitAt, 90, WALL);
  const hit = Math.max(0, 1 - Math.abs(f - hitAt - 3) / 12);
  const ref = both ? 1 : ease(f, bounce, bounce + 24);
  const mwDim = both ? 1 : 1 - 0.65 * ease(f, li, li + 12);
  const lightLen = both ? 1 : ease(f, li + 8, li + 50);
  const foodGlow = both ? 0.5 : pop(f, food, fps);
  const [sx, sy] = squash(f, food);
  const eye = both ? 1 : pop(f, slip, fps);
  const wallTint = both ? ease(f, wallSees, wallSees + 8) : 0;
  return (
    <Stage>
      <defs>
        <linearGradient id="sdIn" x1="0" x2="1"><stop offset="0" stopColor="#7A4416" /><stop offset="1" stopColor="#E89A3C" /></linearGradient>
        <clipPath id="sdL"><rect x={60} y={TOP} width={WALL - 60} height={BOT - TOP} /></clipPath>
      </defs>
      <rect x={60} y={TOP} width={WALL - 60} height={BOT - TOP} rx={24} fill="url(#sdIn)" opacity={0.55} />
      <TagLabel x={100} y={TOP + 40} text="INSIDE" size={34} anchor="start" color={C.paper} />
      <Label x={WALL + 40} y={TOP + 60} text="OUTSIDE" size={36} anchor="start" color={C.dim} />
      {/* the food (left) */}
      <g transform={`translate(190 900) scale(${sx} ${sy})`}>
        <circle r={90 * (0.6 + 0.6 * foodGlow)} fill={C.amber} opacity={0.35 * foodGlow} />
        <rect x={-50} y={-55} width={100} height={115} rx={14} fill={C.paper} />
        {[0, 1].map((k) => <path key={k} d={`M${-14 + k * 28} -70 q10 -18 0 -36 q-10 -18 0 -36`} stroke="#FFF6E0" strokeWidth={6} fill="none" strokeLinecap="round" opacity={0.3 + 0.5 * foodGlow * (0.6 + 0.4 * Math.sin(f / 5 + k))} />)}
      </g>
      {/* microwave: incident, then reflected */}
      <g clipPath="url(#sdL)" opacity={mwDim}>
        <path d={wave(90, 700, head - 90, 300, 80, f / 4)} stroke={MW} strokeWidth={14} fill="none" strokeLinecap="round" />
        {f >= hitAt && <path d={waveL(WALL, 850, (WALL - 230) * ref, 300, 60, f / 4)} stroke={MW} strokeWidth={10} fill="none" strokeLinecap="round" strokeDasharray="28 14" opacity={0.85} />}
      </g>
      {head > 160 && head < WALL - 4 && <Arrow x={head + 14} y={700} dir={1} color={MW} o={mwDim} />}
      {f >= hitAt && ref > 0.1 && <Arrow x={WALL - (WALL - 230) * ref - 12} y={850} dir={-1} color={MW} o={mwDim * 0.9} />}
      <TagLabel x={100} y={TOP + 140} text="MICROWAVE · ≈ 12 cm" size={34} anchor="start" color="#C9BFFF" o={mwDim * ease(f, s + 4, s + 12) * (both ? 1 - ease(f, wallSees - 6, wallSees) : 1)} />
      {/* light: short waves through the gaps to the eye */}
      {[5, 7, 9].map((k, i) => {
        const y = gapY(k), x0 = 250, x1 = 860, L = (x1 - x0) * Math.min(1, Math.max(0, lightLen * 1.15 - i * 0.07));
        return <path key={k} d={wave(x0, y, L, 26, 4, f / 1.5 + i)} stroke={LIGHT} strokeWidth={5} fill="none" strokeLinecap="round" />;
      })}
      <TagLabel x={100} y={1040} text="LIGHT · < 1 µm" size={34} anchor="start" color={LIGHT} o={both ? 1 : ease(f, far, far + 8)} />
      {/* the screen in cross-section: bars with gaps (holes) */}
      {Array.from({ length: Math.floor((BOT - TOP) / PITCH) + 1 }).map((_, k) => (
        <rect key={k} x={WALL - 12} y={TOP + k * PITCH} width={24} height={BAR} rx={5} fill={wallTint > 0 ? MW : "#9AA0AE"} opacity={1} stroke={C.ink} strokeWidth={2} />
      ))}
      <rect x={WALL - 26} y={TOP - 10} width={52} height={BOT - TOP + 20} rx={10} fill={MW} opacity={0.5 * hit + 0.35 * wallTint} />
      {/* the eye (right) */}
      <g transform={`translate(870 ${gapY(7)})`}>
        <path d="M-60 0 Q0 -46 60 0 Q0 46 -60 0Z" fill={C.paper} />
        <circle r={22 + 6 * eye} fill="#3A6EA5" /><circle r={10 + 3 * eye} fill={C.ink} />
        <circle r={60} fill={LIGHT} opacity={0.25 * eye} />
      </g>
      <TagLabel x={100} y={TOP + 140} text="MICROWAVE SEES A WALL" size={34} color="#C9BFFF" anchor="start" o={both ? ease(f, wallSees, wallSees + 8) : 0} />
      <TagLabel x={760} y={560} text="SEES A WINDOW" size={38} color={C.green} anchor="middle" o={both ? ease(f, lightSees, lightSees + 8) : 0} />
      {!both && <Label x={WALL} y={TOP - 24} text="THE SCREEN, SIDE-ON" size={34} color={C.dim} o={ease(f, solid - 40, solid - 30)} />}
    </Stage>
  );
};

const SideHud: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = at0(fps);
  const solid = at("solid metal"), li = at("Light is different"), slip = at("slip right through");
  return (
    <Stage>
      {f < li && <Pill x={500} y={1160} w={600} text="SOLID METAL TO IT" color={C.red} s={pop(f, solid, fps)} icon={X} />}
      {f >= slip - 2 && <Pill x={500} y={1160} w={620} text="LIGHT SLIPS THROUGH" color={C.green} s={pop(f, slip, fps)} icon={Check} />}
    </Stage>
  );
};

/* ---------------------------------------------------------------- the legal limit ----------------------- */
const Limit: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = at0(fps);
  const esc = at("What little escapes"), five = at("five milliwatts"), two = at("two inches");
  const np = pop(f, five, fps, 11);
  const rule = ease(f, two, two + 16);
  const FX = 300; // oven front (side view)
  return (
    <Stage>
      <rect x={76} y={566} width={FX - 70} height={420} rx={26} fill={BODY2} />
      <rect x={70} y={560} width={FX - 70} height={420} rx={26} fill={BODY} />
      {[0, 1, 2, 3, 4].map((k) => <rect key={k} x={100} y={600 + k * 22} width={90} height={8} rx={4} fill={BODY2} />)}
      <rect x={95} y={980} width={50} height={22} rx={6} fill={BODY2} /><rect x={FX - 85} y={980} width={50} height={22} rx={6} fill={BODY2} />
      <rect x={FX - 60} y={575} width={10} height={390} fill={BODY2} />
      <rect x={FX - 18} y={590} width={18} height={360} fill={METAL} />
      <rect x={FX} y={700} width={26} height={140} rx={10} fill={BODY2} />
      <Label x={185} y={530} text="OVEN, SIDE-ON" size={32} color={C.dim} />
      {[0, 1, 2, 3].map((k) => {
        const r = ((f - esc) * 3 + k * 45) % 180;
        return <path key={k} d={`M${FX} ${770 - r * 0.9} A ${r} ${r * 0.9} 0 0 1 ${FX} ${770 + r * 0.9}`} fill="none" stroke={MW} strokeWidth={5} opacity={f >= esc ? 0.55 * (1 - r / 180) : 0} />;
      })}
      <Label x={610} y={500} text="MAXIMUM LEAKAGE" size={40} color={C.paper} o={ease(f, esc + 6, esc + 14)} />
      <g transform={`translate(610 650) scale(${popScale(np)})`} opacity={popOpacity(np)}>
        <Label x={0} y={0} text="5 mW/cm²" size={104} color={C.amber} />{/* proportional font: the mono ² sat 12 px off its word and A13 read it as a separate box */}
      </g>
      <Label x={610} y={760} text="21 CFR 1030.10 · US FDA" size={32} color={C.paper} font={MONO} o={ease(f, five + 12, five + 20)} />
      {/* 2 in / 5 cm ruler from the oven front to the probe */}
      <g opacity={ease(f, two - 4, two + 4)}>
        <line x1={FX} y1={1010} x2={FX + 240 * rule} y2={1010} stroke={C.amber} strokeWidth={6} />
        {[0, 1, 2, 3, 4, 5].map((k) => <line key={k} x1={FX + k * 48} y1={996} x2={FX + k * 48} y2={1024} stroke={C.amber} strokeWidth={4} opacity={rule * 240 >= k * 48 ? 1 : 0} />)}
        <Label x={FX + 120} y={1080} text="2 in · 5 cm" size={40} color={C.amber} font={MONO} />
        <g transform={`translate(${FX + 240} 880)`} opacity={rule}>
          <rect x={-14} y={0} width={28} height={120} rx={8} fill={C.paper} />
          <circle r={26} fill={C.paper} /><circle r={12 + 3 * Math.sin(f / 4)} fill={MW} />
        </g>
      </g>
    </Stage>
  );
};
const LimitHud: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const cap = at0(fps)("capped by");
  return <Stage><Pill x={500} y={1160} w={560} text="US FEDERAL LIMIT" color={C.amber} s={pop(f, cap, fps)} /></Stage>;
};

/* ---------------------------------------------------------------- composition ---------------------------- */
export const MicrowaveVideo: React.FC = () => {
  const { fps, durationInFrames: D } = useVideoConfig();
  const at = makeAt(words, fps);
  const closer = at("Look closer"), runs = at("The oven runs"), twa = at("To a wave"), li = at("Light is different"),
    esc = at("What little escapes"), same = at("Same door"), card = at("That's the mechanism"), fin = at("A wall for"), loop = D - LOOP_FRAMES;
  const cues = [
    cue(4, "swish", 0.7), cue(at("microwave door"), "click", 0.8), cue(at("So why"), "tick", 0.75),
    cue(at("Behind the glass") + 2, "swish", 0.75), cue(at("metal screen"), "clank", 0.8), cue(at("tiny holes"), "pop3", 0.85),
    cue(runs + 20, "count", 0.75), cue(at("GHz"), "pop", 0.9), cue(at("Each wave"), "swish", 0.7), cue(at("twelve") + 10, "pop", 0.8),
    cue(twa + 28, "thud", 0.85), cue(at("solid metal"), "error", 0.75), cue(at("your food"), "pop", 0.85),
    cue(li + 8, "glint", 0.7), cue(at("far smaller"), "tick", 0.75), cue(at("slip right through"), "confirm", 0.85),
    cue(at("capped by"), "pop", 0.85), ...reveal(at("five milliwatts"), 0.8), cue(at("two inches"), "tick", 0.8), cue(at("two inches") + 16, "detent", 0.8),
    cue(at("sees a wall"), "thud", 0.8), cue(at("Light sees"), "confirm", 0.8),
    cue(fin, "pop", 0.85), cue(at("a window for you"), "confirm", 0.85),
  ];
  return (
    <EpisodeShell audio="06-microwave-door.wav" words={words} pillar={P} ep="006" source="FDA · 21 CFR 1030.10"
      cardAt={card} cardUntil={fin} cues={cues} hook={<Front />}
      chapters={[{ at: 0, label: "SEE IN, NOT OUT" }, { at: closer, label: "THE SCREEN" }, { at: runs, label: "THE WAVE" }, { at: twa, label: "BLOCKED" },
        { at: li, label: "LIGHT" }, { at: esc, label: "THE LIMIT" }, { at: same, label: "SAME DOOR" }]}>
      <Shot from={0} to={closer} inT="none" outT="push" cam={[{ at: 30, kind: "push", s: 1.06, y: 10, dur: 50 }, { at: at("stay in"), kind: "punch", s: 1.12, x: 60, y: 16 }]}><Front /></Shot>
      <Shot from={closer} to={runs} inT="push" outT="cut" cam={[{ at: at("Behind the glass"), kind: "push", s: 1.06 }, { at: at("tiny holes"), kind: "glide", s: 1.1, x: -20, dur: 24 }]}><Closer /></Shot>
      <Shot from={runs} to={twa} inT="cut" outT="whip" cam={[{ at: at("Each wave"), kind: "glide", s: 1.04, y: -30, dur: 24 }, { at: at("twelve"), kind: "punch", s: 1.12, x: 30, y: 20 }]}><WaveLen /></Shot>
      <Shot from={twa} to={esc} inT="whip" outT="whipUp" hud={<SideHud />} cam={[
        { at: twa, kind: "glide", s: 1.06, x: 40, dur: 20 },
        { at: at("solid metal"), kind: "push", s: 1.14, x: 0 },
        { at: at("bounces off"), kind: "punch", s: 1.2, x: 60 },
        { at: li, kind: "pull", s: 1.0, x: 0 },
        { at: at("slip right through"), kind: "glide", s: 1.06, x: -40, dur: 24 },
      ]}><Side mode="story" /></Shot>
      <Shot from={esc} to={same} inT="whipUp" outT="cut" hud={<LimitHud />} cam={[{ at: at("five milliwatts"), kind: "push", s: 1.08 }, { at: at("two inches"), kind: "glide", s: 1.1, x: 40, y: -40, dur: 24 }]}><Limit /></Shot>
      <Shot from={same} to={card} inT="cut" outT="push" cam={[{ at: same, kind: "pull", s: 1.0 }, { at: at("Light sees"), kind: "glide", s: 1.05, x: -30, dur: 22 }]}><Side mode="both" /></Shot>
      <Shot from={fin} to={loop} inT="push" outT="whip" hud={<FinalHud />}><Front final /></Shot>
    </EpisodeShell>
  );
};
