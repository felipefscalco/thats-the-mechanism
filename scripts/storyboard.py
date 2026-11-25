#!/usr/bin/env python3
"""Storyboard / stills gate (r5, shorts-kit "storyboard -> stills -> render" idea).
Renders one still every 1.5 s at 1/4 scale from the CURRENT code (one bundle, ~10x cheaper than a full render), tiles them with
timecode + the words being spoken, and writes qa/<Id>/<SUF>/storyboard.jpg + storyboard.md. Then checks the storyboard gate
(pipeline.config.json): human = waits for `scripts/gates.py approve <Id> storyboard ...`; auto = logs and continues.
Usage: SUF=v5 scripts/storyboard.py <CompositionId> <slug> [--every 45]"""
import json, os, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ID, SLUG = sys.argv[1], sys.argv[2]
EVERY = int(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 45
SUF = os.environ.get("SUF", "v5")
OUT = ROOT / "qa" / ID / SUF; OUT.mkdir(parents=True, exist_ok=True)
tmp = OUT / "_sb"; tmp.mkdir(exist_ok=True); [p.unlink() for p in tmp.glob("*")]
r = subprocess.run(["node", "probe_frames.mjs", ID, str(tmp), str(EVERY), "0.25", "{}"], cwd=ROOT / "remotion", capture_output=True, text=True)
if r.returncode: sys.exit(r.stderr[-1500:])
meta = json.loads(r.stdout.strip().splitlines()[-1]); fps = meta["fps"]
frames = sorted(tmp.glob("*.png"))
words = json.loads((ROOT / "episodes" / SLUG / "captions.json").read_text())
font = ImageFont.load_default()
tiles, rows_md = [], ["| # | t | spoken around this frame |", "|---|---|---|"]
for k, p in enumerate(frames):
    t = k * EVERY / fps
    said = " ".join(w["text"] for w in words if t - 0.75 <= w["start"] <= t + 0.75)
    im = Image.open(p).convert("RGB"); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, im.width, 18], fill=(0, 0, 0)); d.text((4, 3), f"{k:02d}  {t:5.1f}s", fill=(255, 200, 0), font=font)
    tiles.append(im); rows_md.append(f"| {k} | {t:.1f}s | {said} |")
cols = 8; w, h = tiles[0].size; rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * h), (20, 20, 24))
for i, im in enumerate(tiles): sheet.paste(im, ((i % cols) * w, (i // cols) * h))
sheet.save(OUT / "storyboard.jpg", quality=82)
(OUT / "storyboard.md").write_text(f"# Storyboard {ID} {SUF} (every {EVERY / fps:.1f}s)\n\n![](storyboard.jpg)\n\n" + "\n".join(rows_md) + "\n")
[p.unlink() for p in tmp.glob("*")]; tmp.rmdir()
print(f"storyboard -> {OUT / 'storyboard.jpg'} ({len(tiles)} stills)")
g = subprocess.run([sys.executable, str(ROOT / "scripts" / "gates.py"), "require", ID, "storyboard", "--artifact", str(OUT / "storyboard.jpg")])
sys.exit(g.returncode)
