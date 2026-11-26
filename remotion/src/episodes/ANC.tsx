import React from "react";
import { useVideoConfig } from "remotion";
import words from "../05-anc-headphones.captions.json";
import { VolumeX, Zap, ShieldCheck } from "lucide-react";
import { C, EASE, EpisodeShell, LabeledBox, Lane, LOOP_FRAMES, Pill, PILLARS, Shot, Stage, TagLabel, TitleHook, cue, ease, makeAt, pop, popOpacity, popScale, reveal, squash, stagger, useG } from "../brand";

const P = PILLARS.sci;
// full-bleed drawn world (no card): waves are light on the dusk backdrop, each with an ink underlay for contrast
const NOISE = "#A99BFF", ANTI = C.amber, FLAT = C.green, SHELL = C.ink3, PAD = "#6B7088";
const W = 1080;
const clamp = (v: number, a = 0, b = 1) => Math.min(b, Math.max(a, v));

const jet = (x: number, f: number) => Math.sin(x / 34 - f * 0.34) + 0.45 * Math.sin(x / 15 + 1 - f * 0.5);
const sine = (x: number, f: number) => Math.sin(x / 38 - f * 0.3);
const line = (x0: number, x1: number, y: number, fn: (x: number) => number, step = 5) => {
  const p: string[] = [];
  const e = Math.max(x1, x0 + step);
  for (let x = x0; x <= e; x += step) p.push(`${x},${y + fn(x)}`);
  return `M${p.join("L")}`;
};
/** Ramp for badge entrances: slow enough that TagLabel's built-in pop (0.62x -> overshoot -> 1x) is visible. */
const pp = (f: number, at: number, dur = 14) => ease(f, at, at + dur);

/** A wave stroke with a dark underlay so it reads on the drawn backdrop. */
const Wave: React.FC<{ d: string; color: string; w?: number; o?: number; dash?: string; off?: number }> = ({ d, color, w = 11, o = 1, dash, off }) => (
  <g opacity={o}>
    <path d={d} stroke={C.ink} strokeWidth={w + 9} opacity={0.55} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={dash} strokeDashoffset={off} />
    <path d={d} stroke={color} strokeWidth={w} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={dash} strokeDashoffset={off} />
  </g>
);

/** Drifting air motes: the one continuous world that every beat shares (replaces the card). */
const Air: React.FC<{ f: number }> = ({ f }) => (
  <g>
    {Array.from({ length: 18 }, (_, i) => {
      const x = ((i * 173 + f * (1.4 + (i % 3) * 0.6)) % 1180) - 50, y = 360 + ((i * 131) % 720) + 14 * Math.sin(f / 18 + i);
      return <circle key={i} cx={x} cy={y} r={4 + (i % 3) * 2} fill={C.paper} opacity={0.2} />;
    })}
  </g>
);

/** Side-view ear cup (head on the right). mic/spk 0..1 glow the outside microphone / inside speaker. */
const Cup: React.FC<{ x: number; y: number; s?: number; mic?: number; spk?: number; band?: boolean }> = ({ x, y, s = 1, mic = 0, spk = 0, band = true }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    {band && <path d="M0,-170 C0,-290 150,-310 235,-240" stroke={C.ink} strokeWidth={26} fill="none" strokeLinecap="round" />}
    <rect x={52} y={-128} width={58} height={256} rx={29} fill={PAD} stroke={C.ink} strokeWidth={6} />
    <rect x={-70} y={-170} width={132} height={340} rx={50} fill={SHELL} stroke={C.paper} strokeWidth={5} />
    <rect x={-44} y={-20} width={80} height={14} rx={7} fill={P.color} opacity={0.9} />
    <rect x={-44} y={14} width={80} height={14} rx={7} fill={P.color} opacity={0.6} />
    {mic > 0 && <circle cx={-70} cy={-96} r={20 + 26 * mic} fill={C.amber} opacity={0.35 * mic} />}
    <circle cx={-70} cy={-96} r={17} fill={C.amber} stroke={C.ink} strokeWidth={4} />
    {spk > 0 && <circle cx={46} cy={70} r={22 + 22 * spk} fill={C.amber} opacity={0.4 * spk} />}
    <circle cx={46} cy={70} r={18} fill={C.amber} stroke={C.ink} strokeWidth={4} />
  </g>
);

