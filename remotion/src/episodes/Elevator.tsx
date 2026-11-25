import React from "react";
import { useVideoConfig } from "remotion";
import words from "../02-elevator.captions.json";
import { C, DISPLAY, EpisodeShell, Label, LOOP_FRAMES, PILLARS, Pill, Shot, Stage, cue, ease, keyed, makeAt, pop, useG } from "../brand";

const P = PILLARS.eng;
const SX = 540, SY = 430, SR = 120;
const CAR_X = SX - SR, CW_X = SX + SR;
const CAR_W = 270, CAR_H = 270, CW_W = 130, CW_H = 230, SUM = 1350;

const Person: React.FC<{ x: number; y: number; c: string; s?: number }> = ({ x, y, c, s = 1 }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    <circle cy={-46} r={15} fill={c} />
    <rect x={-17} y={-28} width={34} height={56} rx={14} fill={c} />
  </g>
);

/** The persistent subject: the whole traction rig. Depends only on useG() (also used frozen at frame 0 for the loop). */
const Rig: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s2 = at("On the other side"), s3 = at("So the motor"), s4 = at("Here's the strange"), s5 = at("That's why a"), stamp = at("That's the mechanism");
  const full = at("car is full"), empty = at("nearly empty"), holds = at("holds it back"), rel = at("Release"), rise = at("It would rise");
  let carTop = keyed(f, [[0, 830], [80, 610], [full, 610], [full + 50, 560], [empty, 560], [holds + 20, 780], [rise - 14, 780], [rise + 26, 530], [s5, 530], [s5 + 20, 700]]);
  if (f >= s5 + 20 && f < stamp) carTop = 700 + Math.sin((f - s5 - 20) / 14) * 140;
  const cwTop = SUM - carTop;
  // people enter one by one (motion every beat)
  const people = f < full ? 3 : f < empty ? Math.min(8, 3 + Math.floor((f - full) / 3)) : f < s4 ? 1 : f < s5 ? 0 : Math.min(6, Math.floor((f - s5) / 4));
  const brakeOpen = ease(f, rel + 4, rel + 14);
  const showBrake = f >= s4 - 6 && f < s5;
  const cwSplit = f >= s2 && f < s3 ? ease(f, at("It's built"), at("It's built") + 10) : 0;
  const bars = f >= s3 && f < s4 ? ease(f, s3, s3 + 10) : 0;
  const carLoad = f < full ? 3300 + 3 * 175 : f < empty ? 6800 : 3300 + 175;
  const motorOn = f >= s5 && f < stamp;
  const cwLit = f >= at("almost balances");
  return (
    <Stage>
      <rect x={CAR_X - CAR_W / 2 - 24} y={SY} width={CW_X + CW_W / 2 - CAR_X + CAR_W / 2 + 48} height={1115 - SY} rx={20} fill={C.ink2} stroke={C.line} strokeWidth={3} opacity={0.85} />
      {/* rails */}
      {[CAR_X - CAR_W / 2 - 8, CW_X + CW_W / 2 + 8].map((x) => <line key={x} x1={x} x2={x} y1={SY + 20} y2={1100} stroke={C.line} strokeWidth={4} strokeDasharray="14 10" />)}
      <line x1={CAR_X} y1={SY} x2={CAR_X} y2={carTop} stroke={C.paper} strokeWidth={8} />
      <line x1={CW_X} y1={SY} x2={CW_X} y2={cwTop} stroke={C.paper} strokeWidth={8} />
      <rect x={SX + 165} y={SY - 70} width={180} height={110} rx={16} fill={motorOn ? P.color : C.ink3} stroke={P.color} strokeWidth={4} />
      <text x={SX + 255} y={SY - 3} fill={motorOn ? C.ink : C.paper} fontFamily={DISPLAY} fontWeight={700} fontSize={34} textAnchor="middle">MOTOR</text>
      <line x1={SX} y1={SY} x2={SX + 165} y2={SY - 15} stroke={C.line} strokeWidth={10} />
      <g transform={`translate(${SX} ${SY}) rotate(${-carTop * 0.9})`}>
        <circle r={SR + 8} fill="none" stroke={C.paper} strokeWidth={8} strokeDasharray={`${Math.PI * (SR + 8)} 9999`} transform="rotate(180)" />
        <circle r={SR} fill={C.ink3} stroke={C.line} strokeWidth={6} />
        {[0, 60, 120, 180, 240, 300].map((a) => <line key={a} x1={0} y1={0} x2={SR - 10} y2={0} stroke={C.line} strokeWidth={10} transform={`rotate(${a})`} />)}
        <circle r={26} fill={C.line} />
      </g>
      {showBrake && [-1, 1].map((d) => (
        <g key={d} transform={`translate(${SX} ${SY}) rotate(${d * 35 - 90})`}>
          <rect x={SR + 14 + brakeOpen * 40} y={-30} width={36} height={60} rx={8} fill={brakeOpen > 0.5 ? C.dim : C.red} />
        </g>
      ))}
      {showBrake && <Label x={SX - SR - 50} y={SY - 40} anchor="end" text={brakeOpen > 0.5 ? "BRAKE OFF" : "BRAKE ON"} size={38} color={brakeOpen > 0.5 ? C.amber : C.red} />}
      <g transform={`translate(${CAR_X - CAR_W / 2} ${carTop})`}>
        <rect width={CAR_W} height={CAR_H} rx={18} fill={C.ink3} stroke={C.paper} strokeWidth={6} />
        <line x1={CAR_W / 2} y1={20} x2={CAR_W / 2} y2={CAR_H - 10} stroke={C.line} strokeWidth={4} />
        {Array.from({ length: people }).map((_, i) => (
          <Person key={i} x={40 + (i % 4) * 63} y={CAR_H - 30 - Math.floor(i / 4) * 95} c={i % 3 === 0 ? C.amber : "#D7D2C6"} />
        ))}
        <text x={CAR_W / 2} y={-14} fill={C.paper} fontFamily={DISPLAY} fontWeight={700} fontSize={30} textAnchor="middle" opacity={0.85}>CAR</text>
      </g>
      <g transform={`translate(${CW_X - CW_W / 2} ${cwTop})`}>
        <rect width={CW_W} height={CW_H} rx={12} fill={cwLit ? P.color : C.line} opacity={cwLit ? 1 : 0.7} />
        {Array.from({ length: 6 }).map((_, i) => <line key={i} x1={10} x2={CW_W - 10} y1={(i + 1) * (CW_H / 7)} y2={(i + 1) * (CW_H / 7)} stroke={C.ink} strokeWidth={3} opacity={0.35} />)}
        {cwSplit > 0 && (
          <g opacity={cwSplit}>
            <rect y={CW_H * 0.62} width={CW_W} height={CW_H * 0.38} rx={12} fill={C.amber} />
            <Label x={CW_W + 24} y={CW_H * 0.3 + 12} text="= EMPTY CAR" anchor="start" size={34} color={P.color} />
            <Label x={CW_W + 24} y={CW_H * 0.81 + 12} text="+ 40–50%" anchor="start" size={34} color={C.amber} o={ease(f, at("plus about"), at("plus about") + 8)} />
            <Label x={CW_W + 24} y={CW_H * 0.81 + 50} text="OF RATED LOAD" anchor="start" size={30} weight={500} color={C.amber} o={ease(f, at("rated load"), at("rated load") + 8)} />
          </g>
        )}
      </g>
      {f < s2 && <Label x={SX} y={1150} text="≈ BALANCED" size={64} color={P.color} o={ease(f, at("almost balances"), at("almost balances") + 8)} />}
      {f >= s2 - 8 && f < s3 && <Label x={CW_X + 40} y={cwTop - 24} text="COUNTERWEIGHT" size={32} color={P.color} o={ease(f, s2, s2 + 10)} />}
      {bars > 0 && (() => {
        const sc = 0.085, hc = carLoad * sc * bars, hw = 4875 * sc * bars, base = 1110;
        const top = Math.min(hc, hw), diff = Math.abs(hc - hw), carHeavier = hc > hw;
        return (
          <g>
            <rect x={60} y={base - hc} width={60} height={hc} rx={8} fill={C.paper} opacity={0.85} />
            <rect x={140} y={base - hw} width={60} height={hw} rx={8} fill={P.color} />
            <rect x={carHeavier ? 60 : 140} y={base - top - diff} width={60} height={diff} rx={8} fill={C.amber} />
            <line x1={50} x2={210} y1={base - top} y2={base - top} stroke={C.dim} strokeWidth={3} strokeDasharray="10 10" />
            <Label x={90} y={base + 44} text="CAR" size={30} />
            <Label x={170} y={base + 44} text="CW" size={30} color={P.color} />
          </g>
        );
      })()}
      {f >= rise - 6 && f < s5 && (
        <g transform={`translate(${CAR_X} ${carTop + CAR_H + 90}) scale(${pop(f, rise - 4, fps)})`}>
          <text fill={C.amber} fontFamily={DISPLAY} fontWeight={700} fontSize={110} textAnchor="middle">↑</text>
        </g>
      )}
    </Stage>
  );
};

