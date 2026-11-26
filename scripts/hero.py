#!/usr/bin/env python3
"""r9 hero / wow-shot gate (critics: "concept_wow 5", "clipart in empty voids", Sky v8 "Earth cropped off the left edge,
static for 3 s"). shots.md marks the episode's ONE special moment with a beat `hero@<spoken phrase>`; at that word the
render must show a hero shot:
  size     subject (foreground vs a heavily blurred background, components >= 0.5 % of the stage) covers >= MIN_SIZE of
           the stage (bbox of the 5-95 % foreground quantiles), median over the hero window
  centred  foreground centroid within ±MAX_DX of the stage width and ±MAX_DY of its height from the stage centre
  motion   mean structure change >= MIN_MOTION per 1/6 s sample, and no still run > MAX_STILL_S inside the window
  edge     the subject is not cut by a side edge in > MAX_CLIP of the window (Sky v8: Earth cropped off the left)
  duration the hero window (word -> next shot / brand card) lasts >= MIN_DUR_S
Usage: hero.py <CompId> <slug> <mp4> [--json] [--out <dir>]   (static half: static_gates.hero_marked)"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shotlib import words, phrase_time, shots

MIN_SIZE, MAX_DX, MAX_DY, MIN_MOTION, MAX_STILL_S, MIN_DUR_S, FPS, MIN_COMP, MAX_CLIP = 0.35, 0.15, 0.20, 0.02, 1.0, 1.5, 6, 0.02, 0.5
W, H, Y0 = 270, 225, 290

def hero_beat(slug):
    rows = shots(slug); hb = [(i, r, p) for i, r in enumerate(rows) for k, p in r["beats"] if k == "hero"]
    return rows, hb

def check(comp, slug, mp4):
    ws = words(slug); rows, hb = hero_beat(slug)
    if len(hb) != 1: return dict(ok=False, error=f"shots.md must mark exactly one hero@phrase beat (found {len(hb)})")
    i, r, phrase = hb[0]; t = phrase_time(ws, phrase)
    nxt = [phrase_time(ws, x["at"]) for x in rows[i + 1:] if x["at"]]
    card = phrase_time(ws, "That's the mechanism")
    t1 = min([x for x in nxt if x > t] + [card])
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.2f}", "-t", f"{max(0.2, t1 - t):.2f}", "-i", str(mp4), "-vf",
                          f"fps={FPS},crop=1080:900:0:{Y0},scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
    sizes, dxs, dys, clip = [], [], [], []
    for a in fr:   # subject = filled foreground components >= MIN_COMP of the stage (particles, stars, grain don't count)
        fg = ndi.binary_fill_holes(ndi.binary_closing(np.abs(a - ndi.gaussian_filter(a, 25)) > 22, iterations=3))
        lab, n = ndi.label(fg)
        if n:
            areas = ndi.sum(fg, lab, range(1, n + 1)); fg = np.isin(lab, 1 + np.where(areas >= MIN_COMP * W * H)[0])
        ys, xs = np.nonzero(fg)
        if len(xs) < 50: sizes.append(0.0); dxs.append(1.0); dys.append(1.0); clip.append(False); continue
        x0, x1 = np.percentile(xs, [5, 95]); y0, y1 = np.percentile(ys, [5, 95])
        sizes.append(float((x1 - x0) * (y1 - y0) / (W * H))); dxs.append(float(abs(xs.mean() - W / 2) / W)); dys.append(float(abs(ys.mean() - H / 2) / H))
        clip.append(bool(fg[:, :2].sum() > 0.25 * H or fg[:, -2:].sum() > 0.25 * H))   # subject runs off a side edge
    bl = [ndi.gaussian_filter(a, 3) for a in fr]   # structure-level change (drifting particles blur away)
    d = [float((np.abs(bl[k + 1] - bl[k]) > 8).mean()) for k in range(len(bl) - 1)]
    still, run = 0.0, 0
    for x in d:
        run = run + 1 if x < 0.005 else 0; still = max(still, run / FPS)
    m = dict(t_s=round(t, 2), until_s=round(t1, 2), duration_s=round(t1 - t, 2), size=round(float(np.median(sizes)), 3) if sizes else 0,
             dx=round(float(np.median(dxs)), 3) if dxs else 1, dy=round(float(np.median(dys)), 3) if dys else 1,
             motion=round(float(np.mean(d)), 4) if d else 0, longest_still_s=round(still, 2), clipped_frac=round(float(np.mean(clip)), 2) if clip else 0, phrase=phrase, shot=r["n"])
    fails = [k for k, bad in (("size", m["size"] < MIN_SIZE), ("centred", m["dx"] > MAX_DX or m["dy"] > MAX_DY),
                              ("motion", m["motion"] < MIN_MOTION or still > MAX_STILL_S), ("duration", m["duration_s"] < MIN_DUR_S), ("edge_clip", m["clipped_frac"] > MAX_CLIP)) if bad]
    return dict(ok=not fails, fails=fails, **m, limits=dict(min_size=MIN_SIZE, max_dx=MAX_DX, max_dy=MAX_DY, min_motion=MIN_MOTION, max_still_s=MAX_STILL_S, min_dur_s=MIN_DUR_S))

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    r = check(a[0], a[1], a[2])
    if "--out" in sys.argv: Path(sys.argv[sys.argv.index("--out") + 1]).joinpath("hero.json").write_text(json.dumps(r, indent=1))
    print(json.dumps(r) if "--json" in sys.argv else f"hero {a[0]} {'PASS' if r['ok'] else 'FAIL'} {r}")
    sys.exit(0 if r["ok"] else 1)