const Ear: React.FC<{ x: number; y: number; s?: number }> = ({ x, y, s = 1 }) => (
  <g transform={`translate(${x} ${y}) scale(${s})`}>
    <ellipse rx={44} ry={78} fill="#F2C9A5" stroke={C.ink} strokeWidth={6} />
    <path d="M-12,-40 C20,-52 30,-6 4,6 C-14,14 -10,40 8,44" fill="none" stroke="#C99A78" strokeWidth={8} strokeLinecap="round" />
  </g>
);

const Jet: React.FC<{ x: number; y: number; o?: number }> = ({ x, y, o = 1 }) => (
  <g transform={`translate(${x} ${y})`} opacity={o}>
    <ellipse rx={78} ry={20} fill={C.ink} stroke={C.paper} strokeWidth={3} />
    <polygon points="-14,0 28,0 -42,-56" fill={C.ink3} stroke={C.paper} strokeWidth={3} />
    <polygon points="-14,0 28,0 -42,56" fill={C.ink3} stroke={C.paper} strokeWidth={3} />
    <polygon points="-70,-4 -88,-38 -54,-4" fill={C.ink3} />
    <circle cx={46} cy={-4} r={5} fill={P.color} />
  </g>
);

/** Speaker glyph: cone faces +x (use flip=-1 to face left). */
const Spk: React.FC<{ x: number; y: number; s?: number; flip?: number; f: number; arcs?: boolean }> = ({ x, y, s = 1, flip = 1, f, arcs = true }) => (
  <g transform={`translate(${x} ${y}) scale(${s * flip} ${s})`}>
    <rect x={-30} y={-34} width={34} height={68} rx={6} fill={C.ink} stroke={C.paper} strokeWidth={3} />
    <polygon points="4,-34 54,-72 54,72 4,34" fill={C.ink3} stroke={C.paper} strokeWidth={4} />
    {arcs && [1, 2].map((k) => <path key={k} d={`M${70 + k * 22},${-24 * k} Q${96 + k * 22},0 ${70 + k * 22},${24 * k}`} stroke={ANTI} strokeWidth={7} fill="none" strokeLinecap="round" opacity={0.5 + 0.5 * Math.sin(f / 3 - k)} />)}
  </g>
);

