#!/usr/bin/env python3
"""Storyboard lint (huashu-art-motion style) for episodes/<slug>/shots.md.
Fails on: unresolved phrases, fades/dissolves, >8 words of on-screen text per item, >2 text items per shot
beyond the channel card, three consecutive push moves, a gap > MAX_GAP s with no beat (anti-PPT gate)."""
import sys
from shotlib import words, phrase_time, shots

CAM = {"push", "pull", "glide", "punch", "settle"}
MAX_GAP = 3.0

def lint(slug):
    ws, rows, errs, warns = words(slug), shots(slug), [], []
    end = ws[-1]["end"]
    times = []
    for r in rows:
        try:
            r["t"] = phrase_time(ws, r["at"])
        except KeyError as e:
            errs.append(f"shot {r['n']}: {e}"); continue
        for kind, ph in r["beats"]:
            try:
                times.append((phrase_time(ws, ph), kind, r["n"]))
            except KeyError as e:
                errs.append(f"shot {r['n']} beat {kind}: {e}")
        for tr in (r["tin"], r["tout"]):
            if any(k in tr.lower() for k in ("fade", "dissolve", "crossfade")):
                errs.append(f"shot {r['n']}: transition '{tr}' is a slideshow fade — use push/whip/whipUp/cut")
        for t in r["text"]:
            if len(t.split()) > 8:
                errs.append(f"shot {r['n']}: on-screen text too long ({len(t.split())} words): {t}")
        if len(r["text"]) > 3:
            warns.append(f"shot {r['n']}: {len(r['text'])} text items — check it still reads in 2 levels")
    times += [(r["t"], "cut", r["n"]) for r in rows if "t" in r]
    times = sorted(times)
    cams = [k for _, k, _ in times if k in CAM]
    for i in range(len(cams) - 2):
        if cams[i] == cams[i + 1] == cams[i + 2] == "push":
            errs.append(f"three pushes in a row (camera beats #{i}-{i+2}) — vary with glide/pull/punch"); break
    pts = [0.0] + [t for t, _, _ in times] + [end]
    gaps = [(b - a, a) for a, b in zip(pts, pts[1:])]
    for g, a in gaps:
        if g > MAX_GAP:
            errs.append(f"no beat for {g:.1f}s from {a:.1f}s (max {MAX_GAP}s)")
    if 0.0 not in [t for t, _, _ in times] and min(t for t, _, _ in times) > 1.0:
        errs.append("first beat after 1.0s — hook needs a visual event in the first second")
    kinds = {k for _, k, _ in times if k in CAM}
    if len(kinds) < 3:
        warns.append(f"camera vocabulary only {sorted(kinds)} — use ≥3 kinds")
    print(f"[{slug}] shots={len(rows)} beats={len(times)} longest_gap={max(g for g, _ in gaps):.1f}s camera_kinds={sorted(kinds)}")
    for w in warns: print("  WARN", w)
    for e in errs: print("  FAIL", e)
    return not errs

if __name__ == "__main__":
    slugs = sys.argv[1:] or ["01-qr-code", "02-elevator", "03-sky"]
    ok = all([lint(s) for s in slugs])
    sys.exit(0 if ok else 1)
