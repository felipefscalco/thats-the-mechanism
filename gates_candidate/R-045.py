#!/usr/bin/env python3
"""R-045 caption word spacing + orphan gate (backlog: voice_captions).

Rule: consecutive caption words keep an explicit horizontal gap, and the last caption line never ends in a lone
1-2 character orphan word ("a", "of").
Measurement: every 0.2 s the caption band (y 1210-1450, see AGENTS.md safe zones) is OCR'd with tesseract (tsv,
psm 6). Word boxes are grouped into lines by `line_num`; a violation is
  (gap)    two adjacent words on one line with a horizontal gap < MIN_GAP px (bbox includes the black stroke, a healthy
           space measures ~20+ px), or
  (orphan) a caption of >= 2 lines whose last line is a single word of <= 2 alphanumeric characters.
Plus a pixel check that does not depend on OCR segmentation: on each text line, the bright fill columns are split into
glyph runs; if the line has a run wider than MAX_RUN px with no space-sized gap (>= SPACE_PX) inside it while the
OCR saw >= 2 words in it, the words were glued ("do themicrowaves") and it is reported as a gap violation.
"""
import json, os, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from PIL import Image

Y0, Y1 = 1210, 1450          # caption band (captions live 1222-1440)
SAMPLE_FPS = 5               # 0.2 s grid
MIN_GAP = 8                  # px, minimum gap between adjacent words
ORPHAN_MAX_CHARS = 2
MIN_CONF = 40                # ignore OCR junk
MERGE_S = 0.6                # events closer than this with the same kind/text collapse into one

def _ocr(path):
    """-> list of (line_key, left, top, width, height, text) for confident words."""
    env = dict(os.environ, OMP_THREAD_LIMIT="1")
    r = subprocess.run(["tesseract", str(path), "stdout", "--psm", "6", "tsv"], capture_output=True, text=True, env=env)
    out = []
    for row in r.stdout.splitlines()[1:]:
        c = row.split("\t")
        if len(c) < 12 or c[0] != "5" or not c[11].strip():
            continue
        try:
            if float(c[10]) < MIN_CONF: continue
            out.append(((int(c[2]), int(c[3]), int(c[4])), int(c[6]), int(c[7]), int(c[8]), int(c[9]), c[11].strip()))
        except ValueError:
            continue
    return out

def _violations(words, img):
    """Per-frame violations: list of dict(kind, text, ...)."""
    lines = {}
    for w in words:
        lines.setdefault(w[0], []).append(w)
    ordered = [sorted(v, key=lambda w: w[1]) for _, v in sorted(lines.items(), key=lambda kv: kv[1][0][2])]
    bad = []
    # (gap) OCR boxes too close
    for ln in ordered:
        for a, b in zip(ln, ln[1:]):
            gap = b[1] - (a[1] + a[3])
            if gap < MIN_GAP:
                bad.append(dict(kind="gap", text=f"{a[5]} {b[5]}", gap_px=gap))
    # (gap) glued words: wide text run without any space-sized hole (pixel check, bright fill only)
    g = np.asarray(img.convert("RGB"), int)
    fill = (g.min(axis=2) > 200) | ((g[..., 0] > 200) & (g[..., 1] > 120) & (g[..., 2] < 90))  # white or amber
    for ln in ordered:
        if len(ln) < 2: continue
        top = min(w[2] for w in ln); bot = max(w[2] + w[4] for w in ln)
        cols = fill[max(0, top):bot].any(axis=0)
        xs = np.flatnonzero(cols)
        if xs.size == 0: continue
        h = bot - top
        gaps = [int(b - a - 1) for a, b in zip(xs, xs[1:]) if b - a > 1]
        space_px = 0.18 * h                      # a real space is ~ 0.3-0.4 of line height in fill pixels
        spaces = sum(1 for x in gaps if x >= space_px)
        if spaces < len(ln) - 1:                 # OCR found more words than the pixels have spaces
            bad.append(dict(kind="gap", text=" ".join(w[5] for w in ln), gap_px=max([x for x in gaps if x < space_px], default=0)))
    # (orphan) last line is one tiny word
    if len(ordered) >= 2 and len(ordered[-1]) == 1:
        t = re.sub(r"\W", "", ordered[-1][0][5])
        if 0 < len(t) <= ORPHAN_MAX_CHARS:
            bad.append(dict(kind="orphan", text=ordered[-1][0][5]))
    return bad

def check(mp4: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="r045_") as tmp:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-vf", f"fps={SAMPLE_FPS},crop=1080:{Y1 - Y0}:0:{Y0}",
                        "-fps_mode", "passthrough", f"{tmp}/f_%04d.png"], check=True)
        files = sorted(Path(tmp).glob("f_*.png"))
        with ThreadPoolExecutor(4) as ex:
            ocr = list(ex.map(_ocr, files))
        events = []
        for i, (f, words) in enumerate(zip(files, ocr)):
            t = i / SAMPLE_FPS
            with Image.open(f) as im:
                im.load()
                for v in _violations(words, im):
                    prev = next((e for e in reversed(events) if e["kind"] == v["kind"] and e["text"] == v["text"]), None)
                    if prev and t - prev["t_end_s"] <= MERGE_S:
                        prev["t_end_s"] = round(t, 2)
                    else:
                        events.append(dict(t_s=round(t, 2), t_end_s=round(t, 2), **v))
    return dict(ok=not events, events=events,
                detail=dict(samples=len(files), min_gap_px=MIN_GAP, orphan_max_chars=ORPHAN_MAX_CHARS,
                            gap_events=sum(e["kind"] == "gap" for e in events),
                            orphan_events=sum(e["kind"] == "orphan" for e in events)))

if __name__ == "__main__":
    print(json.dumps(check(sys.argv[1])))