/** Hook (frame 0, zoomed) and final payoff: noise in from the left, anti-noise from the cup, a flat line reaches the ear. */
const Fight: React.FC<{ final?: boolean }> = ({ final = false }) => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const CX = 520, CY = 840;
  const jetAt = at("A jet engine"), barely = at("barely hear it"), fightAt = at("fight");
  const z = final ? 1 : ease(f, 3, 34, 2.35, 1.0);
  const amp = final ? 1 : ease(f, jetAt - 8, jetAt + 10, 0.55, 1);
  const cancel = final ? ease(f, at("fighting"), at("fighting") + 12) : ease(f, barely - 4, barely + 16);
  const res = amp * (1 - cancel);
  const jetP = final ? 1 : pop(f, jetAt, fps);
  const [sx, sy] = squash(f, final ? at("fighting") : barely, 0.06);
  const aStart = final ? at("sound fighting") : fightAt;
  return (
    <>
      <Stage>
        <g transform={`translate(${CX} ${CY}) scale(${z}) translate(${-CX} ${-CY})`}>
          <Air f={f} />
          <Jet x={190} y={650} o={popOpacity(jetP)} />
          {/* outside noise */}
          <Wave d={line(100, 448, CY, (x) => 96 * amp * jet(x, f))} color={NOISE} w={12} />
          {/* anti-noise leaves the speaker as the fight starts */}
          {(final || f >= fightAt) && (
            <Wave d={line(448, 575, CY + 60, (x) => -60 * amp * jet(x, f) * ease(f, aStart, aStart + 14), 4)} color={ANTI} w={9} o={0.95} />
          )}
          <g transform={`translate(${CX} ${CY}) scale(${sx} ${sy}) translate(${-CX} ${-CY})`}><Cup x={CX} y={CY} mic={0.5 + 0.5 * Math.sin(f / 3)} spk={cancel} /></g>
          {/* what reaches the ear */}
          <Wave d={line(626, 836, CY, (x) => 96 * res * jet(x, f) * 0.6)} color={cancel > 0.7 ? FLAT : NOISE} w={cancel > 0.7 ? 11 : 12} />
          <Ear x={888} y={CY} />
          {!final && f >= jetAt && <TagLabel x={190} y={598 + 6} text="JET ENGINE" size={34} o={pp(f, jetAt)} />}
          {final && <TagLabel x={540} y={1070} text="SOUND VS SOUND" size={40} color={C.amber} o={pp(f, at("sound fighting"))} />}
        </g>
      </Stage>
      {!final && <TitleHook t={["THE HEADPHONES THAT", "FIGHT SOUND", "WITH SOUND"]} top={278} o={ease(f, jetAt + 14, jetAt + 22, 1, 0)} />}
    </>
  );
};

const Mic: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s2 = at("Tiny microphones"), each = at("on each"), listen = at("listen to"), outside = at("noise outside");
  const CX = 640, CY = 740, S = 1.2;
  const pop1 = pop(f, s2 + 2, fps);
  const micG = f > listen ? 0.5 + 0.5 * Math.sin((f - listen) / 2.5) : 0;
  const arcs = [0, 1, 2, 3];
  return (
    <Stage>
      <Air f={f} />
      <g transform={`translate(${CX} ${CY}) scale(${popScale(pop1)})`} opacity={popOpacity(pop1)}><g transform={`translate(${-CX} ${-CY})`}>
        <Cup x={CX} y={CY} s={S} mic={micG} band />
      </g></g>
      {/* sound arcs travelling into the microphone */}
      {arcs.map((i) => {
        const t = ((f - s2 - i * 9) % 36 + 36) % 36 / 36, r = 230 * (1 - t) + 20;
        return <circle key={i} cx={CX - 70 * S} cy={CY - 96 * S} r={r} fill="none" stroke={NOISE} strokeWidth={9} opacity={0.85 * t * (f > s2 ? 1 : 0)} strokeDasharray="60 38" strokeDashoffset={-f * 3} />;
      })}
      <TagLabel x={110} y={470} text="MICROPHONE" anchor="start" size={38} color={C.amber} o={pp(f, each)} />
      <line x1={300} y1={510} x2={ease(f, each, each + 12, 300, CX - 70 * S - 30)} y2={ease(f, each, each + 12, 510, CY - 96 * S - 18)} stroke={C.amber} strokeWidth={6} strokeDasharray="12 10" opacity={ease(f, each, each + 6)} />
      {/* scope: what the mic hears */}
      <rect x={110} y={990} width={860} height={110} rx={24} fill={C.ink} stroke={P.color} strokeWidth={3} opacity={ease(f, listen, listen + 8) * 0.92} />
      <path d={line(130, 950, 1045, (x) => 34 * jet(x, f), 6)} stroke={P.color} strokeWidth={8} fill="none" strokeLinecap="round" opacity={ease(f, listen + 2, listen + 10)} />
      <TagLabel x={110} y={950} text="THE NOISE, SAMPLED" anchor="start" size={34} color={C.paper} o={pp(f, outside - 6)} />
    </Stage>
  );
};