/** Screen-space verdict pills (not affected by camera punches). */
const RigHud: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s3 = at("So the motor"), s4 = at("Here's the strange"), s5 = at("That's why a"), stamp = at("That's the mechanism");
  const full = at("car is full"), empty = at("nearly empty"), rise = at("It would rise"), fd = at("fights the difference");
  const carHeavier = f >= full && f < empty;
  return (
    <Stage>
      {f >= fd && f < s4 && <Pill x={SX} y={1150} w={580} text={carHeavier ? "MOTOR HELPS IT UP" : f > empty + 10 ? "MOTOR HOLDS IT BACK" : "MOTOR = DIFFERENCE"} color={C.amber} s={pop(f, fd, fps)} />}
      {f >= at("wouldn't fall") && f < s5 && <Pill x={SX} y={1150} w={540} text={f >= rise ? "EMPTY CAR RISES" : "IT WOULDN'T FALL"} color={f >= rise ? C.amber : C.paper} s={pop(f, at("wouldn't fall"), fps)} />}
      {f >= s5 && f < stamp && <Pill x={SX} y={1150} w={620} text="SMALL MOTOR · FULL OFFICE" color={P.color} s={pop(f, at("modest motor"), fps)} />}
      {f >= s3 && f < fd && null}
    </Stage>
  );
};

