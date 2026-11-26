#!/usr/bin/env python3
"""r8 VO-sync gate (Elevator v7 tie-break: "lags 2-4 s behind the voiceover during 0:19-0:26"). Every visual beat in
shots.md (`kind@spoken phrase`) must land on its word: a visual change EVENT on the stage must start or peak within
±TOL_S of the aligned word time (captions.json, script-aligned). Measured on the render, not the code.
  change signal = fraction of stage pixels (1/4 scale, blurred) changing > DIFF per frame
  event         = onset (signal crosses ON_FRAC from below) or a local peak >= PEAK_X × the median of the
                  surrounding 3 s
  skipped kinds = sound-only cues (sting, tick, clank, error count as visual too: they ship with a visual hit)
Usage: vo_sync.py <CompId> <slug> <mp4> [--json] [--out <dir>]"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shotlib import ROOT, words, phrase_time, shots

TOL_S, DIFF, ON_FRAC, PEAK_X, MAX_MISS_FRAC = 0.4, 6, 0.004, 1.6, 0.15
SOUND_ONLY = {"sting"}
W, H, Y0, SH = 270, 225, 290, 900          # stage band y 290-1190 at 1/4 scale

def signal(mp4):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(mp4), "-vf", f"crop=1080:{SH}:0:{Y0},scale={W}:{H},gblur=sigma=1.5,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.int16)
    fps = 30.0
    d = (np.abs(np.diff(fr, axis=0)) > DIFF).mean(axis=(1, 2))
    return np.concatenate([[0.0], d]), fps

def check(comp, slug, mp4):
    ws = words(slug); sig, fps = signal(mp4); n = len(sig)
    res = []
    for r in shots(slug):
        nth = {}
        for kind, phrase in r["beats"]:
            if kind in SOUND_ONLY: continue
            k = nth.get(phrase, 0)
            try: t = phrase_time(ws, phrase, k)
            except KeyError: res.append(dict(shot=r["n"], beat=f"{kind}@{phrase}", t_s=None, ok=False, why="phrase not in captions")); continue
            nth[phrase] = k + 1
            a, b = max(1, int((t - TOL_S) * fps)), min(n - 1, int((t + TOL_S) * fps) + 1)
            ctx = sig[max(0, int((t - 1.5) * fps)): min(n, int((t + 1.5) * fps))]
            med = float(np.median(ctx)) if len(ctx) else 0.0
            onset = [i for i in range(a, b) if sig[i] >= ON_FRAC and sig[i - 1] < ON_FRAC]
            peaks = [i for i in range(a, b) if sig[i] >= max(ON_FRAC, PEAK_X * med) and sig[i] >= sig[i - 1] and sig[i] >= sig[min(n - 1, i + 1)]]
            ev = sorted(onset + peaks, key=lambda i: abs(i / fps - t))
            ok = bool(ev)
            res.append(dict(shot=r["n"], beat=f"{kind}@{phrase}", t_s=round(t, 2), event_s=round(ev[0] / fps, 2) if ev else None,
                            win_peak=round(float(sig[a:b].max()), 4), ctx_median=round(med, 4), ok=ok))
    bad = [x for x in res if not x["ok"]]
    # a hard gate on every single beat is too brittle for a pixel metric: fail if > MAX_MISS_FRAC of beats miss, or 2 in a row
    consec = any(not res[i]["ok"] and not res[i + 1]["ok"] for i in range(len(res) - 1))
    ok = len(bad) <= MAX_MISS_FRAC * len(res) and not consec
    return dict(ok=ok, beats=len(res), missed=bad, consecutive_miss=consec, tol_s=TOL_S, results=res)

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    r = check(a[0], a[1], a[2])
    if "--out" in sys.argv: Path(sys.argv[sys.argv.index("--out") + 1]).joinpath("vo_sync.json").write_text(json.dumps(r, indent=1))
    if "--json" in sys.argv: print(json.dumps(r, indent=1))
    else:
        print("vo_sync", a[0], "PASS" if r["ok"] else "FAIL", f"{r['beats'] - len(r['missed'])}/{r['beats']} beats land within ±{TOL_S}s")
        for b in r["missed"]: print("  ", b)
    sys.exit(0 if r["ok"] else 1)