const Flip: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const chip = at("A chip"), flips = at("flips that"), ud = at("upside down"), peak = at("every peak"), plays = at("plays it"), ear = at("into your ear");
  const fl = ease(f, ud, ud + 14);                // 0 = copy, 1 = inverted
  const sgn = 1 - 2 * fl;
  const Y1 = 500, Y2 = 880, A = 78, CPX = 880, CPY = 660, CS = 0.85, SPX = 700;
  const cp = pop(f, chip, fps), [csx, csy] = squash(f, flips, 0.08);
  const copyIn = ease(f, flips, flips + 10);
  const travel = ease(f, plays, plays + 18);
  const sp = pop(f, plays + 6, fps), ep = pop(f, ear, fps);
  const peaks: number[] = [];
  for (let k = -2; k < 20; k++) { const x = 38 * (Math.PI / 2 + 2 * Math.PI * k + f * 0.3); if (x > 150 && x < 560) peaks.push(x); }
  return (
    <Stage>
      <Air f={f} />
      <Wave d={line(110, 620, Y1, (x) => A * sine(x, f))} color={NOISE} />
      <TagLabel x={110} y={Y1 - 120} text="NOISE" anchor="start" size={36} color="#CFC8FF" o={pp(f, 4)} />
      {/* chip */}
      <g transform={`translate(${CPX} ${CPY}) scale(${popScale(cp) * csx * CS} ${popScale(cp) * csy * CS})`} opacity={popOpacity(cp)}>
        <rect x={-62} y={-62} width={124} height={124} rx={22} fill={C.ink} stroke={C.amber} strokeWidth={6} />
        {[-36, -12, 12, 36].map((p) => <g key={p}><rect x={p - 5} y={-84} width={10} height={22} fill={C.amber} /><rect x={p - 5} y={62} width={10} height={22} fill={C.amber} /></g>)}
        <Zap x={-30} y={-30} width={60} height={60} color={C.amber} strokeWidth={3} />
      </g>
      <LabeledBox box={{ x: CPX - 53, y: CPY - 71, w: 106, h: 142 }} side="top" gap={46} label="CHIP" size={36} color={C.amber} o={pp(f, chip + 4)} />
      <path d={`M620,${Y1} C720,${Y1} 760,${CPY} ${CPX - 53},${CPY}`} stroke={NOISE} strokeWidth={6} strokeDasharray="14 12" strokeDashoffset={-f * 4} fill="none" opacity={ease(f, chip, chip + 10)} />
      {/* copy -> inverted */}
      <Wave d={line(110, 560, Y2, (x) => sgn * A * sine(x, f))} color={ANTI} o={copyIn} />
      <TagLabel x={110} y={Y2 + 130} text="COPY" anchor="start" size={36} color={C.amber} o={copyIn * (1 - ease(f, ud - 8, ud - 2))} />
      <TagLabel x={110} y={Y2 + 130} text="ANTI-NOISE (FLIPPED)" anchor="start" size={36} color={C.amber} o={pp(f, ud)} />
      {/* peak <-> valley links */}
      {peaks.map((x, i) => {
        const s = pop(f, peak + stagger(i, 3, 0.85, 2), fps);
        return (
          <g key={i} opacity={popOpacity(s) * (f >= peak ? 1 : 0)}>
            <line x1={x} y1={Y1 - A} x2={x} y2={Y2 + A} stroke={C.paper} strokeWidth={3} strokeDasharray="8 8" opacity={0.6} />
            <circle cx={x} cy={Y1 - A} r={14 * popScale(s)} fill={NOISE} stroke={C.ink} strokeWidth={4} />
            <circle cx={x} cy={Y2 + A} r={14 * popScale(s)} fill={ANTI} stroke={C.ink} strokeWidth={4} />
          </g>
        );
      })}
      {/* speaker + ear */}
      <path d={`M560,${Y2} L${560 + 110 * travel},${Y2}`} stroke={ANTI} strokeWidth={9} strokeLinecap="round" opacity={ease(f, plays, plays + 4)} />
      <g opacity={popOpacity(sp)}><Spk x={SPX} y={Y2} s={popScale(sp)} f={f} /></g>
      <LabeledBox box={{ x: SPX - 30, y: Y2 - 72, w: 84, h: 144 }} side="bottom" label="SPEAKER" size={36} color={C.amber} o={pp(f, plays + 6)} />
      <g opacity={popOpacity(ep)}><Ear x={940} y={Y2} s={0.8 * popScale(ep)} /></g>
    </Stage>
  );
};

