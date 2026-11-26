#!/usr/bin/env python3
"""WCAG contrast QA for on-screen labels (Label + Pill text), measured on real rendered pixels.

How: remotion/probe_frames.mjs renders every Nth frame twice from one bundle. Pass 1 uses {"probe":true}: every Label/Pill text is pure
magenta (#FF00FF) and has no outline, and backings stay their real colours. Magenta pixels = text mask; the ring of pixels around each text block in the probe
frame = the real background (no outline, worst case). The text colour comes from the SAME frame of the final MP4
(so parent opacity, fades and dimming are included). Ratio = WCAG 2.x (L1+0.05)/(L2+0.05).
Pass 2 uses {"probeOccupancy":true}: same magenta text, but TagLabel/Pill/TitleHook backings are cyan (#00FFFF) so the overlap gate can measure pill occupancy without poisoning the WCAG ring.
A label fails if it stays under the threshold for >= PERSIST consecutive samples (0.6 s at every 6th frame), so
fade-ins/outs don't fail but a held low-contrast label does.
Caveat: the probe pass renders the CURRENT code, so only compare against an MP4 rendered from that same code (baselines of old renders must run before code changes).
Usage: contrast.py <CompositionId> <mp4 or - (preview stills)> <outDir> [--min 4.5] [--nth 6]  -> outDir/contrast.json (+ contrast_fail.png)
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
PD = OUT / "_probe"; OCC = OUT / "_probe_occ"; ND = OUT / "_norm"
for d in (PD, OCC, ND):
    d.mkdir(exist_ok=True); [p.unlink() for p in d.glob("*.png")]
OCC_NTH = 2  # occupancy pass is denser: overlap uses every (NTH // OCC_NTH)-th frame, the badge-pop gate uses all of them
# r7 preview-first: MP4 "-" (or --preview) = no render needed. A third pass renders the normal look as stills from the
# same bundle, so contrast/edge/overlap/pop/clutter gates run before any full render (scripts/preview.py).
PREVIEW = MP4.endswith("/-") or MP4 == "-" or "--preview" in sys.argv
_passes = [str(PD), str(NTH), "0.5", '{"probe":true}', str(OCC), '{"probeOccupancy":true}', str(OCC_NTH)]
if PREVIEW: _passes += [str(ND), "{}", str(NTH)]
r = subprocess.run(["node", "probe_frames.mjs", ID, *_passes], cwd=ROOT / "remotion", capture_output=True, text=True)
if r.returncode: sys.exit(r.stderr[-2000:] or r.stdout[-2000:])
if not PREVIEW:
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
# r9 ghost text (Sky v8 critic blocker, min ratio 1.04): a label that is briefly see-through (fading, or text without its
# backing yet) before/after it reaches full contrast. Short runs (< PERSIST) under GHOST whose same label is >= MIN within
# +-GHOST_WIN samples. Atomic kit components can't do this, so any such sample outside a shot transition fails the gate.
GHOST, GHOST_WIN = arg("--ghost", 3.0), 5
def _good_near(r_):
    lo, hi = max(0, r_["first"] - GHOST_WIN), min(len(samples), r_["last"] + GHOST_WIN + 1)
    return any(x["ratio"] >= MIN and iou(x["bbox"], r_["bbox"]) > 0.3 for k in range(lo, hi) for x in samples[k])
ghosts = [dict(t_start_s=round(r_["first"] * NTH / 30, 2), t_end_s=round(r_["last"] * NTH / 30, 2), samples=r_["n"], worst_ratio=r_["worst"], bbox=r_["bbox"])
          for r_ in runs if r_["n"] < PERSIST and r_["worst"] < GHOST and _good_near(r_)]
_gcuts = [float(x) for x in arg("--cuts", "").split(",") if x.strip()]
_gcard = [float(x) for x in arg("--card", "").split(",") if x.strip()]
def _in_transition(t):   # shot transitions (push/whip blur) and the brand card / loop whip are not label fades
    return any(c - 0.3 <= t <= c + 0.5 for c in _gcuts) or (len(_gcard) == 2 and _gcard[0] - 0.3 <= t <= _gcard[1] + 0.3) or t >= len(samples) * NTH / 30 - 1.0
ghost_fail = [g for g in ghosts if not _in_transition(g["t_start_s"])]   # r9 atomic kit: ANY see-through label sample fails
# r5 Shorts UI safe zones (YT Shorts/Reels/TikTok overlays): top 220 px, bottom 360 px (y > 1560), right button column x > 900 from y 900
# r6 (critic blocker, Elevator v6 00:17-00:26 'CAR vs CW' -> 'AR vs CW'): a label pushed past the left/right frame edge
# by a camera move is clipped. Text must keep >= 24 px from both side edges (EDGE), held >= 0.6 s like the rest.
EDGE = 24
def unsafe(b):
    x0, y0, x1, y1 = b
    return y0 < 220 or y1 > 1560 or (x1 > 900 and y1 > 900) or x0 < EDGE or x1 > 1080 - EDGE
sz_all = [(i, x["bbox"]) for i, s_ in enumerate(samples) for x in s_ if unsafe(x["bbox"])]
# held violations only (>= PERSIST consecutive samples, i.e. >= 0.6 s): transitions that fling labels past the edge for a few frames don't count
idx = sorted({i for i, _ in sz_all}); held = set()
run = [idx[0]] if idx else []
for i in idx[1:] + [None]:
    if i is not None and i == run[-1] + 1: run.append(i); continue
    if len(run) >= PERSIST: held.update(run)
    run = [i] if i is not None else []
# r7 (r6 gap 3, Sky SUNSET clipped at 0.3 s): the hook/intro is judged frame by frame. Any side-edge/safe-zone clip in
# the first INTRO_S seconds fails even if shorter than 0.6 s (that is the thumbnail and the first impression).
INTRO_S = 2.0
held |= {i for i in idx if i * NTH / 30 < INTRO_S}
sz = [dict(t_s=round(i * NTH / 30, 2), bbox=b, intro=i * NTH / 30 < INTRO_S) for i, b in sz_all if i in held]
allr = [x["ratio"] for s in samples for x in s]

# r6: label/icon overlap + clearance (ANC 00:16 SPEAKER clipped CHIP). Occupancy = magenta text
# OR cyan backings (TagLabel/Pill/TitleHook in probe). Fail if two stage occupancies sit closer
# than CLEARANCE px, or a foreign (non-key) object covers the interior of a pill, held >= 0.6 s.
CLEARANCE = 36
def box_clearance(a, b):
    dx = max(0, a[0] - b[2], b[0] - a[2]); dy = max(0, a[1] - b[3], b[1] - a[3])
    if dx == 0 and dy == 0: return 0.0
    return float(dy if dx == 0 else dx if dy == 0 else (dx * dx + dy * dy) ** 0.5)
def box_iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1])); I = ix * iy
    return I / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - I + 1e-9)
def merge_stacked(boxes, gap=24, min_iou=0.45):
    boxes = [list(b) for b in boxes]
    changed = True
    while changed and len(boxes) > 1:
        changed = False
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i], boxes[j]
                x_iou = max(0, min(a[2], b[2]) - max(a[0], b[0])) / (max(a[2], b[2]) - min(a[0], b[0]) + 1e-9)
                vgap = max(0, a[1] - b[3], b[1] - a[3])
                if x_iou >= min_iou and vgap <= gap:
                    boxes[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    boxes.pop(j); changed = True; break
            if changed: break
    return boxes
def union_box(boxes):
    return [min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes)]
def y_iou(a, b):
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return iy / (min(a[3] - a[1], b[3] - b[1]) + 1e-9)
def x_gap(a, b):
    return max(0, a[0] - b[2], b[0] - a[2])
def labelled_boxes(mask, min_px=15):
    lab, _ = ndi.label(mask)
    out = []
    for j, sl in enumerate(ndi.find_objects(lab), 1):
        if sl is None: continue
        m = lab == j
        if m.sum() < min_px: continue
        ys, xs = sl
        bbox = [xs.start * 2, ys.start * 2, xs.stop * 2, ys.stop * 2]
        if bbox[1] >= 1222:  # captions / deck, not stage labels
            continue
        out.append(dict(id=j, bbox=bbox, mask=m))
    return out
def cluster_baseline(items, max_gap=64, min_yiou=0.5):
    # Join same-baseline fragments split by an occluder (CHIP -> CH + P) without
    # merging two properly spaced labels (text gap ~= 72 px at LANE_GAP).
    unused = list(range(len(items)))
    clusters = []
    while unused:
        i = unused.pop(0); cl = [i]; changed = True
        while changed:
            changed = False
            for j in list(unused):
                if any(y_iou(items[a]["bbox"], items[j]["bbox"]) >= min_yiou and x_gap(items[a]["bbox"], items[j]["bbox"]) <= max_gap for a in cl):
                    cl.append(j); unused.remove(j); changed = True
        clusters.append(cl)
    return clusters
def stadium_mask(shape, bbox, shrink=2):
    """Rounded-rect mask in probe space. Capsules (rx=h/2) for squat pills; tight rx for tall title hooks."""
    h, w = shape
    x0, y0, x1, y1 = [v / 2.0 for v in bbox]
    bw, bh = max(1.0, x1 - x0), max(1.0, y1 - y0)
    rx = min(bw, bh) / 2.0 if bh <= 50 else 8.0  # pills/tags (<= 100 px tall) are capsules; title hooks have rx 22
    rx = max(0.0, rx - shrink)
    if rx <= 0:
        yy, xx = np.mgrid[0:h, 0:w]
        return (xx >= x0 + shrink) & (xx < x1 - shrink) & (yy >= y0 + shrink) & (yy < y1 - shrink)
    cx0, cx1 = x0 + rx + shrink, x1 - rx - shrink
    cy0, cy1 = y0 + rx + shrink, y1 - rx - shrink
    if cx1 < cx0: cx0 = cx1 = (x0 + x1) / 2.0
    if cy1 < cy0: cy0 = cy1 = (y0 + y1) / 2.0
    yy, xx = np.ogrid[0:h, 0:w]
    dx = np.maximum(np.maximum(cx0 - xx, xx - cx1), 0)
    dy = np.maximum(np.maximum(cy0 - yy, yy - cy1), 0)
    return (dx * dx + dy * dy) <= rx * rx + 0.5
def occupy(P):
    # Occupancy is built from the occupancy-probe frame (cyan backings + magenta text).
    # Magenta fragments on one baseline with a gap <= 64 px are one split label; cyan
    # sharing that cluster rebuilds the pill, then foreign (non-key) pixels inside the
    # stadium are an icon covering the label. (The previous version labelled the union
    # of cyan|magenta, so overlapping/split pills collapsed to one box, and
    # `eroded_cyan & ~cyan` was identically zero — so the 00:16 SPEAKER/CHIP slip passed.)
    R, G, B = P[..., 0], P[..., 1], P[..., 2]
    mag = (R - G > 90) & (B - G > 90) & (np.abs(R - B) < 60)
    # Tight to #00FFFF so brand teals (header "TECH", hex-cell strokes, chapter "01/05")
    # are not treated as occupancy. Magenta is still the looser key used for WCAG.
    cyn = (R < 50) & (G > 220) & (B > 220) & (np.abs(G.astype(int) - B) < 30)
    mcomps = labelled_boxes(ndi.binary_dilation(mag, iterations=2), 15)
    ccomps = labelled_boxes(ndi.binary_dilation(cyn, iterations=1), 20)
    clusters = cluster_baseline(mcomps, max_gap=64)
    raw = []
    for cl in clusters:
        members = [mcomps[i] for i in cl]
        ub = union_box([m["bbox"] for m in members])
        cyn_ids = set()
        for c in ccomps:
            # r7: only text that sits ON the backing joins it. Raw SVG text is now in the mask too, and a label that merely
            # sits near a pill (<= 16 px) must stay separate so the clearance check measures the gap instead of
            # inflating the pill into a giant 'occupied' box.
            if box_iou(ub, c["bbox"]) > 0:
                cyn_ids.add(c["id"]); ub = union_box([ub, c["bbox"]])
        raw.append(dict(bbox=ub, cyn_ids=cyn_ids, split=len(cl) > 1, has_cyan=bool(cyn_ids)))
    # leftover cyan with no magenta still counts (empty pill / icon-only)
    used = {i for o in raw for i in o["cyn_ids"]}
    for c in ccomps:
        if c["id"] not in used:
            raw.append(dict(bbox=c["bbox"], cyn_ids={c["id"]}, split=False, has_cyan=True))
    # magenta clusters that attached to the same cyan backing (TitleHook lines) are one occupancy
    merged, skip = [], set()
    for i, a in enumerate(raw):
        if i in skip: continue
        acc = dict(a); acc["cyn_ids"] = set(a["cyn_ids"])
        for j, b in enumerate(raw[i + 1 :], i + 1):
            if j in skip: continue
            if acc["cyn_ids"] and acc["cyn_ids"] & b["cyn_ids"]:
                acc["bbox"] = union_box([acc["bbox"], b["bbox"]])
                acc["cyn_ids"] |= b["cyn_ids"]; acc["split"] = acc["split"] or b["split"]
                acc["has_cyan"] = True; skip.add(j)
        merged.append(acc)
    boxes, interiors = [], []
    # Dilate key colors so font AA (the ring between magenta glyphs and cyan backings)
    # is not counted as an occluder. A real icon over the pill stays well outside that halo.
    key = ndi.binary_dilation(mag | cyn, iterations=2)
    for o in merged:
        boxes.append(o["bbox"]); fr = 0
        if o["has_cyan"]:
            core = stadium_mask(mag.shape[:2], o["bbox"], shrink=2)
            fr = int((core & ~key).sum())
        interiors.append(fr)
    return boxes, interiors
ov_per = []
occs_all = sorted(OCC.glob("*.png"))
occs = occs_all[:: NTH // OCC_NTH]
if len(occs) < n: sys.exit(f"occupancy probe frames {len(occs)} < contrast frames {n}")
for i in range(n):
    P = np.asarray(Image.open(occs[i]).convert("RGB")).astype(int)
    raw_boxes, interiors = occupy(P)
    hits = []
    for ia, fr in enumerate(interiors):
        if fr >= 80:
            hits.append(dict(kind="occlusion", foreign_px=int(fr) * 4, bbox_a=raw_boxes[ia], bbox_b=None, clearance=0))
    boxes = merge_stacked(raw_boxes)
    for ia in range(len(boxes)):
        for ib in range(ia + 1, len(boxes)):
            cl = box_clearance(boxes[ia], boxes[ib])
            if cl < CLEARANCE:
                hits.append(dict(kind="clearance", clearance=round(cl, 1), bbox_a=boxes[ia], bbox_b=boxes[ib]))
    ov_per.append(hits)
# held violations (>= PERSIST consecutive samples)
ov_runs, ov_open = [], []
for i, hits in enumerate(ov_per):
    nxt = []
    for h in hits:
        if h.get("bbox_b"):
            kb = [min(h["bbox_a"][k], h["bbox_b"][k]) if k < 2 else max(h["bbox_a"][k], h["bbox_b"][k]) for k in range(4)]
        else:
            kb = list(h["bbox_a"])
        m = next((o for o in ov_open if o["kind"] == h["kind"] and box_iou(o["bbox"], kb) > 0.3), None)
        if m:
            m.update(last=i, n=m["n"] + 1, worst=min(m["worst"], h.get("clearance", 0)), bbox=kb, hit=h)
            nxt.append(m); ov_open.remove(m)
        else:
            nxt.append(dict(first=i, last=i, n=1, worst=h.get("clearance", 0), bbox=kb, kind=h["kind"], hit=h))
    ov_runs += ov_open; ov_open = nxt
ov_runs += ov_open
ov_fails = [dict(t_start_s=round(r_["first"] * NTH / 30, 2), t_end_s=round(r_["last"] * NTH / 30, 2),
                 kind=r_["kind"], min_clearance=r_["worst"], bbox=r_["bbox"], detail=r_["hit"])
            for r_ in ov_runs if r_["n"] >= PERSIST]
min_cl = None
all_cl = [h["clearance"] for hits in ov_per for h in hits if "clearance" in h]
# also record the global min among ALL pairs in any frame that had at least 2 boxes? skip; report worst held
overlap_min_clearance = round(min((f["min_clearance"] for f in ov_fails), default=CLEARANCE), 1)
if ov_fails:
    tiles = []
    for fl in ov_fails[:8]:
        i = int(round(fl["t_start_s"] * 30 / NTH)); i = min(max(i, 0), n - 1)
        im = Image.open(norms[i]).convert("RGB").resize((540, 960)); d = ImageDraw.Draw(im)
        hit = fl.get("detail") or {}
        for key, col in (("bbox_a", (255, 80, 80)), ("bbox_b", (255, 200, 0)), ("bbox", (255, 80, 80))):
            b = hit.get(key) or (fl["bbox"] if key == "bbox" else None)
            if not b: continue
            x0, y0, x1, y1 = [v // 2 for v in b]; d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], outline=col, width=3)
        d.text((8, 8), f"{fl['t_start_s']}s {fl['kind']} cl={fl['min_clearance']}", fill=(255, 80, 80)); tiles.append(im)
    if tiles:
        sheet = Image.new("RGB", (540 * len(tiles), 960)); [sheet.paste(t, (540 * k, 0)) for k, t in enumerate(tiles)]; sheet.save(OUT / "overlap_fail.png")

# r6 gate: badge entrances must pop with anticipation/overshoot (critic rule R-002, ANC/Elevator/Sky).
# Track every cyan backing (TagLabel / Pill / TitleHook) on the dense occupancy pass. A badge that is born on
# a still stage (not at frame 0, not inside a shot transition, not in the loop whip) and already sits at its
# settled width in its first samples "snapped in". Pass = it grows into place (first width <= 92% of settled)
# or overshoots (peak >= 101.5% of settled) within 0.53 s. Transitions are passed in by qa.py with --cuts.
CUTS = [float(x) for x in arg("--cuts", "").split(",") if x.strip()]
STEP_S = OCC_NTH / 30
dur_s = len(occs_all) * STEP_S
def excluded(t):
    if t < 0.5 or t > dur_s - 1.0: return True
    return any(c - 0.1 <= t <= c + 0.5 for c in CUTS)
tracks, live = [], []
for i, path in enumerate(occs_all):
    P = np.asarray(Image.open(path).convert("RGB")).astype(int)
    R, G, B = P[..., 0], P[..., 1], P[..., 2]
    cyn = (R < 50) & (G > 220) & (B > 220) & (np.abs(G - B) < 30)
    lab, _ = ndi.label(ndi.binary_closing(cyn, iterations=2))
    Hh, Ww = cyn.shape
    boxes = []
    for j, sl in enumerate(ndi.find_objects(lab), 1):
        if sl is None or (lab[sl] == j).sum() < 60: continue
        ys, xs = sl
        if ys.start * 2 >= 1222: continue
        boxes.append([xs.start, ys.start, xs.stop, ys.stop])
    nxt = []
    for b in boxes:
        m = next((tr for tr in live if box_iou(tr["b"][-1], b) > 0.3), None)
        if m: m["b"].append(b); m["last"] = i; nxt.append(m); live.remove(m)
        else:
            tr = dict(birth=i, last=i, b=[b], edge=b[0] <= 2 or b[2] >= Ww - 2 or b[1] <= 2 or b[3] >= Hh - 2); tracks.append(tr); nxt.append(tr)
    live = [tr for tr in live if i - tr["last"] <= 1] + nxt
pops, snaps = [], []
for tr in tracks:
    if len(tr["b"]) < 10 or tr["edge"]: continue
    t0 = tr["birth"] * STEP_S
    if excluded(t0): continue
    w = np.array([b[2] - b[0] for b in tr["b"]], float); cx = np.array([(b[0] + b[2]) / 2 for b in tr["b"]])
    W = float(np.median(w[8:14])) if len(w) >= 12 else float(w[-1])
    head = w[:8]
    grow = head[0] <= 0.92 * W; over = head.max() >= 1.015 * W
    moving = abs(cx[min(7, len(cx) - 1)] - cx[0]) > 0.1 * W
    rec = dict(t_s=round(t0, 2), bbox=[v * 2 for v in tr["b"][0]], first_w_ratio=round(float(head[0] / W), 3), peak_w_ratio=round(float(head.max() / W), 3))
    if grow or over: pops.append(rec)
    elif not moving: snaps.append(rec)
pop_ok = not snaps

# r7 gates on the same dense occupancy pass:
#  (e) hand-rolled badges: magenta text sitting on a compact, uniform, NON-cyan backing (an episode-drawn rect/pill)
#      is tracked like a TagLabel/Pill and must pop too (r6 gap 2: the pop gate only saw cyan backings).
#  (b) callout clutter: more than CLUTTER_MAX pills/badges (cyan backings + hand-rolled badges) on the stage at once,
#      held >= 0.6 s, fails (Sky_v6 0:35 had four callout pills; critic: 'clutter of callouts').
_QG = json.loads((Path(__file__).resolve().parent.parent / "pipeline.config.json").read_text()).get("qa_gates", {}).get("clutter", {})
CLUTTER_COUNT = arg("--clutter-count", _QG.get("count", "floating"))   # floating | all
ATTACH_PX = arg("--attach-px", int(_QG.get("attach_px", 25)))
CLUTTER_MAX = arg("--clutter-max", int(_QG.get("max", 3)))
CARD = [float(x) for x in arg("--card", "").split(",") if x.strip()]
in_card = lambda t: len(CARD) == 2 and CARD[0] - 0.2 <= t <= CARD[1] + 0.2
def backed_badges(P):
    R, G, B = P[..., 0], P[..., 1], P[..., 2]
    mag = (R - G > 90) & (B - G > 90) & (np.abs(R - B) < 60)
    cyn = (R < 50) & (G > 220) & (B > 220) & (np.abs(G - B) < 30)
    keyish = ndi.binary_dilation(mag, iterations=2)
    H_, W_ = mag.shape; out = []
    comps = labelled_boxes(ndi.binary_dilation(mag, iterations=2), 15)
    for cl in cluster_baseline(comps, max_gap=40):
        x0, y0, x1, y1 = [v // 2 for v in union_box([comps[i]["bbox"] for i in cl])]
        if y1 * 2 > 1222 or y0 * 2 < 200: continue
        def ring(a, b):
            m = np.zeros_like(mag); m[max(0, y0 - b):y1 + b, max(0, x0 - b):x1 + b] = True
            m[max(0, y0 - a):y1 + a, max(0, x0 - a):x1 + a] = False
            return m & ~keyish
        inner, outer = ring(3, 8), ring(16, 22)
        if inner.sum() < 30 or outer.sum() < 30: continue
        if (cyn & ring(0, 10)).sum() > 10: continue          # cyan-backed: already tracked by the pop gate above
        med = np.median(P[inner], axis=0)
        near = lambda m: float((np.abs(P[m] - med).max(axis=1) < 26).mean())
        if near(inner) >= 0.85 and near(outer) <= 0.45 and np.abs(med - np.median(P[outer], axis=0)).max() > 30:
            out.append([x0, y0, x1, y1])
    # Grid / table cells (>= 3 same-size backed boxes on one row, e.g. a byte grid) are diagram content, not callouts.
    def in_grid(b, allb):
        h = b[3] - b[1]; w = b[2] - b[0]
        row = [c for c in allb if y_iou(c, b) >= 0.6 and abs((c[3] - c[1]) - h) <= 0.25 * h + 2]
        return len(row) >= 3
    out = [b for b in out if not in_grid(b, out)]
    # Callouts are pill-shaped: short and wide (h <= 120 px at full res, w/h >= 1.6). Title blocks and icon tiles are not.
    pill = lambda b: (b[3] - b[1]) * 2 <= 120 and (b[2] - b[0]) >= 1.6 * (b[3] - b[1])
    # r8: a pill is a FLOATING callout unless diagram art touches it (a leader line, the part it names, a shape edge
    # in a 2-18 px ring at half scale). Labels attached to shapes are diagram content (ANC_v7 15.5 s: NOISE/CHIP/
    # SPEAKER tags on the parts they name). CLUTTER_COUNT=floating (default, pipeline.config.json gates.clutter.count)
    # counts only floating callouts; "all" restores the r7 behaviour.
    keyc = ndi.binary_dilation(mag | cyn, iterations=3)
    def attached(b):
        # attached = a piece of diagram art (>= 25 px connected, i.e. not a background dot) reaches within 6 px of the
        # pill: a leader line, the part it names, a shape edge. Art = pixels far (> 45) from the ring's median colour.
        x0, y0, x1, y1 = b
        m = np.zeros_like(mag); m[max(0, y0 - 18):y1 + 18, max(0, x0 - 18):x1 + 18] = True
        m[max(0, y0 - 2):y1 + 2, max(0, x0 - 2):x1 + 2] = False; m &= ~keyc
        if m.sum() < 40: return False
        med = np.median(P[m], axis=0)
        art = m & (np.abs(P - med).max(axis=2) > 45)
        lab_, _ = ndi.label(art)
        near = np.zeros_like(mag); near[max(0, y0 - 8):y1 + 8, max(0, x0 - 8):x1 + 8] = True
        ids = set(np.unique(lab_[near & art])) - {0}
        return any((lab_ == k).sum() >= ATTACH_PX for k in ids)
    cand = []
    labc, _ = ndi.label(ndi.binary_closing(cyn, iterations=2))
    for j, sl in enumerate(ndi.find_objects(labc), 1):
        if sl is None or (labc[sl] == j).sum() < 60: continue
        if sl[0].start * 2 >= 1222 or sl[0].stop * 2 < 220: continue
        b = [sl[1].start, sl[0].start, sl[1].stop, sl[0].stop]
        if pill(b): cand.append(b)
    # backed text bbox is the glyph box; the badge around it adds ~20 px padding per side at half scale
    cand += [[b[0] - 10, b[1] - 6, b[2] + 10, b[3] + 6] for b in out if pill([b[0] - 10, b[1] - 6, b[2] + 10, b[3] + 6])]
    floating = [b for b in cand if not attached(b)]
    return out, (len(floating) if CLUTTER_COUNT == "floating" else len(cand)), len(cand)
btracks, blive, clutter_series, clutter_all = [], [], [], []
for i, path in enumerate(occs_all):
    P = np.asarray(Image.open(path).convert("RGB")).astype(int)
    boxes, cnt, cnt_all = backed_badges(P)
    t = i * STEP_S
    clutter_series.append(0 if in_card(t) else cnt); clutter_all.append(0 if in_card(t) else cnt_all)
    nxt = []
    for b in boxes:
        m = next((tr for tr in blive if box_iou(tr["b"][-1], b) > 0.3), None)
        if m: m["b"].append(b); m["last"] = i; nxt.append(m); blive.remove(m)
        else:
            tr = dict(birth=i, last=i, b=[b], edge=b[0] <= 2 or b[2] >= P.shape[1] - 2); btracks.append(tr); nxt.append(tr)
    blive = [tr for tr in blive if i - tr["last"] <= 1] + nxt
bsnaps = []
for tr in btracks:
    if len(tr["b"]) < 10 or tr["edge"]: continue
    t0 = tr["birth"] * STEP_S
    if excluded(t0) or in_card(t0): continue
    w = np.array([b[2] - b[0] for b in tr["b"]], float); cx = np.array([(b[0] + b[2]) / 2 for b in tr["b"]])
    W = float(np.median(w[8:14])) if len(w) >= 12 else float(w[-1]); head = w[:8]
    grow = head[0] <= 0.92 * W; over = head.max() >= 1.015 * W; moving = abs(cx[min(7, len(cx) - 1)] - cx[0]) > 0.1 * W
    if not (grow or over or moving):
        bsnaps.append(dict(t_s=round(t0, 2), bbox=[v * 2 for v in tr["b"][0]], kind="hand-rolled badge"))
pop_ok = pop_ok and not bsnaps
snaps += bsnaps
need = int(round(0.6 / STEP_S)); clutter_runs, run_ = [], []
for i, c in enumerate(clutter_series + [0]):
    if c > CLUTTER_MAX: run_.append(i); continue
    if len(run_) >= need: clutter_runs.append(dict(t_start_s=round(run_[0] * STEP_S, 2), t_end_s=round(run_[-1] * STEP_S, 2), max_badges=max(clutter_series[k] for k in run_)))
    run_ = []
clutter_ok = not clutter_runs
res = dict(min_required=MIN, samples=n, nth=NTH, label_instances=len(allr), min_ratio=round(min(allr), 2) if allr else None,
           p10_ratio=round(float(np.percentile(allr, 10)), 2) if allr else None, median_ratio=round(float(np.median(allr)), 2) if allr else None,
           held_failures=fails, ok=not fails, ghosts=ghosts[:20], ghost_ok=not ghost_fail, ghost_failures=ghost_fail[:10], safe_zone_violations=sz[:20], safe_zone_ok=not sz, safe_zone_transient=len(sz_all) - len(sz),
           overlap_clearance_px=CLEARANCE, overlap_ok=not ov_fails, overlap_min_clearance=overlap_min_clearance, overlap_violations=ov_fails,
           pop_ok=pop_ok, pop_entrances=len(pops), pop_snaps=snaps[:20], pop_handrolled_tracks=len(btracks),
           clutter_ok=clutter_ok, clutter_max_allowed=CLUTTER_MAX, clutter_peak=max(clutter_series, default=0), clutter_count=CLUTTER_COUNT, clutter_peak_all=max(clutter_all, default=0), clutter_violations=clutter_runs[:10],
           intro_edge_s=INTRO_S, preview=PREVIEW, raw_svg_text_probed=True)
if not fails:
    (OUT / "contrast_fail.png").unlink(missing_ok=True)
if fails:  # annotated evidence: one tile per failure (frame of its worst moment)
    tiles = []
    for fl in fails[:8]:
        i = int(round(fl["t_start_s"] * 30 / NTH)); im = Image.open(norms[i]).convert("RGB").resize((540, 960)); d = ImageDraw.Draw(im)
        x0, y0, x1, y1 = [v // 2 for v in fl["bbox"]]; d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], outline=(0, 255, 255), width=3)
        d.text((8, 8), f"{fl['t_start_s']}s ratio {fl['worst_ratio']}", fill=(0, 255, 255)); tiles.append(im)
    sheet = Image.new("RGB", (540 * len(tiles), 960)); [sheet.paste(t, (540 * k, 0)) for k, t in enumerate(tiles)]; sheet.save(OUT / "contrast_fail.png")
(OUT / "contrast.json").write_text(json.dumps(res, indent=1))
for d in (PD, OCC, ND):
    if d == ND and "--keep-norm" in sys.argv: continue   # preview.py reuses the normal stills for framing/hold/contact sheet
    [p.unlink() for p in d.glob("*.png")]; d.rmdir()
print(json.dumps({k: v for k, v in res.items() if k != "held_failures"}), "held_failures:", json.dumps(fails))
