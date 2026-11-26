#!/usr/bin/env python3
"""r8 entrance gate for EVERY element (not just badges): an element that appears on a quiet stage must arrive with
motion (scale / slide / draw-on, ideally overshoot), never a hard snap and never an opacity-only fade.
Method (stage ROI y 290-1190 at 1/5 scale, every frame): an entrance is a region that was quiet for 0.1 s and then
gains structure (edge energy up) over the next 0.3 s. For each, per-pixel progress p(x,k) = (frame_k - before) /
(after - before) is followed through the entrance:
  snap       -> >= 85 % of the change lands in one frame
  fade-only  -> while the element is 20-80 % in, progress is spatially uniform (std < FADE_STD) and never overshoots:
                every pixel brightens together = a pure opacity ramp, no scale/slide/draw-on
  ok         -> anything else (scale pop, slide, wipe/draw-on, overshoot)
Usage: entrances.py <mp4> <out_dir> [--cuts t1,t2] [--card a,b] [--json]  -> <out_dir>/entrances.json"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
arg = lambda k, d: type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
MP4, OUT = sys.argv[1], Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
CUTS = [float(x) for x in arg("--cuts", "").split(",") if x.strip()]
CARD = [float(x) for x in arg("--card", "").split(",") if x.strip()]
MIN_AREA, FADE_STD, PRE, POST = arg("--min-area", 120), arg("--fade-std", 0.12), 3, 9
raw = subprocess.run(f"ffmpeg -v error -i {MP4} -vf crop=1080:900:0:290,scale=216:180,format=gray -f rawvideo -", shell=True, capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, 180, 216).astype(np.float32); N = len(fr); fps = 30.0
edge = lambda a: np.hypot(ndi.sobel(a, 0), ndi.sobel(a, 1))
def excluded(t):
    if t < 0.4 or t > N / fps - 1.0: return True
    if len(CARD) == 2 and CARD[0] - 0.3 <= t <= CARD[1] + 0.3: return True
    return any(c - 0.2 <= t <= c + 0.5 for c in CUTS)
events, used = [], np.zeros((N, 180, 216), bool)
for t in range(PRE + 1, N - POST - 6):
    if excluded(t / fps): continue
    if (np.abs(fr[t + POST] - fr[t - 1]) > 30).mean() > 0.35: continue   # scene change / shot transition, not an element entrance
    quiet = np.abs(fr[t - 1] - fr[t - 1 - PRE]) < 6
    gain = np.abs(fr[t + POST] - fr[t - 1]) > 30
    m = quiet & gain & ~used[t]
    if m.sum() < MIN_AREA: continue
    lab, n = ndi.label(ndi.binary_closing(m, iterations=2))
    for j, sl in enumerate(ndi.find_objects(lab), 1):
        if sl is None: continue
        reg = lab[sl] == j
        if reg.sum() < MIN_AREA: continue
        before, after = fr[t - 1][sl], fr[t + POST][sl]
        e0, e1 = edge(fr[t - 1])[sl][reg].mean(), edge(fr[t + POST])[sl][reg].mean()
        if e1 < 2.0 * e0 + 4: continue                       # not an arrival (exit, recolour, background drift)
        if t + POST + 5 >= N or np.abs(fr[t + POST + 5][sl] - after)[reg].mean() > 5: continue   # still moving = travelling element, not an arrival that settles
        d = (after - before)[reg]; ok_px = np.abs(d) > 30
        if ok_px.sum() < MIN_AREA // 2: continue
        prog = np.stack([((fr[k][sl] - before)[reg])[ok_px] / d[ok_px] for k in range(t - 1, t + POST + 1)])  # frames x pixels
        mean = prog.mean(axis=1)
        step = float(np.max(np.diff(mean)))
        mid = [k for k in range(len(mean)) if 0.2 <= mean[k] <= 0.8]
        std_mid = float(np.mean([prog[k].std() for k in mid])) if mid else 0.0
        over = float(prog.max(axis=0).mean())
        kind = "snap" if step >= 0.85 else ("fade-only" if mid and std_mid < FADE_STD and over <= 1.05 else "ok")
        ys, xs = sl
        events.append(dict(t_s=round(t / fps, 2), bbox=[xs.start * 5, ys.start * 5 + 290, xs.stop * 5, ys.stop * 5 + 290], area_px=int(reg.sum() * 25),
                           kind=kind, max_step=round(step, 2), mid_std=round(std_mid, 3), overshoot=round(over, 2)))
        used[t:t + POST + 1][:, sl[0], sl[1]] |= reg
bad = [e for e in events if e["kind"] != "ok"]
_cfg = json.loads((Path(__file__).resolve().parent.parent / "pipeline.config.json").read_text()).get("qa_gates", {}).get("entrances", {})
MAX_FADES = arg("--max-fades", int(_cfg.get("max_fade_only", 2)))
n_snap = sum(e["kind"] == "snap" for e in bad); n_fade = len(bad) - n_snap
res = dict(ok=n_snap == 0 and n_fade <= MAX_FADES, max_fade_only=MAX_FADES, entrances=len(events), snaps=[e for e in bad if e["kind"] == "snap"][:20], fades=[e for e in bad if e["kind"] == "fade-only"][:20],
           ok_count=len(events) - len(bad), params=dict(min_area_px=MIN_AREA * 25, fade_std=FADE_STD))
(OUT / "entrances.json").write_text(json.dumps(res, indent=1))
print("entrances", "PASS" if res["ok"] else "FAIL", len(events), "events;", len(res["snaps"]), "snaps,", len(res["fades"]), "fade-only")
for e in bad[:30]: print(" ", e)