/** Destructive interference as motion: noise travels right, anti-noise travels left, they meet at the ear and merge into a flat line. */
const Sum: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const meet = at("When the waves"), flat = at("flat."), di = at("destructive");
  const Y = 820, EX = 540, A = 62, XN0 = 110, XA0 = 830;
  const m = flat - 6;                                   // the instant the fronts reach the ear
  const p = ease(f, meet + 4, m, 0, 1);
  const nF = XN0 + (EX - 52 - XN0) * p, aF = XA0 - (XA0 - (EX + 52)) * p;
  const R = ease(f, m, m + 26, -60, 470);               // flat zone grows outward from the ear
  const amp = (x: number) => clamp((Math.abs(x - EX) - R) / 60);
  const noise = (x: number) => A * amp(x) * Math.sin((x - EX) / 38 - f * 0.3);
  const anti = (x: number) => A * amp(x) * Math.sin((x - EX) / 38 + f * 0.3);
  const vis = ease(f, meet - 4, meet + 8);
  const merged = f >= m;
  const fx0 = Math.max(XN0, EX - Math.max(0, R)), fx1 = Math.min(XA0, EX + Math.max(0, R));
  const [sx, sy] = squash(f, m, 0.12);
  const jp = pop(f, meet - 6, fps);
  return (
    <Stage>
      <Air f={f} />
      <g opacity={popOpacity(jp)}><Jet x={170} y={520} /></g>
      <LabeledBox box={{ x: 82, y: 464, w: 166, h: 112 }} side="bottom" label="NOISE" size={34} color="#CFC8FF" o={pp(f, meet - 4)} />
      <g transform={`translate(880 ${Y}) scale(${sx} ${sy}) translate(-880 ${-Y})`} opacity={vis}><Spk x={880} y={Y} flip={-1} f={f} arcs={false} /></g>
      <LabeledBox box={{ x: 826, y: Y - 72, w: 84, h: 144 }} side="top" gap={46} label="ANTI-NOISE" size={34} color={C.amber} o={pp(f, meet + 2)} />
      <Wave d={line(XN0, nF, Y, noise)} color={NOISE} o={vis} />
      <Wave d={line(aF, XA0, Y, anti)} color={ANTI} o={vis} />
      {merged && <Wave d={`M${fx0},${Y} L${fx1},${Y}`} color={FLAT} w={14 + 8 * Math.exp(-(f - m) / 5)} />}
      {/* shockwave rings at the cancellation moment */}
      {merged && [0, 1, 2].map((k) => (
        <circle key={k} cx={EX} cy={Y} r={ease(f, m + 4 * k, m + 4 * k + 20, 50, 190 + 50 * k)} fill="none" stroke={FLAT} strokeWidth={8 - 2 * k} opacity={ease(f, m + 4 * k, m + 4 * k + 20, 0.9, 0)} />
      ))}
      <g transform={`translate(${EX} ${Y}) scale(${sx} ${sy}) translate(${-EX} ${-Y})`}><Ear x={EX} y={Y} s={1.1} /></g>
      <TagLabel x={540} y={1086} text="DESTRUCTIVE INTERFERENCE" size={40} color={C.amber} o={pp(f, di - 4)} />
    </Stage>
  );
};

