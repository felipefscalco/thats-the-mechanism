import React from "react";
import { Easing, interpolate, useVideoConfig } from "remotion";
import words from "../02-elevator.captions.json";
import { Check, X, Scale } from "lucide-react";
import { C, DISPLAY, EpisodeShell, Enter, Label, Lane, LOOP_FRAMES, MONO, PILLARS, TagLabel, ProofCard, Shot, Stage, TitleHook, cue, ease, makeAt, pop, popOpacity, popScale, reveal, useG } from "../brand";

const P = PILLARS.eng;
const SX = 490, SY = 585, SR = 92;
const DEF_X = 635, DEF_Y = SY + 74, DEF_R = 42;
const CAR_X = SX - SR, CW_X = DEF_X + DEF_R;
const CAR_W = 220, CAR_H = 225, CW_W = 118, CW_H = 205, SUM = 1480;

/** Smoothly eased piecewise trajectory (no jagged linear velocity corners). */
const smoothKeyed = (f: number, pts: [number, number][], overshoot = false): number => {
  if (f <= pts[0][0]) return pts[0][1];
  for (let i = 1; i < pts.length; i++) {
    const [t0, v0] = pts[i - 1], [t1, v1] = pts[i];
    if (f <= t1) {
      return interpolate(f, [t0, t1], [v0, v1], {
        extrapolateLeft: "clamp", extrapolateRight: "clamp",
        easing: overshoot ? Easing.out(Easing.back(1.25)) : Easing.inOut(Easing.cubic),
      });
    }
  }
  return pts[pts.length - 1][1];
};

const Extrude: React.FC<{ w: number; h: number; d?: number; top: string; side: string }> = ({ w, h, d = 20, top, side }) => (
  <>
    <polygon points={`${w},0 ${w + d},${-d * 0.6} ${w + d},${h - d * 0.6} ${w},${h}`} fill={side} />
    <polygon points={`0,0 ${d},${-d * 0.6} ${w + d},${-d * 0.6} ${w},0`} fill={top} />
  </>
);

const Person: React.FC<{ x: number; y: number; c: string; s?: number }> = ({ x, y, c, s = 1 }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    <circle cy={-44} r={14} fill={c} />
    <rect x={-16} y={-27} width={32} height={54} rx={13} fill={c} />
  </g>
);

const GuideShoe: React.FC<{ x: number; y: number }> = ({ x, y }) => (
  <g transform={`translate(${x} ${y})`}>
    <rect x={-10} y={-12} width={20} height={24} rx={4} fill="#5E6678" stroke={C.ink} strokeWidth={3} />
    <circle r={4} fill={C.amber} />
  </g>
);

const SpringBuffer: React.FC<{ x: number; y: number; compress?: number }> = ({ x, y, compress = 0 }) => {
  const h = 42 - compress * 14;
  return (
    <g transform={`translate(${x} ${y})`}>
      <rect x={-22} y={-h - 8} width={44} height={8} rx={3} fill={C.amber} />
      {[0, 1, 2, 3].map((i) => <line key={i} x1={-16} x2={16} y1={-h + (i * h) / 4} y2={-h + ((i + 0.5) * h) / 4} stroke="#8B91A1" strokeWidth={5} strokeLinecap="round" />)}
      <rect x={-24} y={-4} width={48} height={8} rx={3} fill="#4A5060" />
    </g>
  );
};

