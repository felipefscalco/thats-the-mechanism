#!/usr/bin/env python3
"""r7 framing gate: slide-deck boxing (critic rules from ANC_v6/v7, Sky_v6; AI LABS 'AI tells' analysis).

Detects a rectangular container on the stage (y 290-1190): a long top + bottom edge and a long left + right edge that
close into one box (outlined or filled card; rounded corners allowed). Per sample (every 0.2 s, 540x960):
  coverage = box area / stage area of the largest closed box.
FAIL if (a1) a WHOLE-STAGE CARD (coverage >= 0.55, i.e. one rounded box enclosing most of the stage) is held >= 1.0 s, or
        (a2) BOXED FRAMING (any closed box with coverage >= 0.30) covers > 50 % of the runtime.
Excluded: the outro card window (--card a,b) and the loop whip (last 0.5 s). Chrome (chapter deck y 1462-1552, captions)
is outside the stage band, so the real chapter deck is never counted.
Usage: framing.py <mp4 | stills-dir> <outDir> [--card a,b] [--fps 30]  -> outDir/framing.json
"""
import json, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image

src, OUT = Path(sys.argv[1]), Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
arg = lambda k, d: type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
CARD = [float(x) for x in arg("--card", "").split(",") if x.strip()]
NTH, FPS = 6, arg("--fps", 30.0)
WHOLE, BOXED, WHOLE_HOLD_S, BOXED_FRAC = 0.55, 0.30, 1.0, 0.50
Y0, Y1 = 145, 595   # stage band at half scale (290..1190)

def frames():
    if src.is_dir():
        return sorted(src.glob("*.png"))
    tmp = Path(tempfile.mkdtemp(prefix="framing_", dir=OUT))
    subprocess.run(f"ffmpeg -v error -y -i {src} -vf \"select=not(mod(n\\,{NTH})),scale=540:960:flags=area\" -vsync 0 {tmp}/f_%04d.png", shell=True, check=True)
    return sorted(tmp.glob("*.png"))

def runs(b):
    """Longest run length of True per row."""
    best = np.zeros(b.shape[0], int); cur = np.zeros(b.shape[0], int)
    for j in range(b.shape[1]):
        cur = np.where(b[:, j], cur + 1, 0); best = np.maximum(best, cur)
    return best

def box_coverage(img):
    g = np.asarray(img.convert("L"), float)[Y0 - 10:Y1 + 10]
    H, W = g.shape
    gy = np.abs(np.diff(g, axis=0, prepend=g[:1])) > 22
    gx = np.abs(np.diff(g, axis=1, prepend=g[:, :1])) > 22
    gy = gy | np.roll(gy, 1, 0); gx = gx | np.roll(gx, 1, 1)
    hr = runs(gy); vr = runs(gx.T)
    rows = [y for y in range(H) if hr[y] >= 0.45 * W]
    cols = [x for x in range(W) if vr[x] >= 0.25 * (Y1 - Y0)]
    best = 0.0
    if len(rows) < 2 or len(cols) < 2: return 0.0
    # cluster lines
    def clus(v):
        out = []
        for a in v:
            if out and a - out[-1][-1] <= 3: out[-1].append(a)
            else: out.append([a])
        return [int(np.mean(c)) for c in out]
    rows, cols = clus(rows), clus(cols)
    for i, yt in enumerate(rows):
        for yb in rows[i + 1:]:
            if yb - yt < 0.25 * (Y1 - Y0): continue
            for k, xl in enumerate(cols):
                for xr in cols[k + 1:]:
                    if xr - xl < 0.45 * W: continue
                    # sides must span the box height, top/bottom the box width (>= 70 %, rounded corners allowed)
                    side = lambda x: gx[yt:yb, max(0, x - 2):x + 3].any(axis=1).mean()
                    lid = lambda y: gy[max(0, y - 2):y + 3, xl:xr].any(axis=0).mean()
                    if min(side(xl), side(xr)) >= 0.7 and min(lid(yt), lid(yb)) >= 0.7:
                        cov = (xr - xl) * (min(yb, H - 10) - max(yt, 10)) / (W * (Y1 - Y0))
                        best = max(best, cov)
    return round(float(min(best, 1.0)), 3)

fs = frames()
step = NTH / FPS; dur = len(fs) * step
series = []
for i, f in enumerate(fs):
    t = i * step
    skip = t > dur - 0.5 or (len(CARD) == 2 and CARD[0] - 0.2 <= t <= CARD[1] + 0.2)
    series.append(None if skip else box_coverage(Image.open(f)))
valid = [c for c in series if c is not None]
boxed_frac = sum(c >= BOXED for c in valid) / max(1, len(valid))
whole_runs, run_ = [], []
for i, c in enumerate(series + [0]):
    if c is not None and c >= WHOLE: run_.append(i); continue
    if run_ and len(run_) * step >= WHOLE_HOLD_S: whole_runs.append(dict(t_start_s=round(run_[0] * step, 2), t_end_s=round(run_[-1] * step, 2), peak=max(series[k] for k in run_)))
    run_ = []
res = dict(samples=len(valid), boxed_threshold=BOXED, whole_threshold=WHOLE, boxed_frac=round(boxed_frac, 3), boxed_frac_max=BOXED_FRAC,
           whole_stage_card_runs=whole_runs, ok=boxed_frac <= BOXED_FRAC and not whole_runs,
           series=[None if c is None else c for c in series])
(OUT / "framing.json").write_text(json.dumps(res))
if not src.is_dir():
    for f in fs: f.unlink()
    fs[0].parent.rmdir() if fs else None
print(json.dumps({k: v for k, v in res.items() if k != "series"}))