/** Steady rumble: the chip learns the pattern, so the dashed prediction lands exactly on the real wave. */
const Steady: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const s5 = at("It works best"), eng = at("engines"), vent = at("ventilation"), rep = at("they repeat"), pred = at("predict");
  const Y = 760, NOWX = 560, A = 100, L = 78;
  const w = (x: number) => A * Math.sin(x / L - f * 0.16);
  const k = ease(f, s5, s5 + 14);
  const period = 2 * Math.PI * L;
  const st = at("steady,"), r1 = ease(f, st, st + 10), r2 = ease(f, vent, vent + 10), pdash = ease(f, pred - 4, pred + 8);
  const [e1, e2] = [pop(f, eng, fps), pop(f, vent + 6, fps)];
  return (
    <Stage>
      <Air f={f} />
      <Wave d={line(100, NOWX, Y, w)} color={NOISE} w={12} o={k} />
      <Wave d={line(NOWX, 960, Y, w)} color={ANTI} w={10} dash="22 16" off={-f * 2} o={pdash} />
      <path d={line(NOWX, 960, Y, w)} stroke={NOISE} strokeWidth={8} fill="none" strokeLinecap="round" strokeDasharray="2 14" opacity={0.55 * k * (1 - pdash)} />
      <line x1={NOWX} y1={Y - 190} x2={NOWX} y2={Y + 190} stroke={C.paper} strokeWidth={5} opacity={k} />
      <TagLabel x={NOWX} y={Y - 214} text="NOW" size={34} color={C.paper} o={pp(f, s5 + 2)} />
      {/* one period highlighted, then its twin */}
      <g>
        <rect x={100} y={Y - 150} width={period * 0.5} height={300} rx={18} fill={NOISE} opacity={0.3 * r1} />
        <rect x={100 + period * 0.5 + 12} y={Y - 150} width={period * 0.5} height={300} rx={18} fill={NOISE} opacity={(0.3 + 0.1 * Math.sin(f / 4)) * r2} />
      </g>
      <TagLabel x={110} y={Y + 236} text="REPEATS" anchor="start" size={38} color={C.paper} o={pp(f, rep)} />
      <Lane x={223} y={390} dir="right" gap={64} items={[
        { w: 240, h: 76, node: <Pill x={120} y={38} w={240} text="ENGINES" color={C.paper} s={e1} /> },
        { w: 330, h: 76, node: <Pill x={165} y={38} w={330} text="VENTILATION" color={C.paper} s={e2} /> },
      ]} />
      <TagLabel x={780} y={Y + 236} text="PREDICTED" size={38} color={C.amber} anchor="middle" o={pp(f, pred - 4)} />
    </Stage>
  );
};