/** Persistent mechanical traction rig. Depends only on useG() (also frozen at f=0 by LoopBack). */
const Rig: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s2 = at("On the other side"), s3 = at("So the motor"), s4 = at("Here's the strange"), s5 = at("That's why a"), stamp = at("That's the mechanism");
  const full = at("car is full"), empty = at("nearly empty"), rel = at("Release"), rise = at("It would rise");

  // Scale reveal: f=0 zoomed 2.25x on the bright elevator car + rider, pulling out smoothly to show the full shaft & counterweight
  const Z0 = 2.2;
  const zoom = interpolate(f, [3, 38], [Z0, 1.0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const zFocusX = CAR_X, zFocusY = 951;
  const zk = (zoom - 1) / (Z0 - 1);

  // Car vertical trajectory. r6 pass 2: the nearly-empty car is HELD (strain jitter, no descent) while
  // "MOTOR HOLDS IT BACK" is on screen; it parks at the bottom only after that caption, then the release rises (longer).
  const fdF = at("fights the difference");
  const wf = at("wouldn't fall"), holdsF = at("holds it back");
  const riseEnd = Math.min(rise + 34, s5 - 2);
  let carTop = smoothKeyed(f, [[0, 835], [75, 715], [at("plus about"), 715], [s3, 740], [full - 8, 705], [full + 8, 720], [full + 48, 675], [empty, 675], [rel - 30, 845], [rel - 6, 845], [rel + 2, 855], [wf, 830], [rise - 12, 826], [riseEnd, 625], [s5, 625], [s5 + 24, 750]], f >= rise - 12 && f <= riseEnd + 2);
  // continuous secondary motion: slow bob while loading, strain jitter while held, tension shudder at brake release
  const bobEnv = interpolate(f, [0, 40, 75, s3 - 10, s3, empty - 16, empty - 6], [0, 8, 18, 18, 8, 8, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const strainEnv = interpolate(f, [holdsF - 6, holdsF, s4 + 10, s4 + 20], [0, 2.4, 2.4, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const shudderEnv = interpolate(f, [rel, rel + 2, rel + 10, rel + 16], [0, 5, 5, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // "wouldn't fall": small sag-and-recover (+-8 px)
  carTop += 8 * Math.sin(Math.min(1, Math.max(0, (f - wf) / 22)) * Math.PI) * Math.exp(-Math.max(0, f - wf) / 30);
  carTop += bobEnv * Math.sin((f - 75) / 8) + strainEnv * Math.sin(f * 1.9) + shudderEnv * Math.sin(f * 2.7);
  if (f >= s5 + 24 && f < stamp) carTop = 740 + Math.sin((f - s5 - 24) / 14) * 115;
  const cwTop = SUM - carTop; // strictly coupled opposite motion

  const strainQ = f >= holdsF && f < holdsF + 24 ? 0.07 * Math.exp(-(f - holdsF) / 7) * Math.cos((f - holdsF) * 0.9) : 0;
  const sheaveDeg = -(carTop - 815) * (180 / Math.PI / SR);
  const defDeg = (carTop - 815) * (180 / Math.PI / DEF_R);
  const motorDeg = (carTop - 815) * 4.2;

  const people = f < full ? 2 : f < empty ? Math.min(7, 2 + Math.floor((f - full) / 4)) : f < s4 + 8 ? 7 : f < s5 ? 0 : Math.min(6, Math.floor((f - s5) / 4));
  // riders pop in with overshoot / shrink out instead of snapping
  // riders leave one at a time (~0.4 s apart), last-in first-out
  const exitAt = (i: number) => empty + 20 + 12 * (6 - i);
  const personSc = (i: number): number => {
    if (f < full) return 1;
    if (f < empty) return i < 2 ? 1 : popScale(pop(f, full + (i - 2) * 4, fps)) / 1;
    if (f < s4 + 8) return i === 0 ? (f < s4 ? 1 : 1 - ease(f, s4, s4 + 8)) : 1 - ease(f, exitAt(i), exitAt(i) + 8);
    return popScale(pop(f, s5 + 4 * (i + 1) - 4, fps));
  };
  const doorOpen = f >= full - 6 && f < full + 18 ? ease(f, full - 6, full + 2) * (1 - ease(f, full + 10, full + 18)) : 0;
  const brakeOpen = ease(f, rel + 2, rel + 12);
  const showBrake = f >= rel - 30 && f < s5;
  const cwSplit = f >= s2 && f < s3 ? ease(f, at("It's built"), at("It's built") + 10) : 0;
  const bars = f >= s3 && f < s4 ? ease(f, s3, s3 + 10) : 0;
  const carLoad = f < full ? 3650 : f < empty + 20 ? 3650 + 3150 * ease(f, full, full + 20) : interpolate(f, [empty + 20, empty + 92], [6800, 3475], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const motorAt = at("motor never"), modestAt = at("modest motor");
  const motorP = ease(f, motorAt, motorAt + 14);
  const motorRe = f >= modestAt ? 1 + 0.22 * Math.sin(Math.min(1, (f - modestAt) / 14) * Math.PI) : 1;
  const flip1 = full + 8, flip2 = empty + 62;
  const motorOn = f >= s5 && f < stamp;
  const cwLit = f >= at("almost balances");
  const shaftLeft = CAR_X - CAR_W / 2 - 42, shaftRight = CW_X + CW_W / 2 + 42, shaftW = shaftRight - shaftLeft;
  const pitY = 1130;
  const titleO = 1 - ease(f, s2 - 10, s2);
  // title clearance: once zoomed out the whole rig sits 40 px lower so the sheave/motor clear the title by >= 24 px
  const offY = 40 * (1 - zk) * (1 - ease(f, s2 - 10, s2));

  return (
    <>
      <Stage>
        <defs>
          <radialGradient id="spot" cx="50%" cy="42%" r="55%">
            <stop offset="0" stopColor={P.color} stopOpacity={0.22} />
            <stop offset="0.6" stopColor={P.color} stopOpacity={0.05} />
            <stop offset="1" stopColor={P.color} stopOpacity={0} />
          </radialGradient>
        </defs>
        <ellipse cx={540} cy={760} rx={540} ry={520} fill="url(#spot)" />
        {/* Architectural shaft framing (refined Look A depth, not a cartoonish backdrop) */}
        {[85, 975].map((x) => <rect key={x} x={x} y={530} width={20} height={630} rx={4} fill="#181C26" stroke="#282E3E" strokeWidth={2} />)}
        {Array.from({ length: 8 }).map((_, i) => (
          <g key={i} opacity={1 - ease(f, s2 - 10, s2)}>
            <line x1={105} x2={shaftLeft - 14} y1={556 + i * 80} y2={556 + i * 80} stroke="#3A4256" strokeWidth={2} />
            <rect x={108} y={548 + i * 80 - 30} width={74} height={40} rx={10} fill={C.ink} />
            <text x={118} y={548 + i * 80} fill={C.paper} fontFamily={MONO} fontSize={30} fontWeight={700}>L{String(8 - i).padStart(2, "0")}</text>
          </g>
        ))}

        {/* Scale-reveal camera group centered on the bright car at f=0, pulling out to full hoistway */}
        <g transform={`translate(${Math.sin(f / 37) * 5} ${Math.sin(f / 45) * 4 + offY}) translate(540 860) scale(${zoom}) translate(${-540 + (540 - zFocusX) * zk} ${-860 + (860 - zFocusY) * zk})`}>
          {/* Bright cutaway hoistway (guarantees high contrast and bright frame 0) */}
          <rect x={shaftLeft} y={SY - 70} width={shaftW} height={pitY - (SY - 70)} rx={22} fill="#EAE3D4" stroke="#5E6678" strokeWidth={4} />
          <rect x={shaftLeft + shaftW * 0.5} y={SY - 70} width={shaftW * 0.5} height={pitY - (SY - 70)} rx={0} fill="#DCD4C2" />
          {Array.from({ length: 10 }).map((_, i) => (
            <line key={i} x1={shaftLeft + 8} x2={shaftRight - 8} y1={SY + 40 + i * 64} y2={SY + 40 + i * 64} stroke="#C7BFAE" strokeWidth={2} />
          ))}

          {/* Steel T-guide rails for car and counterweight */}
          {[CAR_X - CAR_W / 2 - 12, CAR_X + CAR_W / 2 + 12, CW_X - CW_W / 2 - 10, CW_X + CW_W / 2 + 10].map((x, idx) => (
            <line key={idx} x1={x} x2={x} y1={SY + 10} y2={pitY - 12} stroke="#5B6375" strokeWidth={6} />
          ))}
          {/* Pit spring buffers */}
          <SpringBuffer x={CAR_X} y={pitY - 4} compress={Math.max(0, (carTop - 800) / 80)} />
          <SpringBuffer x={CW_X} y={pitY - 4} compress={Math.max(0, (cwTop - 800) / 80)} />

          {/* Machine room bedplate + Motor + cooling flywheel */}
          <rect x={SX - 20} y={SY - 12} width={355} height={24} rx={6} fill="#363D4E" />
          <g transform={`translate(${SX + 150} ${SY - 96})`}>
            <rect x={0} y={0} width={172} height={92} rx={16} fill={motorOn ? C.amber : "#3B4354"} stroke={C.ink} strokeWidth={4} />
            {[16, 34, 52, 70].map((y) => <line key={y} x1={14} x2={158} y1={y} y2={y} stroke={C.ink} strokeWidth={4} opacity={0.22} />)}
            {motorP > 0 && (
              <Enter p={motorP} cx={86} cy={44}>
                <g transform={`translate(86 44) scale(${motorRe}) translate(-86 -44)`}>
                  <text x={86} y={56} fill={motorOn ? C.ink : C.paper} fontFamily={DISPLAY} fontWeight={700} fontSize={32} textAnchor="middle">MOTOR</text>
                </g>
              </Enter>
            )}
            <circle cx={146} cy={22} r={8} fill={motorOn ? C.ink : C.amber} />
            {/* Spinning end flywheel */}
            <g transform={`translate(178 46) rotate(${motorDeg})`}>
              <rect x={-10} y={-34} width={20} height={68} rx={6} fill="#5E6678" stroke={C.ink} strokeWidth={3} />
              <line x1={0} y1={-28} x2={0} y2={28} stroke={C.amber} strokeWidth={4} />
            </g>
          </g>
          {/* Drive shaft coupling to main traction sheave */}
          <rect x={SX} y={SY - 62} width={150} height={18} rx={6} fill="#5E6678" stroke={C.ink} strokeWidth={3} />

          {/* rise streaks: floor-speed lines trailing the empty car (surprise punch) */}
          {f >= rise - 6 && f <= riseEnd + 6 && [0, 1, 2, 3, 4, 5].map((k) => {
            const env = Math.min(1, ease(f, rise - 6, rise + 4)) * (1 - ease(f, riseEnd - 4, riseEnd + 6));
            const y0 = carTop + ((k * 83 + (f - rise) * 34) % 330 + 330) % 330;
            const x = CAR_X + (k % 2 === 0 ? -1 : 1) * (CAR_W / 2 + 34 + (k >> 1) * 0);
            return <line key={k} x1={x} x2={x} y1={y0} y2={y0 + 62} stroke={C.amber} strokeWidth={6} strokeLinecap="round" opacity={0.85 * env} />;
          })}

          {/* Running hoist cables (twin ropes + moving strand dashes coupled 1:1 to carTop) */}
          <line x1={CAR_X - 5} y1={SY} x2={CAR_X - 5} y2={carTop} stroke="#1B1F2A" strokeWidth={5} />
          <line x1={CAR_X + 5} y1={SY} x2={CAR_X + 5} y2={carTop} stroke="#1B1F2A" strokeWidth={5} />
          <line x1={CAR_X} y1={SY} x2={CAR_X} y2={carTop} stroke={C.amber} strokeWidth={4} strokeDasharray="12 18" strokeDashoffset={-carTop} opacity={0.85} />

          {/* Crossover cable over main sheave to deflector sheave */}
          <line x1={SX} y1={SY - SR} x2={DEF_X} y2={DEF_Y - DEF_R} stroke="#1B1F2A" strokeWidth={8} />
          <line x1={SX} y1={SY - SR} x2={DEF_X} y2={DEF_Y - DEF_R} stroke={C.amber} strokeWidth={4} strokeDasharray="12 18" strokeDashoffset={-carTop} opacity={0.85} />

          {/* Right cable down to counterweight (moves OPPOSITE to carTop!) */}
          <line x1={CW_X - 5} y1={DEF_Y} x2={CW_X - 5} y2={cwTop} stroke="#1B1F2A" strokeWidth={5} />
          <line x1={CW_X + 5} y1={DEF_Y} x2={CW_X + 5} y2={cwTop} stroke="#1B1F2A" strokeWidth={5} />
          <line x1={CW_X} y1={DEF_Y} x2={CW_X} y2={cwTop} stroke={P.color} strokeWidth={4} strokeDasharray="12 18" strokeDashoffset={carTop} opacity={0.9} />

          {/* Main grooved traction sheave */}
          <g transform={`translate(${SX} ${SY}) scale(${1 + strainQ} ${1 - strainQ}) rotate(${sheaveDeg})`}>
            <circle r={SR + 6} fill="#2A303E" stroke={C.ink} strokeWidth={4} />
            <circle r={SR - 6} fill="#464E62" stroke={C.amber} strokeWidth={3} strokeDasharray="18 14" />
            <circle r={SR - 16} fill="#232734" />
            {[0, 60, 120, 180, 240, 300].map((a) => (
              <rect key={a} x={0} y={-6} width={SR - 18} height={12} rx={5} fill="#5E6678" transform={`rotate(${a})`} />
            ))}
            <circle r={24} fill={C.amber} stroke={C.ink} strokeWidth={4} />
            <circle r={8} fill={C.ink} />
          </g>

          {/* Secondary deflector/idler sheave */}
          <g transform={`translate(${DEF_X} ${DEF_Y}) rotate(${defDeg})`}>
            <circle r={DEF_R} fill="#363D4E" stroke={C.ink} strokeWidth={4} />
            {[0, 90, 180, 270].map((a) => <line key={a} x1={0} y1={0} x2={DEF_R - 8} y2={0} stroke="#8B91A1" strokeWidth={6} transform={`rotate(${a})`} />)}
            <circle r={12} fill={C.amber} />
          </g>

          {/* Articulated caliper brake shoes */}
          {showBrake && [-1, 1].map((d) => (
            <g key={d} transform={`translate(${SX} ${SY}) rotate(${d * 38 - 90})`}>
              <rect x={SR + 10 + brakeOpen * 34 - (brakeOpen < 0.5 ? 3 + Math.sin(f / 3) * 3 : 0)} y={-28} width={32} height={56} rx={8} fill={brakeOpen > 0.5 ? C.amber : C.red} stroke={C.ink} strokeWidth={3} />
            </g>
          ))}
          {showBrake && (
            <TagLabel key={brakeOpen > 0.5 ? "off" : "on"} x={SX - SR - 153} y={SY - 77} text={brakeOpen > 0.5 ? "BRAKE OFF" : "BRAKE ON"} size={32} color={brakeOpen > 0.5 ? C.amber : C.red}
              o={Math.min(1, pop(f, brakeOpen > 0.5 ? rel + 6 : rel - 30, fps))} />
          )}

          {/* Elevator Car with isometric extrusion, sliding doors, guide shoes, backlit interior */}
          <g transform={`translate(${CAR_X - CAR_W / 2} ${carTop})`}>
            <Extrude w={CAR_W} h={CAR_H} top="#5A6378" side="#272D3B" />
            <rect width={CAR_W} height={CAR_H} rx={16} fill="#2B3140" stroke={f < s2 ? C.amber : C.ink} strokeWidth={6} />
            <rect x={14} y={24} width={CAR_W - 28} height={CAR_H - 38} rx={8} fill="#F9F4E8" />
            <rect x={28} y={28} width={CAR_W - 56} height={10} rx={5} fill={C.amber} opacity={0.85} />
            {Array.from({ length: people }).map((_, i) => (
              <Person key={i} x={48 + (i % 4) * 42} y={CAR_H - 28 - Math.floor(i / 4) * 86} c={i % 2 === 0 ? "#1F2430" : "#C97D0C"} s={0.86 * Math.max(0, personSc(i))} />
            ))}
            {/* Center-parting sliding doors */}
            <rect x={14} y={24} width={(CAR_W / 2 - 14) * (1 - doorOpen * 0.85)} height={CAR_H - 38} fill="#8B91A1" opacity={0.35} />
            <rect x={CAR_W - 14 - (CAR_W / 2 - 14) * (1 - doorOpen * 0.85)} y={24} width={(CAR_W / 2 - 14) * (1 - doorOpen * 0.85)} height={CAR_H - 38} fill="#72798C" opacity={0.35} />
            {/* 4 roller guide shoes gripping the rails */}
            <GuideShoe x={-8} y={20} /><GuideShoe x={CAR_W + 8} y={20} />
            <GuideShoe x={-8} y={CAR_H - 20} /><GuideShoe x={CAR_W + 8} y={CAR_H - 20} />
            <rect x={CAR_W / 2 - 44} y={-38} width={88} height={32} rx={8} fill={C.ink} />
            <text x={CAR_W / 2} y={-13} fill={C.paper} fontFamily={DISPLAY} fontWeight={700} fontSize={30} textAnchor="middle">CAR</text>
          </g>

          {/* Counterweight frame with stacked cast-iron plates + guide shoes */}
          <g transform={`translate(${CW_X - CW_W / 2} ${cwTop})`}>
            <Extrude w={CW_W} h={CW_H} d={16} top={cwLit ? "#A8E6B0" : "#6D758A"} side={cwLit ? "#4F9A5A" : "#353B4B"} />
            <rect width={CW_W} height={CW_H} rx={12} fill={cwLit ? P.color : "#5A6275"} stroke={C.ink} strokeWidth={4} />
            {Array.from({ length: 6 }).map((_, i) => <line key={i} x1={8} x2={CW_W - 8} y1={(i + 1) * (CW_H / 7)} y2={(i + 1) * (CW_H / 7)} stroke={C.ink} strokeWidth={3} opacity={0.35} />)}
            <GuideShoe x={-6} y={22} /><GuideShoe x={CW_W + 6} y={22} />
            <GuideShoe x={-6} y={CW_H - 22} /><GuideShoe x={CW_W + 6} y={CW_H - 22} />
            {cwSplit > 0 && (
              <g>
                {/* plate-stack fill rises from the base (draws on, no opacity fade) */}
                <rect y={CW_H - CW_H * 0.38 * cwSplit} width={CW_W} height={CW_H * 0.38 * cwSplit} rx={10} fill={C.amber} />
                <TagLabel x={CW_W + 36} y={CW_H * 0.24 + 8} text="= EMPTY CAR" size={30} color={P.color} anchor="start" o={Math.min(1, pop(f, at("It's built"), fps))} />
                <TagLabel x={CW_W + 36} y={CW_H * 0.66 + 8} text="+ 40–50% LOAD" size={30} color={C.amber} anchor="start" o={Math.min(1, pop(f, at("plus about"), fps))} />
              </g>
            )}
          </g>

          {/* Force arrows (r6 clarity): gravity on car + counterweight (length = weight), motor torque on the sheave (width = difference) */}
          {f >= fdF && f < s5 && (() => {
            // car gravity arrow: pops in when the car turns heavier, shrinks out when the counterweight takes over / on release
            const carArrowP = f < flip1 ? 0 : f < flip2 ? ease(f, flip1, flip1 + 14) : f < rel - 30 ? 1 - ease(f, flip2, flip2 + 8) : 1 - ease(f, rel - 30, rel - 22);
            const ft = f >= flip2 ? flip2 : f >= flip1 ? flip1 : -1;
            const torqueSc = ft < 0 ? 1 : 0.72 + 0.28 * pop(f, ft, fps); // torque arrow flips with a spring pop
            const gCar = carLoad * 0.03, gCw = 4875 * 0.03;
            const diff = Math.abs(carLoad - 4875), cwSide = carLoad > 4875; // car heavier => motor pulls it up (clockwise); else motor holds counterweight back (counter-clockwise)
            const torque = f < rel - 30 && f < s4;
            const R = SR + 30, a0 = (190 * Math.PI) / 180, a1 = (290 * Math.PI) / 180;
            const pt = (t: number): [number, number] => [SX + R * Math.cos(t), SY + R * Math.sin(t)];
            const [x0, y0] = pt(a0), [x1, y1] = pt(a1);
            const tw = 4 + diff / 90;
            const tip = cwSide ? a1 : a0, dirS = cwSide ? 1 : -1;
            const [px, py] = pt(tip), dx = -Math.sin(tip) * dirS, dy = Math.cos(tip) * dirS;
            const head = `${px + dx * 30},${py + dy * 30} ${px - dy * 22},${py + dx * 22} ${px + dy * 22},${py - dx * 22}`;
            const down = (x: number, y: number, len: number) => (
              <g>
                <line x1={x} x2={x} y1={y} y2={y + len - 24} stroke={C.ink} strokeWidth={22} strokeLinecap="round" />
                <polygon points={`${x - 30},${y + len - 30} ${x + 30},${y + len - 30} ${x},${y + len + 6}`} fill={C.ink} stroke={C.ink} strokeWidth={6} strokeLinejoin="round" />
                <line x1={x} x2={x} y1={y} y2={y + len - 24} stroke={C.amber} strokeWidth={12} strokeLinecap="round" />
                <polygon points={`${x - 24},${y + len - 28} ${x + 24},${y + len - 28} ${x},${y + len}`} fill={C.amber} />
              </g>
            );
            // arrows hang BELOW the bodies (clear of riders, on the dark shaft); the car's gravity arrow shows only while the car is the heavier side
            const carBot = carTop + CAR_H, cwBot = cwTop + CW_H;
            const lenC = Math.max(34, Math.min(gCar, 1112 - carBot)), lenW = Math.max(34, Math.min(gCw, 1112 - cwBot));
            return (
              <g>
                <Enter p={carArrowP} cx={CAR_X} cy={carBot + 4} from="down" dist={60}>{down(CAR_X, carBot + 4, lenC)}</Enter>
                <Enter p={ease(f, fdF, fdF + 14)} cx={CW_X} cy={cwBot + 4} from="down" dist={60}>{down(CW_X, cwBot + 4, lenW)}</Enter>
                <Enter p={ease(f, fdF + 4, fdF + 18)} cx={SX} cy={SY}>
                {torque && (
                  <g transform={`translate(${SX} ${SY}) scale(${torqueSc}) translate(${-SX} ${-SY})`}>
                    <path d={`M${x0},${y0} A${R},${R} 0 0 1 ${x1},${y1}`} fill="none" stroke={C.ink} strokeWidth={tw + 8} strokeLinecap="round" />
                    <path d={`M${x0},${y0} A${R},${R} 0 0 1 ${x1},${y1}`} fill="none" stroke={C.amber} strokeWidth={tw} strokeLinecap="round" strokeDasharray="30 14" strokeDashoffset={-dirS * f * 2.5} />
                    <polygon points={head} fill={C.amber} stroke={C.ink} strokeWidth={5} strokeLinejoin="round" />
                  </g>
                )}
                </Enter>
              </g>
            );
          })()}

          {/* Balanced tag in Shot 1 */}
          {f < s2 && (
            <TagLabel x={540} y={1041} text="≈ BALANCED" size={40} color={P.color} o={Math.min(1, pop(f, at("almost balances"), fps))} />
          )}
          {f >= s2 - 6 && f < s3 && (
            <TagLabel x={CW_X} y={cwTop - 39} text="COUNTERWEIGHT" size={30} color={P.color} o={Math.min(1, pop(f, s2, fps))} />
          )}

          {/* Live weight comparison bars in Shot 3 */}
          {bars > 0 && (() => {
            const legO = bars * (1 - ease(f, fdF, fdF + 8));
            const sc = 0.062, hc = carLoad * sc * bars, hw = 4875 * sc * bars, base = 1050;
            const top = Math.min(hc, hw), diff = Math.abs(hc - hw), carHeavier = hc > hw;
            const cx = 84, wx = 152; // panel x 64-224: >= 64 px from the frame edge even under the chapter-3 camera
            return (
              <g>
                <rect x={64} y={base - 440} width={160} height={460} rx={16} fill={C.ink} opacity={0.85} />
                <rect x={cx} y={base - hc} width={52} height={hc} rx={8} fill={C.paper} />
                <rect x={wx} y={base - hw} width={52} height={hw} rx={8} fill={P.color} />
                <g transform={`translate(${carHeavier ? cx : wx} ${base - top}) scale(1 ${ease(f, s3 + 10, s3 + 26)}) translate(0 ${-(base - top)})`}><rect x={0} y={base - top - diff} width={52} height={diff} rx={8} fill={C.amber} /></g>
                <line x1={74} x2={214} y1={base - top} y2={base - top} stroke={C.dim} strokeWidth={3} strokeDasharray="10 10" />
                {/* legend keeps the colour cue: car = white, counterweight = teal (Lane guarantees the 36 px gap) */}
                <Lane x={64} y={base - 440 - 44} dir="up" align="start" gap={44} items={[
                  { w: 90, h: 52, node: <TagLabel x={18} y={34} text="CAR" size={30} color={C.paper} o={legO} anchor="start" /> },
                  { w: 72, h: 52, node: <TagLabel x={18} y={34} text="CW" size={30} color={P.color} o={legO} anchor="start" /> },
                ]} />
              </g>
            );
          })()}

          {/* shockwave ring off the car at the start of the rise (continuous burst) */}
          {f >= rise - 4 && f < rise + 20 && (() => {
            const t = (f - (rise - 4)) / 24;
            return <circle cx={CAR_X} cy={carTop + CAR_H / 2} r={60 + 230 * t} fill="none" stroke={C.amber} strokeWidth={10 * (1 - t) + 2} opacity={0.8 * (1 - t)} />;
          })()}
          {/* Rising arrow on empty-car release */}
          {f >= rise - 6 && f < s5 && (
            <g transform={`translate(${CAR_X} ${carTop + CAR_H + 80}) scale(${popScale(pop(f, rise - 4, fps))})`} opacity={popOpacity(pop(f, rise - 4, fps))}>
              <circle r={46} fill={C.ink} stroke={C.amber} strokeWidth={4} />
              {/* r5: cascading chevrons (continuous upward motion instead of a static glyph; critic v4 0:32) */}
              {[0, 1, 2].map((k) => {
                const ph = (((f - rise) / 16 + k / 3) % 1 + 1) % 1;
                return <path key={k} d="M-20,10 L0,-10 L20,10" transform={`translate(0 ${22 - ph * 44})`} stroke={C.amber} strokeWidth={8}
                  fill="none" strokeLinecap="round" strokeLinejoin="round" opacity={Math.sin(ph * Math.PI)} />;
              })}
            </g>
          )}
        </g>
      </Stage>
      {f < s2 && (
        <div style={{ position: "absolute", left: 0, top: 0, width: 1080, height: 1920, transform: "scale(0.85)", transformOrigin: "48px 0", pointerEvents: "none" }}>
          <TitleHook t={["THE ELEVATOR THAT", "BARELY LIFTS", "YOU"]} top={353} o={titleO} />
        </div>
      )}
    </>
  );
};

/** Screen-space verdict pills + Washington Monument real-photo ProofCard in Shot 5. */
const RigHud: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s3 = at("So the motor"), s4 = at("Here's the strange"), s5 = at("That's why a"), stamp = at("That's the mechanism");
  const empty = at("nearly empty"), rise = at("It would rise"), fd = at("fights the difference"), office = at("full office");
  const helps = at("helps it up"), holds = at("holds it back");
  return (
    <>
      <Stage>
        {f >= fd && f < s4 && (() => {
          const seg = f >= holds ? 3 : f >= empty ? 2 : f >= helps ? 1 : 0;
          const t0 = [fd, helps, empty, holds][seg];
          return <TagLabel key={seg} x={540} y={1150} size={44} text={["DIFFERENCE", "MOTOR HELPS IT UP", "DIFFERENCE", "MOTOR HOLDS IT BACK"][seg]} color={C.amber} o={ease(f, t0, t0 + 12)} />;
        })()}
        {f >= at("wouldn't fall") && f < s5 && <TagLabel key={f >= rise ? 1 : 0} x={540} y={1150} size={44} text={f >= rise ? "EMPTY CAR RISES" : "IT WOULDN'T FALL"} color={f >= rise ? C.amber : C.paper} o={ease(f, f >= rise ? rise : at("wouldn't fall"), (f >= rise ? rise : at("wouldn't fall")) + 12)} />}
        {f >= s5 && f < office && <TagLabel x={540} y={1164} size={44} text="SMALL MOTOR · FULL OFFICE" color={P.color} o={ease(f, at("modest motor"), at("modest motor") + 12)} />}
        {f >= s3 && f < fd && null}
      </Stage>
      {f >= office && f < stamp && (
        <ProofCard src="photos/02-elevator--habs-motor-graded.jpg"
          tag="TRACTION MACHINE" credit="PHOTO: JACK E. BOUCHER, HABS / LOC · PUBLIC DOMAIN"
          aspect={1920 / 2664} focus={[0.25, 0.14, 0.90, 0.86]} focusLabel="MOTOR + DRIVE SHEAVE"
          startFrame={office} duration={Math.max(45, stamp - office)} />
      )}
    </>
  );
};

/** Payoff, settled >= 1.5 s before loop: animated scale tips, bounces, then locks horizontal while crane gets struck out. */
const ScaleNotCrane: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const fin = at("An elevator is a"), sc = at("a scale"), cr = at("not a crane");
  const inL = pop(f, fin - 2, fps), inR = pop(f, fin + 4, fps), win = pop(f, sc, fps), strike = ease(f, cr, cr + 8);
  // Tip left (-11 deg), rebound right (+6 deg), then damp smoothly to balanced 0 deg by cr + 10
  const tilt = f < sc ? interpolate(f, [fin, sc], [-11, 5], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.sin) })
    : interpolate(f, [sc, sc + 16], [5, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.back(2.0)) }) + Math.sin(f / 18) * 0.7;
  const dropCar = pop(f, fin + 2, fps), dropCw = pop(f, fin + 6, fps);
  return (
    <Stage>
      <g transform={`translate(285 750) scale(${0.92 + 0.08 * inL})`} opacity={Math.min(1, inL)}>
        <rect x={-210} y={-350} width={420} height={700} rx={36} fill={C.ink2} stroke={C.line} strokeWidth={4} />
        <rect x={-210} y={-350} width={420} height={700} rx={36} fill="none" stroke={C.green} strokeWidth={8} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - Math.min(1, win)} />
        <polygon points="0,-30 -64,175 64,175" fill={P.color} />
        <g transform={`rotate(${tilt})`}>
          <rect x={-180} y={-52} width={360} height={22} rx={11} fill={C.paper} />
          <g transform={`translate(-172 ${-192 - (1 - dropCar) * 40})`} opacity={Math.min(1, dropCar)}>
            <Extrude w={112} h={140} top="#4B5569" side="#1F2430" />
            <rect width={112} height={140} rx={14} fill="#2B3140" stroke={C.paper} strokeWidth={5} />
            <text x={56} y={84} fill={C.paper} fontFamily={DISPLAY} fontWeight={700} fontSize={32} textAnchor="middle">CAR</text>
          </g>
          <g transform={`translate(66 ${-172 - (1 - dropCw) * 40})`} opacity={Math.min(1, dropCw)}>
            <Extrude w={94} h={120} d={16} top="#A8E6B0" side="#4F9A5A" />
            <rect width={94} height={120} rx={12} fill={P.color} />
            <text x={47} y={74} fill={C.ink} fontFamily={DISPLAY} fontWeight={700} fontSize={32} textAnchor="middle">CW</text>
          </g>
        </g>
        <Scale x={-34} y={200} width={68} height={68} color={C.green} strokeWidth={2.5} />
        <Label x={0} y={318} text="A SCALE" size={62} color={C.green} />
      </g>
      {/* Dim ONLY crane artwork on strike; label stays outside at full opacity (L-13 WCAG fix) */}
      <g transform={`translate(735 750) scale(${0.92 + 0.08 * inR})`} opacity={Math.min(1, inR) * (1 - 0.45 * strike)}>
        <rect x={-210} y={-350} width={420} height={700} rx={36} fill={C.ink2} stroke={C.line} strokeWidth={4} />
        <rect x={-210} y={-350} width={420} height={700} rx={36} fill="none" stroke={C.red} strokeWidth={6} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - strike} />
        <rect x={-14} y={-245} width={28} height={415} fill={C.dim} />
        <rect x={-160} y={-257} width={280} height={24} fill={C.dim} />
        <line x1={-140} y1={-233} x2={-140} y2={-60 + Math.sin(f / 10) * 6} stroke={C.dim} strokeWidth={6} />
        <rect x={-180} y={-60 + Math.sin(f / 10) * 6} width={80} height={70} rx={8} fill={C.dim} />
      </g>
      <g transform={`translate(735 750) scale(${0.92 + 0.08 * inR})`} opacity={Math.min(1, inR)}>
        <Label x={0} y={318} text="A CRANE" size={62} color={strike > 0.5 ? C.red : C.paper} />
      </g>
      <g transform="translate(735 750)">
        <line x1={-180} y1={-320} x2={180} y2={240} stroke={C.red} strokeWidth={18} strokeLinecap="round" strokeDasharray={720} strokeDashoffset={720 * (1 - strike)} />
        <g transform={`translate(140 -285) scale(${popScale(pop(f, cr + 4, fps))})`} opacity={popOpacity(pop(f, cr + 4, fps))}><circle r={56} fill={C.red} /><X x={-36} y={-36} width={72} height={72} color="white" strokeWidth={3.5} /></g>
      </g>
      {f >= cr && (() => {
        // soft ring pulses off the green check + amber sheen sweeping the beam keep the settled state alive
        const ph = (((f - cr) / 36) % 1 + 1) % 1, sh = (((f - cr) / 36) % 1 + 1) % 1;
        return (
          <g>
            <circle cx={425} cy={465} r={56 + 70 * ph} fill="none" stroke={C.green} strokeWidth={8 * (1 - ph) + 1} opacity={0.7 * (1 - ph)} />
            <g transform={`translate(285 750) rotate(${tilt})`}><rect x={-180 + 340 * sh} y={-52} width={24} height={22} rx={11} fill={C.amber} opacity={0.8 * Math.sin(sh * Math.PI)} /></g>
          </g>
        );
      })()}
      <g transform={`translate(425 465) scale(${win})`}><circle r={56} fill={C.green} /><Check x={-36} y={-36} width={72} height={72} color={C.ink} strokeWidth={3.5} /></g>
    </Stage>
  );
};

export const ElevatorVideo: React.FC = () => {
  const { fps, durationInFrames: D } = useVideoConfig();
  const at = makeAt(words, fps);
  const s2 = at("On the other side"), s3 = at("So the motor"), s4 = at("Here's the strange"), s5 = at("That's why a"),
    card = at("That's the mechanism"), fin = at("An elevator is a"), loop = D - LOOP_FRAMES;
  const full = at("car is full"), empty = at("nearly empty"), rel = at("Release"), rise = at("It would rise");
  const cues = [
    cue(4, "swish", 0.75), cue(at("almost balances"), "pop", 0.76),
    cue(s2, "whoosh", 0.78), cue(at("It's built"), "clank", 0.72), cue(at("plus about"), "pop", 0.76),
    cue(s3, "whoosh", 0.78), cue(at("helps it up"), "pop", 0.76), cue(at("fights the difference"), "pop", 0.76), cue(empty + 10, "pop", 0.76),
    cue(s4, "riser", 0.65), cue(rel + 2, "clank", 0.72), cue(rise - 4, "whoosh", 0.75), ...reveal(rise, 0.68),
    cue(s5, "whoosh", 0.75), cue(at("modest motor"), "pop", 0.76), cue(at("full office"), "pop3", 0.72),
    ...reveal(at("a scale"), 0.74), cue(at("not a crane"), "error", 0.7),
  ];
  return (
    <EpisodeShell audio="02-elevator.wav" words={words} pillar={P} ep="002" source="TK ELEVATOR" microGap={18}
      cardAt={card} cardUntil={fin} cues={cues} hook={<Rig />}
      chapters={[{ at: 0, label: "IT ALMOST BALANCES" }, { at: s2, label: "THE COUNTERWEIGHT" }, { at: s3, label: "ONLY THE DIFFERENCE" }, { at: s4, label: "THE STRANGE PART" }, { at: s5, label: "WHY IT'S CHEAP" }]}>
      <Shot from={0} to={card} inT="none" outT="push" cam={[
        // r6 pass 2: camera keeps the pit/shaft floor above the caption band (390*s + y <= 435, <= 360 once the HUD tag is up)
        // and the chapter-3 bar panel >= 24 px from the left edge.
        { at: s2, kind: "glide", s: 1.18, x: -120, y: -30 },
        { at: at("It's built"), kind: "push", s: 1.24, x: -165, y: -50 },
        { at: at("plus about"), kind: "glide", s: 1.18, x: -205, y: -30 },
        { at: s3, kind: "pull", s: 0.94, x: 0, y: -10 },
        { at: at("fights the difference"), kind: "punch", s: 1.04, x: 0, y: -45 },
        { at: full, kind: "push", s: 1.02, x: 0, y: -38 },
        { at: empty, kind: "punch", s: 1.04, x: 0, y: -45 },
        { at: at("heavier side"), kind: "glide", s: 1.02, x: 0, y: -38 },
        { at: s4, kind: "push", s: 1.14, x: 30, y: -85 },
        { at: rise - 2, kind: "punch", s: 1.06, x: 10, y: -55 },
        { at: s5, kind: "glide", s: 1.02, x: 0, y: -38 },
        { at: at("full office"), kind: "pull", s: 1.0, x: 0, y: -30 },
      ]} hud={<RigHud />}><Rig /></Shot>
      <Shot from={fin} to={loop} inT="push" outT="whip" cam={[{ at: fin, kind: "push", s: 1.02, dur: 40 }]}><ScaleNotCrane /></Shot>
    </EpisodeShell>
  );
};
