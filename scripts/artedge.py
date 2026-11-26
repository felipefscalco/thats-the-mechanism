#!/usr/bin/env python3
"""r9 artwork edge gate (Elevator v7 critic: "clips the left wall of the shaft and the car off-screen (x < 0) for 5+ s").
The label edge gate (contrast.py) only sees text; this one sees ART. An object cut by a side edge of the stage is a framing
bug; full-bleed bands (sky, horizon, ground: touching BOTH side edges) and full-height backdrops are intended.
  object = filled foreground component (vs a heavily blurred background) >= MIN_COMP of the stage
  cut    = touches exactly one side edge over >= MIN_TOUCH (90 px) of the stage height (thin beams/rays entering from off-screen are fine), and is not a backdrop (< MAX_AREA of the stage)
  fail   = a cut held >= HOLD_S outside shot transitions / the brand card / the loop whip
Usage: artedge.py <mp4> <out_dir> [--cuts t1,t2] [--card a,b]"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
arg = lambda k, d: type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
MP4, OUT = sys.argv[1], Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
CUTS = [float(x) for x in arg("--cuts", "").split(",") if x.strip()]; CARD = [float(x) for x in arg("--card", "").split(",") if x.strip()]
W, H, FPS, MIN_COMP, MIN_TOUCH, MAX_AREA, HOLD_S, EDGE = 270, 225, 6, 0.02, 0.10, 0.70, 0.6, 4
STRIP, SAME = 28, 18     # full-res: a cut object's fill continues to x=0 (edge pixel ~= the object 24 px inside, != the scene at that edge); a margin does not
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", MP4, "-vf", f"fps={FPS},crop=1080:900:0:290,scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                     capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32); N = len(fr)
def strip(x):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", MP4, "-vf", f"fps={FPS},crop={STRIP}:900:{x}:290,format=gray", "-f", "rawvideo", "-"],
                       capture_output=True, check=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, 900, STRIP).astype(np.float32)
SL, SR = strip(0), strip(1080 - STRIP)[:, :, ::-1]           # both oriented edge-first
def excluded(t):
    return t < 0.3 or t > N / FPS - 1.0 or any(c - 0.3 <= t <= c + 0.5 for c in CUTS) or (len(CARD) == 2 and CARD[0] - 0.3 <= t <= CARD[1] + 0.3)
hits = []
for k, a in enumerate(fr):
    t = k / FPS
    if excluded(t): hits.append(None); continue
    fg = ndi.binary_fill_holes(ndi.binary_closing(np.abs(a - ndi.gaussian_filter(a, 25, mode="nearest")) > 22, iterations=3))
    lab, n = ndi.label(fg); found = None
    for j, sl in enumerate(ndi.find_objects(lab), 1):
        m = lab[sl] == j
        if m.sum() < MIN_COMP * W * H: continue
        ys, xs = sl; left, right = xs.start <= EDGE, xs.stop >= W - EDGE
        if left == right: continue                                    # inside the stage, or a full-width band
        if m.sum() >= MAX_AREA * W * H: continue                        # a backdrop, not an object
        rows = (lab[:, 6] == j) if left else (lab[:, W - 7] == j)       # the object is solid 24 px in from the edge (mask is exact there)
        st = (SL if left else SR)[min(k, len(SL) - 1)]
        rr = np.repeat(rows, 4)[:900]
        bg = float(np.median(st[~rr, 1])) if (~rr).sum() > 40 else float(np.median(st[:, 1]))   # the scene at this edge, off the object
        cut = rr & (np.abs(st[:, 1] - st[:, 24]) < SAME) & (np.abs(st[:, 1] - bg) > 2 * SAME)   # the object's fill runs on past the edge
        col = cut.sum() / 4
        if col >= MIN_TOUCH * H:
            found = dict(side="left" if left else "right", bbox=[xs.start * 4, ys.start * 4 + 290, xs.stop * 4, ys.stop * 4 + 290], touch_px=int(col * 4)); break
    hits.append(found)
runs, cur = [], None
for k, h in enumerate(hits + [None]):
    if h and cur is None: cur = dict(t_start_s=round(k / FPS, 2), n=0, first=h)
    if h and cur is not None: cur["n"] += 1
    if not h and cur is not None:
        cur["dur_s"] = round(cur.pop("n") / FPS, 2); runs.append(cur); cur = None
fails = [r for r in runs if r["dur_s"] >= HOLD_S]
res = dict(ok=not fails, fails=fails[:10], runs=len(runs), params=dict(min_comp=MIN_COMP, min_touch=MIN_TOUCH, max_area=MAX_AREA, hold_s=HOLD_S))
(OUT / "artedge.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res)[:1500])
