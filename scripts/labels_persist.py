#!/usr/bin/env python3
"""r8 labels-persist gate (Elevator v7 tie-break: "loses the CAR and CW bar-chart labels during the active comparison").
Every key label planned in shots.md (on-screen text column; "A / B" = alternatives) must be READ on the stage during its
shot, and once it has appeared it must stay readable for the rest of that shot (>= PERSIST of the later samples), or until a
later label of the same shot appears (sequential callouts; at least 1 s). Measured on the render with tesseract OCR (stage band y 290-1190, 2 fps),
so it catches labels that exist in code but are hidden, covered, clipped or faded out.
  ok   = every label seen in its shot and persists; brand card rows (shot == Card) are skipped
Usage: labels_persist.py <CompId> <slug> <mp4> [--json] [--out <dir>]"""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shotlib import ROOT, words, phrase_time, shots

_OCR_ENV = {**os.environ, "OMP_THREAD_LIMIT": "1"}   # tesseract spawns a thread per core; parallel calls thrash without this
FPS, PERSIST, TAIL_S = 2, 0.6, 0.5
STAGE = (0, 290, 1080, 900)          # x, y, w, h: content safe zone (captions band excluded)
SKIP_SHOTS = {"Card"}
def toks(s): return [t for t in re.findall(r"[A-Z0-9%]+", s.upper().replace("’", "'")) if len(t) >= 2 and t not in {"THE", "OF", "A", "IT", "IS"}]

def ocr_frames(mp4, d):
    x, y, w, h = STAGE
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp4), "-vf", f"fps={FPS},crop={w}:{h}:{x}:{y},format=gray",
                    str(d / "f_%05d.png")], check=True)
    def one(f):
        txt = " ".join(subprocess.run(["tesseract", str(f), "-", "--psm", m], capture_output=True, text=True, env=_OCR_ENV).stdout for m in ("11", "3", "6"))  # sparse + auto: each misses some labels
        return set(toks(txt)), re.sub(r"[^A-Z0-9%]", "", txt.upper())
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(os.cpu_count() or 4) as ex: return list(ex.map(one, sorted(d.glob("f_*.png"))))

def seen(label, frame):   # every content token of the label (alternative), fuzzy on 1 char for words >= 5,
    words_on, flat = frame   # or the whole label as a substring of the space-less OCR text (OCR fuses "CAR RISES")
    need = toks(label)
    if not need: return True
    if "".join(need) in flat: return True
    def hit(t): return t in words_on or (len(t) >= 5 and any(len(o) == len(t) and sum(a != b for a, b in zip(o, t)) <= 1 for o in words_on))
    return all(hit(t) for t in need)

def check(comp, slug, mp4):
    ws = words(slug); rows = shots(slug); dur = ws[-1]["end"] + 1.0
    starts = [phrase_time(ws, r["at"]) if r["at"] else 0.0 for r in rows]
    with tempfile.TemporaryDirectory() as td:
        frames = ocr_frames(mp4, Path(td))
    res = []
    for i, r in enumerate(rows):
        if r["shot"] in SKIP_SHOTS: continue
        t0, t1 = starts[i], (starts[i + 1] if i + 1 < len(rows) else dur)
        idx = [k for k in range(len(frames)) if t0 <= k / FPS < t1 - TAIL_S]   # the shot's exit transition is not judged
        H, F = [], []
        for lab in r["text"]:
            alts = [a.strip() for a in lab.split("/") if a.strip()]
            hits = [any(seen(a, frames[k]) for a in alts) for k in idx]
            H.append(hits); F.append(next((j for j, h in enumerate(hits) if h), None))
        for li, lab in enumerate(r["text"]):
            hits, first = H[li], F[li]
            # a label may hand over to a LATER label of the same shot (sequential callouts): judge it until that one appears
            nxt = [F[m] for m in range(li + 1, len(F)) if F[m] is not None and first is not None and F[m] > first]
            end = max(min(nxt), first + 2) if nxt else len(hits)
            later = hits[first:end] if first is not None else []
            frac = round(sum(later) / len(later), 2) if later else 0.0
            ok = first is not None and frac >= (0.5 if len(later) <= 2 else PERSIST)   # a 1 s handover callout may blink once
            res.append(dict(shot=r["n"], label=lab, window_s=[round(t0, 2), round(t1, 2)], first_seen_s=None if first is None else round(idx[first] / FPS, 2),
                            persist=frac, ok=ok))
    bad = [x for x in res if not x["ok"]]
    return dict(ok=not bad, labels=len(res), failing=bad, results=res)

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    r = check(a[0], a[1], a[2])
    if "--out" in sys.argv: Path(sys.argv[sys.argv.index("--out") + 1]).joinpath("labels_persist.json").write_text(json.dumps(r, indent=1))
    if "--json" in sys.argv: print(json.dumps(r, indent=1))
    else:
        print("labels_persist", a[0], "PASS" if r["ok"] else "FAIL", f"{r['labels'] - len(r['failing'])}/{r['labels']}")
        for b in r["failing"]: print("  ", b)
    sys.exit(0 if r["ok"] else 1)