/** A clap: the real wave jumps, the prediction misses, the cushions stop it physically. */
const Clap: React.FC = () => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const clap = at("clap"), fast = at("too fast"), block = at("have to block");
  const Y = 760, NOWX = 560, L = 78;
  const calm = (x: number) => 100 * Math.sin(x / L - f * 0.16);
  const hit = f >= clap;
  const burst = ease(f, clap, clap + 6);
  const noisy = (x: number) => (hit ? calm(x) * (1 - burst) + burst * (150 * Math.sin(x / 9 + f * 0.9) * Math.sin(x / 41 + f * 0.31) + 40 * Math.sin(x / 4 - f * 1.3)) : calm(x));
  const cushion = EASE.OUT(Math.min(1, Math.max(0, (f - block + 2) / 16)));
  const stopX = 560 - 10;
  const cx = 1000 + (NOWX - 36 - 1000) * cushion;
  const miss = pp(f, fast);
  const [csx, csy] = squash(f, block + 12, 0.14);
  return (
    <Stage>
      <Air f={f} />
      <Wave d={line(100, 960, Y, calm)} color={ANTI} w={10} dash="22 16" off={-f * 2} o={0.9} />
      <Wave d={line(100, cushion > 0.5 ? stopX : 960, Y, noisy, 4)} color={NOISE} w={12} />
      <line x1={NOWX} y1={Y - 190} x2={NOWX} y2={Y + 190} stroke={C.paper} strokeWidth={5} />
      {/* clap burst */}
      {hit && f < clap + 26 && [0, 1, 2, 3, 4].map((i) => {
        const a = -0.9 + i * 0.45, r0 = 30 + (f - clap) * 9;
        return <line key={i} x1={300 + Math.cos(a) * r0} y1={520 + Math.sin(a) * r0} x2={300 + Math.cos(a) * (r0 + 46)} y2={520 + Math.sin(a) * (r0 + 46)} stroke={C.paper} strokeWidth={9} strokeLinecap="round" opacity={ease(f, clap + 10, clap + 26, 1, 0)} />;
      })}
      {hit && [0, 1, 2].map((k) => <circle key={k} cx={300} cy={520} r={ease(f, clap + 3 * k, clap + 3 * k + 18, 30, 150 + 40 * k)} fill="none" stroke={C.paper} strokeWidth={6} opacity={ease(f, clap + 3 * k, clap + 3 * k + 18, 0.8, 0)} />)}
      <TagLabel x={300} y={620} text="CLAP" size={40} color={C.paper} o={pp(f, clap)} />
      {miss > 0 && <TagLabel x={740} y={Y - 214} text="MISSED!" size={36} color={C.paper} o={miss * (cushion > 0.3 ? 0 : 1)} />}
      {/* cushion slides in, squashes on impact and stops the sound */}
      <g transform={`translate(${cx} ${Y}) scale(${csx} ${csy})`} opacity={popOpacity(cushion)}>
        <rect x={-34} y={-200} width={68} height={400} rx={34} fill={PAD} stroke={C.paper} strokeWidth={5} />
        <rect x={-34} y={-200} width={68} height={400} rx={34} fill="none" stroke={C.paper} strokeWidth={3} strokeDasharray="4 18" opacity={0.7} />
      </g>
      <TagLabel x={560} y={Y + 262} text="CUSHIONS BLOCK IT" size={38} color={C.paper} o={pp(f, block)} />
    </Stage>
  );
};

const Verdict: React.FC<{ phrase: string; until?: string; text: string; color: string; w?: number; icon?: React.ComponentProps<typeof Pill>["icon"] }> = ({ phrase, until, text, color, w = 440, icon }) => {
  const f = useG();
  const { fps } = useVideoConfig();
  const at = makeAt(words, fps);
  const a = at(phrase), u = until ? at(until) : 1e9;
  if (f < a || f > u + 6) return null;
  return <Stage><Pill x={W / 2} y={1152} w={w} text={text} color={color} icon={icon} s={pop(f, a, fps) * ease(f, u, u + 6, 1, 0)} /></Stage>;
};

