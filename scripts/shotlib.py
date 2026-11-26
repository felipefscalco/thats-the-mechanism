"""Shared helpers: resolve spoken phrases to times (same rule as remotion/src/brand/timing.ts makeAt) and parse shots.md."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
norm = lambda s: re.sub(r"[^a-z0-9%']+", " ", s.lower().replace("’", "'")).split()

def words(slug):
    return json.load(open(ROOT / "episodes" / slug / "captions.json"))

def phrase_time(ws, phrase, nth=0):
    if not phrase.strip():
        return 0.0
    toks = [norm(w["text"]) for w in ws]
    flat = [(i, t) for i, ts in enumerate(toks) for t in ts]
    target = norm(phrase)
    hits = [flat[k][0] for k in range(len(flat) - len(target) + 1) if [t for _, t in flat[k:k + len(target)]] == target]
    if len(hits) <= nth:
        raise KeyError(f"phrase not found in captions: {phrase!r}")
    return ws[hits[nth]]["start"]

def shots(slug):
    rows = []
    for line in open(ROOT / "episodes" / slug / "shots.md"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 8 or not cells[0].isdigit():
            continue
        n, at, shot, subj, beats, text, tin, tout = cells
        beats = [tuple(b.strip().split("@", 1)) for b in beats.split(",") if "@" in b]
        rows.append(dict(n=int(n), at=at.strip("`"), shot=shot, subject=subj, beats=beats,
                         text=[t.split("@", 1)[0].strip() for t in text.split(";") if t.strip()],   # r9: "LABEL @spoken phrase" = explicit sync
                         text_raw=[t.strip() for t in text.split(";") if t.strip()], tin=tin, tout=tout))
    return rows