const ScaleNotCrane: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const fin = at("An elevator is a"), sc = at("a scale"), cr = at("not a crane");
  return (
    <Stage>
      <g transform={`translate(300 700) scale(${0.85 + 0.15 * pop(f, sc, fps)})`} opacity={ease(f, fin - 6, fin + 2)}>
        <polygon points="0,-10 -40,170 40,170" fill={P.color} />
        <g transform={`rotate(${Math.sin(f / 10) * 4})`}>
          <rect x={-190} y={-22} width={380} height={18} rx={9} fill={C.paper} />
          <rect x={-210} y={-110} width={80} height={90} rx={10} fill={C.ink3} stroke={C.paper} strokeWidth={4} />
          <rect x={140} y={-100} width={50} height={80} rx={8} fill={P.color} />
        </g>
        <Label x={0} y={250} text="SCALE ✓" size={56} color={C.green} />
      </g>
      <g transform={`translate(790 700) scale(${pop(f, cr, fps)})`}>
        <rect x={-12} y={-170} width={24} height={340} fill={C.dim} />
        <rect x={-150} y={-180} width={240} height={20} fill={C.dim} />
        <line x1={-130} y1={-160} x2={-130} y2={-20} stroke={C.dim} strokeWidth={5} />
        <rect x={-160} y={-20} width={60} height={50} fill={C.dim} />
        <line x1={-180} y1={-200} x2={130} y2={200} stroke={C.red} strokeWidth={14} strokeLinecap="round" strokeDasharray={600} strokeDashoffset={600 * (1 - ease(f, cr + 4, cr + 12))} />
        <Label x={0} y={250} text="CRANE ✕" size={56} color={C.red} />
      </g>
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
    cue(0, "whoosh", 0.5), cue(at("almost balances"), "pop", 0.8), cue(s2, "whoosh", 0.6), cue(at("It's built"), "clank", 0.6), cue(at("plus about"), "pop", 0.7),
    cue(at("counterweight."), "tick", 0.7), cue(s3, "whoosh", 0.6), cue(at("full weight."), "tick", 0.6), cue(at("helps it up"), "pop", 0.7), cue(at("heavier side"), "tick", 0.7), cue(at("fights the difference"), "pop", 0.8), ...Array.from({ length: 5 }, (_, i) => cue(full + i * 3, "tick", 0.5)), cue(empty + 10, "pop", 0.7),
    cue(s4, "riser", 0.5), cue(rel + 4, "clank", 0.9), cue(rise - 4, "whoosh", 0.9), cue(rise, "pop", 0.9),
    cue(s5, "whoosh", 0.6), cue(at("modest motor"), "pop", 0.8), cue(at("all day long"), "confirm", 0.6),
    cue(at("a scale"), "pop", 0.8), cue(at("not a crane"), "error", 0.7),
  ];
  return (
    <EpisodeShell audio="02-elevator.wav" words={words} pillar={P} ep="002" source="TK ELEVATOR" cardAt={card} cardUntil={fin} cues={cues} hook={<Rig />}
      chapters={[{ at: 0, label: "IT ALMOST BALANCES" }, { at: s2, label: "THE COUNTERWEIGHT" }, { at: s3, label: "ONLY THE DIFFERENCE" }, { at: s4, label: "THE STRANGE PART" }, { at: s5, label: "WHY IT'S CHEAP" }]}>
      {/* one persistent world; beats are camera moves, not slides */}
      <Shot from={0} to={card} inT="none" outT="push" cam={[
        { at: 20, kind: "push", s: 1.06, y: 30 },
        { at: s2, kind: "glide", s: 1.18, x: -150, y: 40 },          // to the counterweight
        { at: at("hangs a"), kind: "push", s: 1.23, x: -190, y: 50 },
        { at: at("It's built"), kind: "push", s: 1.28, x: -230, y: 60 },
        { at: at("plus about"), kind: "glide", s: 1.22, x: -200, y: -10 },
        { at: at("rated load"), kind: "pull", s: 1.1, x: -110, y: 30 },
        { at: s3, kind: "pull", s: 0.92, x: 0, y: 30 },              // context for the bars
        { at: at("full weight."), kind: "glide", s: 0.95, x: 0, y: 10 },
        { at: full, kind: "push", s: 1.0, y: 0 },
        { at: at("heavier side"), kind: "glide", s: 1.06, x: 60, y: 20 },
        { at: s4, kind: "push", s: 1.22, x: 60, y: 160 },            // brake close-up
        { at: rise - 2, kind: "punch", s: 1.0, x: 0, y: 40 },        // reveal: it rises (pull out fast)
        { at: s5, kind: "glide", s: 1.04, y: 0 },
        { at: at("all day long"), kind: "push", s: 1.1, x: 0, y: 40 },
      ]} hud={<RigHud />}><Rig /></Shot>
      <Shot from={fin} to={loop} inT="push" outT="whip" cam={[{ at: fin, kind: "push", s: 1.05, dur: 40 }]}><ScaleNotCrane /></Shot>
    </EpisodeShell>
  );
};