export const ANCVideo: React.FC = () => {
  const { fps, durationInFrames: D } = useVideoConfig();
  const at = makeAt(words, fps);
  const s2 = at("Tiny microphones"), s3 = at("A chip"), s4 = at("When the waves"), s5 = at("It works best"), s6 = at("A sudden clap"),
    card = at("That's the mechanism"), fin = at("So the quiet"), loop = D - LOOP_FRAMES;
  const jetAt = at("A jet engine"), barely = at("barely hear it"), listen = at("listen to"), flips = at("flips that"), ud = at("upside down"), peak = at("every peak"),
    plays = at("plays it"), ear = at("into your ear"), plus = at("peak plus"), flat = at("flat."), di = at("destructive"),
    engines = at("engines"), vent = at("ventilation"), rep = at("they repeat"), pred = at("predict"), clap = at("clap"), fast = at("too fast"), block = at("have to block"), fight = at("fight");
  const cues = [
    cue(4, "swish", 0.92), cue(fight, "pop", 0.92), cue(jetAt, "thud", 0.92), cue(barely, "confirm", 0.92),
    cue(s2 - 5, "whoosh", 0.95), cue(s2 + 6, "pop", 0.92), cue(listen, "click", 0.95), cue(at("noise outside"), "tick", 0.92),
    cue(s3 - 5, "whoosh", 0.95), cue(s3 + 2, "pop", 0.92), cue(flips, "click", 0.95), cue(ud, "pop3", 0.92), cue(peak, "tick", 0.92), cue(plays + 6, "pop", 0.92), cue(ear, "confirm", 0.92),
    cue(s4 - 5, "whoosh", 0.95), cue(plus, "tick", 0.92), cue(flat, "confirm", 0.95), ...reveal(di, 0.7),
    cue(s5 - 5, "whoosh", 0.95), cue(engines, "pop", 0.92), cue(vent, "pop", 0.92), cue(rep, "tick", 0.92), cue(pred, "confirm", 0.92),
    cue(s6 - 5, "whoosh", 0.95), cue(clap, "thud", 0.95), cue(clap + 3, "error", 0.9), cue(fast, "glitch", 0.9), cue(block, "tick", 0.95),
    cue(at("sound fighting"), "pop", 0.92),
  ];
  return (
    <EpisodeShell audio="05-anc-headphones.wav" words={words} pillar={P} ep="005" source="SCIENCE FOCUS · WIKIPEDIA"
      backdrop="library/anc_dusk.jpg" backdropDim={0.42} microGap={36}
      cardAt={card} cardUntil={fin} cues={cues} hook={<Fight />}
      chapters={[{ at: 0, label: "SOUND VS SOUND" }, { at: s2, label: "THE MICROPHONE" }, { at: s3, label: "THE FLIP" }, { at: s4, label: "THE SUM" }, { at: s5, label: "WHAT IT CAN DO" }]}>
      <Shot from={0} to={s2} inT="none" outT="push" cam={[{ at: fight, kind: "push", s: 1.05 }, { at: barely, kind: "punch", s: 1.12, y: -20 }]} hud={<Verdict phrase="barely hear it" text="QUIET" color={C.green} icon={VolumeX} w={360} />}><Fight /></Shot>
      <Shot from={s2} to={s3} inT="push" outT="whip" cam={[{ at: 0, kind: "settle", s: 1.0, y: 20, dur: 1 }, { at: listen, kind: "punch", s: 1.1, x: 20, y: 30 }, { at: at("noise outside"), kind: "pull", s: 1.0, y: 0 }]}><Mic /></Shot>
      <Shot from={s3} to={s4} inT="whip" outT="whipUp" cam={[{ at: flips, kind: "push", s: 1.05 }, { at: ud, kind: "punch", s: 1.1, y: 40 }, { at: plays, kind: "glide", s: 1.04, x: -30 }, { at: ear, kind: "pull", s: 1.0, x: 0, y: 0 }]}><Flip /></Shot>
      <Shot from={s4} to={s5} inT="whipUp" outT="push" cam={[{ at: plus, kind: "push", s: 1.06, dur: 36 }, { at: flat, kind: "punch", s: 1.1, y: 30 }, { at: di, kind: "pull", s: 1.0, y: 0 }]} hud={<Verdict phrase="flat." until="Engineers call" text="= FLAT" color={C.green} icon={ShieldCheck} w={380} />}><Sum /></Shot>
      <Shot from={s5} to={s6} inT="push" outT="whip" cam={[{ at: engines, kind: "glide", s: 1.04, y: 20 }, { at: rep, kind: "push", s: 1.08, y: 10 }, { at: pred, kind: "pull", s: 1.0, y: 0 }]} hud={<Verdict phrase="predict" text="PREDICTABLE" color={C.green} icon={ShieldCheck} w={440} />}><Steady /></Shot>
      <Shot from={s6} to={card} inT="whip" outT="push" cam={[{ at: clap, kind: "punch", s: 1.12, x: 20, y: 40 }, { at: block, kind: "settle", s: 1.04, y: 10 }, { at: block + 30, kind: "settle", s: 1.0, y: 0 }]} hud={<Verdict phrase="too fast" until="have to block" text="TOO FAST" color={C.red} w={380} />}><Clap /></Shot>
      <Shot from={fin} to={loop} inT="push" outT="whip" cam={[{ at: fin, kind: "pull", s: 0.97, dur: 12 }]}><Fight final /></Shot>
    </EpisodeShell>
  );
};
