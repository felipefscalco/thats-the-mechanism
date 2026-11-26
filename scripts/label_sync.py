#!/usr/bin/env python3
"""r9 word-to-label timing sync (Elevator v7 tie-break: "lags 2-4 s behind the voiceover during 0:19-0:26").
Every on-screen label planned in shots.md that ECHOES a spoken phrase must first appear within ±TOL_S of that phrase's
aligned word time (captions.json is aligned to the script). Measured on the render with OCR, so it judges what is on
screen, not what the code intends.
  echo      = the label's content tokens (crude stems) found in the captions inside its shot: >= half of them within a
              6-word span; time = first matched word. "A / B" alternatives are separate beats. An explicit
              `LABEL @spoken phrase` in shots.md overrides the automatic echo.
  first seen= coarse OCR at 2 fps over the shot (labels_persist), then refined at 10 fps around it
  skipped   = labels with no spoken echo, labels already on screen when their shot opens (the shot's context), and
              labels the persist gate never reads (that gate fails them)
Usage: label_sync.py <CompId> <slug> <mp4> [--json] [--out <dir>]"""
import json, os, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shotlib import words, phrase_time, shots
import labels_persist as LP

_OCR_ENV = {**os.environ, "OMP_THREAD_LIMIT": "1"}   # tesseract spawns a thread per core; parallel calls thrash without this
TOL_S, FINE_FPS, SPAN = 0.5, 10, 6
def stem(t):
    t = t.upper()
    for suf in ("ING", "ED", "ES", "S"):
        if len(t) > len(suf) + 2 and t.endswith(suf): return t[: -len(suf)]
    return t

def echo(label, ws, t0, t1):
    if "@" in label: return phrase_time(ws, label.split("@", 1)[1].strip()), "explicit"
    need = [stem(x) for x in LP.toks(label) if len(x) >= 3 or x.isdigit()]
    if not need: return None, None
    idx = [i for i, w in enumerate(ws) if t0 - 0.3 <= w["start"] < t1]
    best, score = None, 0
    for i in idx:   # the span that echoes the MOST label tokens wins (earliest on ties); it must start on a label token
        span = [stem(re.sub(r"[^A-Za-z0-9%]", "", w["text"])) for w in ws[i:i + SPAN]]
        n = len({x for x in span if x in need})
        if span and span[0] in need and n >= max(1, -(-len(set(need)) * 3 // 5)) and n > score:
            best, score = ws[i]["start"], n
    return best, "auto" if best is not None else None

def ocr_at(mp4, times):
    x, y, w, h = LP.STAGE
    def one(t):
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "f.png"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", str(mp4), "-frames:v", "1", "-vf", f"crop={w}:{h}:{x}:{y},format=gray", str(f)], check=True)
            txt = " ".join(subprocess.run(["tesseract", str(f), "-", "--psm", m], capture_output=True, text=True, env=_OCR_ENV).stdout for m in ("11", "3"))
        return set(LP.toks(txt)), re.sub(r"[^A-Z0-9%]", "", txt.upper())
    with ThreadPoolExecutor(8) as ex: return list(ex.map(one, times))

def check(comp, slug, mp4):
    ws = words(slug); rows = shots(slug); dur = ws[-1]["end"] + 1.0
    starts = [phrase_time(ws, r["at"]) if r["at"] else 0.0 for r in rows]
    with tempfile.TemporaryDirectory() as td: frames = LP.ocr_frames(mp4, Path(td))
    res = []
    for i, r in enumerate(rows):
        if r["shot"] in LP.SKIP_SHOTS: continue
        t0, t1 = starts[i], (starts[i + 1] if i + 1 < len(rows) else dur)
        for lab in r["text_raw"]:
            for alt in [a.strip() for a in lab.split("@")[0].split("/") if a.strip()]:
                full = alt + ("@" + lab.split("@", 1)[1] if "@" in lab else "")
                tw, how = echo(full, ws, t0, t1)
                if tw is None: res.append(dict(shot=r["n"], label=alt, skipped="no spoken echo")); continue
                ks = [k for k in range(len(frames)) if t0 <= k / LP.FPS < t1]
                first = next((k for k in ks if LP.seen(alt, frames[k])), None)
                if first is None: res.append(dict(shot=r["n"], label=alt, word_s=round(tw, 2), skipped="never read (labels_persist judges it)")); continue
                if first / LP.FPS <= t0 + 0.5:
                    res.append(dict(shot=r["n"], label=alt, word_s=round(tw, 2), skipped="on screen when the shot opens")); continue
                fine = [max(0.0, first / LP.FPS - 0.6 + j / FINE_FPS) for j in range(int(0.7 * FINE_FPS) + 1)]
                fr = ocr_at(mp4, fine)
                ts = next((t for t, f in zip(fine, fr) if LP.seen(alt, f)), first / LP.FPS)
                dt = round(ts - tw, 2)
                res.append(dict(shot=r["n"], label=alt, echo=how, word_s=round(tw, 2), first_seen_s=round(ts, 2), dt_s=dt, ok=abs(dt) <= TOL_S))
    judged = [x for x in res if "ok" in x]; bad = [x for x in judged if not x["ok"]]
    return dict(ok=not bad, judged=len(judged), failing=bad, tol_s=TOL_S, results=res)

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    r = check(a[0], a[1], a[2])
    if "--out" in sys.argv: Path(sys.argv[sys.argv.index("--out") + 1]).joinpath("label_sync.json").write_text(json.dumps(r, indent=1))
    if "--json" in sys.argv: print(json.dumps(r, indent=1))
    else:
        print("label_sync", a[0], "PASS" if r["ok"] else "FAIL", f"{r['judged'] - len(r['failing'])}/{r['judged']} echoed labels within ±{TOL_S}s")
        for x in r["results"]: print("  ", x)
    sys.exit(0 if r["ok"] else 1)
