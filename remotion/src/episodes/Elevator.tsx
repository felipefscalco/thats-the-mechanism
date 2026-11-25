import React from "react";
import { Easing, interpolate, useVideoConfig } from "remotion";
import words from "../02-elevator.captions.json";
import { Check, X, Zap, ArrowUp, Scale } from "lucide-react";
import { C, DISPLAY, EpisodeShell, Label, LOOP_FRAMES, MONO, PILLARS, Pill, ProofCard, Shot, Stage, TitleHook, cue, ease, makeAt, pop, popOpacity, popScale, reveal, useG } from "../brand";

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
  const full = at("car is full"), empty = at("nearly empty"), holds = at("holds it back"), rel = at("Release"), rise = at("It would rise");

  // Scale reveal: f=0 zoomed 2.25x on the bright elevator car + rider, pulling out smoothly to show the full shaft & counterweight
  const zoom = interpolate(f, [3, 38], [1.95, 1.0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const zFocusX = CAR_X, zFocusY = 980;

  // Car vertical trajectory with anticipation dip and overshoot bounce on the release reveal
  let carTop = smoothKeyed(f, [[0, 835], [75, 715], [at("plus about"), 715], [s3, 740], [full - 8, 705], [full + 8, 720], [full + 48, 675], [empty - 6, 675], [holds + 22, 845], [rel - 6, 845], [rel + 2, 855], [rise - 6, 845], [rise + 26, 625], [s5, 625], [s5 + 24, 750]], f >= rel && f <= rise + 28);
  if (f >= 75 && f < s3) carTop += Math.sin((f - 75) / 8) * 18;
  if (f >= s5 + 24 && f < stamp) carTop = 740 + Math.sin((f - s5 - 24) / 14) * 115;
  const cwTop = SUM - carTop; // strictly coupled opposite motion

  const sheaveDeg = -(carTop - 815) * (180 / Math.PI / SR);
  const defDeg = (carTop - 815) * (180 / Math.PI / DEF_R);
  const motorDeg = (carTop - 815) * 4.2;

  const people = f < full ? 2 : f < empty ? Math.min(7, 2 + Math.floor((f - full) / 4)) : f < s4 ? 1 : f < s5 ? 0 : Math.min(6, Math.floor((f - s5) / 4));
  const doorOpen = f >= full - 6 && f < full + 18 ? ease(f, full - 6, full + 2) * (1 - ease(f, full + 10, full + 18)) : 0;
  const brakeOpen = ease(f, rel + 2, rel + 12);
  const showBrake = f >= s4 - 6 && f < s5;
  const cwSplit = f >= s2 && f < s3 ? ease(f, at("It's built"), at("It's built") + 10) : 0;
  const bars = f >= s3 && f < s4 ? ease(f, s3, s3 + 10) : 0;
  const carLoad = f < full ? 3300 + 2 * 175 : f < empty ? 6800 : 3300 + 175;
  const motorOn = f >= s5 && f < stamp;
  const cwLit = f >= at("almost balances");
  const shaftLeft = CAR_X - CAR_W / 2 - 42, shaftRight = CW_X + CW_W / 2 + 42, shaftW = shaftRight - shaftLeft;
  const pitY = 1130;
  const titleO = 1 - ease(f, s2 - 10, s2);

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
        {[85, 975].map((x) => <rect key={x} x={x} y={290} width={20} height={870} rx={4} fill="#181C26" stroke="#282E3E" strokeWidth={2} />)}
        {Array.from({ length: 8 }).map((_, i) => (
          <g key={i} opacity={0.45}>
            <line x1={105} x2={shaftLeft - 14} y1={420 + i * 95} y2={420 + i * 95} stroke="#2A3040" strokeWidth={2} />
            <text x={118} y={412 + i * 95} fill="#5A6174" fontFamily={MONO} fontSize={30} fontWeight={700}>L{String(8 - i).padStart(2, "0")}</text>
          </g>
        ))}

        {/* Scale-reveal camera group centered on the bright car at f=0, pulling out to full hoistway */}
        <g transform={`translate(540 860) scale(${zoom}) translate(${-540 + (540 - zFocusX) * ((zoom - 1) / 0.95)} ${-860 + (860 - zFocusY) * ((zoom - 1) / 0.95)})`}>
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
            <rect x={0} y={0} width={172} height={92} rx={16} fill={motorOn ? P.color : "#3B4354"} stroke={C.ink} strokeWidth={4} />
            {[16, 34, 52, 70].map((y) => <line key={y} x1={14} x2={158} y1={y} y2={y} stroke={C.ink} strokeWidth={4} opacity={0.22} />)}
            <text x={86} y={56} fill={motorOn ? C.ink : C.paper} fontFamily={DISPLAY} fontWeight={700} fontSize={32} textAnchor="middle">MOTOR</text>
            <circle cx={146} cy={22} r={8} fill={motorOn ? C.amber : C.green} />
            {/* Spinning end flywheel */}
            <g transform={`translate(178 46) rotate(${motorDeg})`}>
              <rect x={-10} y={-34} width={20} height={68} rx={6} fill="#5E6678" stroke={C.ink} strokeWidth={3} />
              <line x1={0} y1={-28} x2={0} y2={28} stroke={C.amber} strokeWidth={4} />
            </g>
          </g>
          {/* Drive shaft coupling to main traction sheave */}
          <rect x={SX} y={SY - 62} width={150} height={18} rx={6} fill="#5E6678" stroke={C.ink} strokeWidth={3} />

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
          <g transform={`translate(${SX} ${SY}) rotate(${sheaveDeg})`}>
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
              <rect x={SR + 10 + brakeOpen * 34} y={-28} width={32} height={56} rx={8} fill={brakeOpen > 0.5 ? C.amber : C.red} stroke={C.ink} strokeWidth={3} />
            </g>
          ))}
          {showBrake && (
            <g transform={`translate(${SX - SR - 28} ${SY - 54})`}>
              <rect x={-210} y={-26} width={210} height={50} rx={25} fill={C.ink} />
              <text x={-105} y={10} fill={brakeOpen > 0.5 ? C.amber : C.red} fontFamily={DISPLAY} fontWeight={700} fontSize={32} textAnchor="middle">{brakeOpen > 0.5 ? "BRAKE OFF" : "BRAKE ON"}</text>
            </g>
          )}

          {/* Elevator Car with isometric extrusion, sliding doors, guide shoes, backlit interior */}
          <g transform={`translate(${CAR_X - CAR_W / 2} ${carTop})`}>
            <Extrude w={CAR_W} h={CAR_H} top="#5A6378" side="#272D3B" />
            <rect width={CAR_W} height={CAR_H} rx={16} fill="#2B3140" stroke={f < s2 ? C.amber : C.ink} strokeWidth={6} />
            <rect x={14} y={24} width={CAR_W - 28} height={CAR_H - 38} rx={8} fill="#F9F4E8" />
            <rect x={28} y={28} width={CAR_W - 56} height={10} rx={5} fill={C.amber} opacity={0.85} />
            {Array.from({ length: people }).map((_, i) => (
              <Person key={i} x={48 + (i % 4) * 42} y={CAR_H - 28 - Math.floor(i / 4) * 86} c={i % 2 === 0 ? "#1F2430" : "#C97D0C"} s={0.86} />
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
              <g opacity={cwSplit}>
                <rect y={CW_H * 0.62} width={CW_W} height={CW_H * 0.38} rx={10} fill={C.amber} />
                <g transform={`translate(${CW_W + 18} ${CW_H * 0.28})`}>
                  <rect x={0} y={-28} width={225} height={44} rx={22} fill={C.ink} />
                  <text x={112} y={4} fill={P.color} fontFamily={DISPLAY} fontWeight={700} fontSize={30} textAnchor="middle">= EMPTY CAR</text>
                </g>
                <g transform={`translate(${CW_W + 18} ${CW_H * 0.80})`} opacity={ease(f, at("plus about"), at("plus about") + 8)}>
                  <rect x={0} y={-28} width={250} height={44} rx={22} fill={C.ink} />
                  <text x={125} y={4} fill={C.amber} fontFamily={DISPLAY} fontWeight={700} fontSize={30} textAnchor="middle">+ 40–50% LOAD</text>
                </g>
              </g>
            )}
          </g>

          {/* Balanced tag in Shot 1 */}
          {f < s2 && (
            <g transform="translate(540 1100)" opacity={ease(f, at("almost balances"), at("almost balances") + 8)}>
              <rect x={-190} y={-32} width={380} height={60} rx={30} fill={C.ink} stroke={P.color} strokeWidth={4} />
              <text y={10} fill={P.color} fontFamily={DISPLAY} fontWeight={700} fontSize={40} textAnchor="middle">≈ BALANCED</text>
            </g>
          )}
          {f >= s2 - 6 && f < s3 && (
            <g transform={`translate(${CW_X} ${cwTop - 26})`} opacity={ease(f, s2, s2 + 8)}>
              <rect x={-140} y={-32} width={280} height={42} rx={21} fill={C.ink} />
              <text y={-2} fill={P.color} fontFamily={DISPLAY} fontWeight={700} fontSize={30} textAnchor="middle">COUNTERWEIGHT</text>
            </g>
          )}

          {/* Live weight comparison bars in Shot 3 */}
          {bars > 0 && (() => {
            const sc = 0.078, hc = carLoad * sc * bars, hw = 4875 * sc * bars, base = 1090;
            const top = Math.min(hc, hw), diff = Math.abs(hc - hw), carHeavier = hc > hw;
            return (
              <g>
                <rect x={45} y={base - 560} width={175} height={615} rx={16} fill={C.ink} opacity={0.85} />
                <rect x={64} y={base - hc} width={56} height={hc} rx={8} fill={C.paper} />
                <rect x={140} y={base - hw} width={56} height={hw} rx={8} fill={P.color} />
                <rect x={carHeavier ? 64 : 140} y={base - top - diff} width={56} height={diff} rx={8} fill={C.amber} />
                <line x1={55} x2={205} y1={base - top} y2={base - top} stroke={C.dim} strokeWidth={3} strokeDasharray="10 10" />
                <Label x={92} y={base + 40} text="CAR" size={30} />
                <Label x={168} y={base + 40} text="CW" size={30} color={P.color} />
              </g>
            );
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
      {f < s2 && <TitleHook t={["THE ELEVATOR THAT", "BARELY LIFTS", "YOU"]} top={278} o={titleO} />}
    </>
  );
};

/** Screen-space verdict pills + Washington Monument real-photo ProofCard in Shot 5. */
const RigHud: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s3 = at("So the motor"), s4 = at("Here's the strange"), s5 = at("That's why a"), stamp = at("That's the mechanism");
  const full = at("car is full"), empty = at("nearly empty"), rise = at("It would rise"), fd = at("fights the difference"), office = at("full office");
  const carHeavier = f >= full && f < empty;
  return (
    <>
      <Stage>
        {f >= fd && f < s4 && <Pill x={540} y={1152} w={580} text={carHeavier ? "MOTOR HELPS IT UP" : f > empty + 10 ? "MOTOR HOLDS IT BACK" : "MOTOR = DIFFERENCE"} color={C.amber} s={pop(f, fd, fps)} />}
        {f >= at("wouldn't fall") && f < s5 && <Pill x={540} y={1152} w={540} text={f >= rise ? "EMPTY CAR RISES" : "IT WOULDN'T FALL"} color={f >= rise ? C.amber : C.paper} s={pop(f, at("wouldn't fall"), fps)} icon={f >= rise ? ArrowUp : undefined} />}
        {f >= s5 && f < office && <Pill x={540} y={1152} w={680} text="SMALL MOTOR · FULL OFFICE" color={P.color} s={pop(f, at("modest motor"), fps)} icon={Zap} />}
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
        <rect x={-210} y={-350} width={420} height={700} rx={36} fill={C.ink2} stroke={win > 0.5 ? C.green : C.line} strokeWidth={win > 0.5 ? 8 : 4} />
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
        <rect x={-210} y={-350} width={420} height={700} rx={36} fill={C.ink2} stroke={strike > 0.5 ? C.red : C.line} strokeWidth={4} />
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
        { at: s2, kind: "glide", s: 1.18, x: -120, y: 20 },
        { at: at("It's built"), kind: "push", s: 1.24, x: -165, y: 20 },
        { at: at("plus about"), kind: "glide", s: 1.18, x: -140, y: -20 },
        { at: s3, kind: "pull", s: 0.94, x: 0, y: 15 },
        { at: at("fights the difference"), kind: "punch", s: 1.12, x: 0, y: -40 }, // r5 cadence: 14.8-18.9 s gap
        { at: full, kind: "push", s: 1.02, x: 0, y: 0 },
        { at: empty, kind: "punch", s: 1.16, x: -120, y: 20 }, // r5 cadence: new visual state inside the 19.9-24.3 s gap
        { at: at("heavier side"), kind: "glide", s: 1.06, x: 50, y: 20 },
        { at: s4, kind: "push", s: 1.24, x: 40, y: 130 },
        { at: rise - 2, kind: "punch", s: 1.04, x: 10, y: 40 },
        { at: s5, kind: "glide", s: 1.02, x: 0, y: 10 },
        { at: at("full office"), kind: "pull", s: 1.0, x: 0, y: 0 },
      ]} hud={<RigHud />}><Rig /></Shot>
      <Shot from={fin} to={loop} inT="push" outT="whip" cam={[{ at: fin, kind: "push", s: 1.02, dur: 40 }]}><ScaleNotCrane /></Shot>
    </EpisodeShell>
  );
};
