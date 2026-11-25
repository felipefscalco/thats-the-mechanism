#!/usr/bin/env python3
"""WCAG contrast QA for on-screen labels (Label + Pill text), measured on real rendered pixels.

How: remotion/probe_frames.mjs renders every Nth frame with --props {"probe":true}, where every Label/Pill text is pure
magenta (#FF00FF) and has no outline. Magenta pixels = text mask; the ring of pixels around each text block in the probe
frame = the real background (no outline, worst case). The text colour comes from the SAME frame of the final MP4
(so parent opacity, fades and dimming are included). Ratio = WCAG 2.x (L1+0.05)/(L2+0.05).
A label fails if it stays under the threshold for >= PERSIST consecutive samples (0.6 s at every 6th frame), so
fade-ins/outs don't fail but a held low-contrast label does.
Caveat: the probe pass renders the CURRENT code, so only compare against an MP4 rendered from that same code (baselines of old renders must run before code changes).
Usage: contrast.py <CompositionId> <mp4> <outDir> [--min 4.5] [--nth 6]  -> outDir/contrast.json (+ contrast_fail.png)
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

ID, MP4, OUT = sys.argv[1], str(Path(sys.argv[2]).resolve()), Path(sys.argv[3]).resolve(); OUT.mkdir(parents=True, exist_ok=True)
arg = lambda k, d: type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
MIN, NTH, PERSIST = arg("--min", 4.5), arg("--nth", 6), arg("--persist", 3)
ROOT = Path(__file__).resolve().parents[1]
PD = OUT / "_probe"; ND = OUT / "_norm"
for d in (PD, ND):
    d.mkdir(exist_ok=True); [p.unlink() for p in d.glob("*.png")]
r = subprocess.run(["node", "probe_frames.mjs", ID, str(PD), str(NTH), "0.5"], cwd=ROOT / "remotion", capture_output=True, text=True)
if r.returncode: sys.exit(r.stderr[-2000:])
subprocess.run(f"ffmpeg -v error -y -i {MP4} -vf \"select=not(mod(n\\,{NTH})),scale=540:960:flags=area\" -vsync 0 {ND}/n_%04d.png", shell=True, check=True)
probes, norms = sorted(PD.glob("*.png")), sorted(ND.glob("*.png"))
n = min(len(probes), len(norms))

def lum(rgb):
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
ratio = lambda a, b: (max(lum(a), lum(b)) + 0.05) / (min(lum(a), lum(b)) + 0.05)

samples = []  # per sample: list of (bbox, ratio, text_rgb, bg_rgb)
for i in range(n):
    P = np.asarray(Image.open(probes[i]).convert("RGB")).astype(int); N = np.asarray(Image.open(norms[i]).convert("RGB")).astype(int)
    R, G, B = P[..., 0], P[..., 1], P[..., 2]
    mag = (R - G > 90) & (B - G > 90) & (np.abs(R - B) < 60)
    found = []
    if mag.sum() > 20:
        lab, k = ndi.label(ndi.binary_dilation(mag, iterations=6))
        for j, sl in enumerate(ndi.find_objects(lab), 1):
            m = (lab == j) & mag
            if m.sum() < 25: continue
            core = ndi.binary_erosion(m, iterations=1); core = core if core.sum() >= 10 else m
            pure = core & (G < 70)  # fully-opaque magenta (skip antialiased edges)
            core = pure if pure.sum() >= 10 else core
            ring = ndi.binary_dilation(m, iterations=4) & ~ndi.binary_dilation(m, iterations=1) & ~mag
            if ring.sum() < 10: continue
            t = np.median(N[core], axis=0); b = np.median(P[ring], axis=0)
            ys, xs = sl; found.append(dict(bbox=[xs.start * 2, ys.start * 2, xs.stop * 2, ys.stop * 2], ratio=round(float(ratio(t, b)), 2),
                                           text=[int(v) for v in t], bg=[int(v) for v in b]))
    samples.append(found)

def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1])); I = ix * iy
    return I / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - I + 1e-9)
# track low-contrast runs across samples
runs, open_ = [], []
for i, found in enumerate(samples):
    nxt = []
    for f in (x for x in found if x["ratio"] < MIN):
        m = next((o for o in open_ if iou(o["bbox"], f["bbox"]) > 0.3), None)
        if m: m.update(last=i, n=m["n"] + 1, worst=min(m["worst"], f["ratio"]), bbox=f["bbox"], text=f["text"], bg=f["bg"]); nxt.append(m); open_.remove(m)
        else: nxt.append(dict(first=i, last=i, n=1, worst=f["ratio"], bbox=f["bbox"], text=f["text"], bg=f["bg"]))
    runs += open_; open_ = nxt
runs += open_
fails = [dict(t_start_s=round(r_["first"] * NTH / 30, 2), t_end_s=round(r_["last"] * NTH / 30, 2), worst_ratio=r_["worst"], bbox=r_["bbox"], text_rgb=r_["text"], bg_rgb=r_["bg"])
         for r_ in runs if r_["n"] >= PERSIST]
# r5 Shorts UI safe zones (YT Shorts/Reels/TikTok overlays): top 220 px, bottom 360 px (y > 1560), right button column x > 900 from y 900
def unsafe(b):
    x0, y0, x1, y1 = b
    return y0 < 220 or y1 > 1560 or (x1 > 900 and y1 > 900)
sz_all = [(i, x["bbox"]) for i, s_ in enumerate(samples) for x in s_ if unsafe(x["bbox"])]
# held violations only (>= PERSIST consecutive samples, i.e. >= 0.6 s): transitions that fling labels past the edge for a few frames don't count
idx = sorted({i for i, _ in sz_all}); held = set()
run = [idx[0]] if idx else []
for i in idx[1:] + [None]:
    if i is not None and i == run[-1] + 1: run.append(i); continue
    if len(run) >= PERSIST: held.update(run)
    run = [i] if i is not None else []
sz = [dict(t_s=round(i * NTH / 30, 2), bbox=b) for i, b in sz_all if i in held]
allr = [x["ratio"] for s in samples for x in s]
res = dict(min_required=MIN, samples=n, nth=NTH, label_instances=len(allr), min_ratio=round(min(allr), 2) if allr else None,
           p10_ratio=round(float(np.percentile(allr, 10)), 2) if allr else None, median_ratio=round(float(np.median(allr)), 2) if allr else None,
           held_failures=fails, ok=not fails, safe_zone_violations=sz[:20], safe_zone_ok=not sz, safe_zone_transient=len(sz_all) - len(sz))
if fails:  # annotated evidence: one tile per failure (frame of its worst moment)
    tiles = []
    for fl in fails[:8]:
        i = int(round(fl["t_start_s"] * 30 / NTH)); im = Image.open(norms[i]).convert("RGB").resize((540, 960)); d = ImageDraw.Draw(im)
        x0, y0, x1, y1 = [v // 2 for v in fl["bbox"]]; d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], outline=(0, 255, 255), width=3)
        d.text((8, 8), f"{fl['t_start_s']}s ratio {fl['worst_ratio']}", fill=(0, 255, 255)); tiles.append(im)
    sheet = Image.new("RGB", (540 * len(tiles), 960)); [sheet.paste(t, (540 * k, 0)) for k, t in enumerate(tiles)]; sheet.save(OUT / "contrast_fail.png")
(OUT / "contrast.json").write_text(json.dumps(res, indent=1))
for d in (PD, ND):
    [p.unlink() for p in d.glob("*.png")]; d.rmdir()
print(json.dumps({k: v for k, v in res.items() if k != "held_failures"}), "held_failures:", json.dumps(fails))
