#!/usr/bin/env python3
"""Look-B drawn backdrop for 05-anc-headphones: violet high-altitude dusk with clouds (flatvector, MIT claude-drawing-skill)."""
import sys, json
from pathlib import Path
sys.path.insert(0, "/workspace/skill-eval/claude-drawing-skill/lib")
from flatvector import FlatVector
R = Path(__file__).resolve().parent
PUB = R.parents[2] / "remotion" / "public" / "library"
W, H = 1080, 1920
fv = FlatVector(W, H, seed=21); fv.backdrop("#1C1838")
for y, col in [(0, "#1C1838"), (420, "#2A2352"), (800, "#3B3169"), (1150, "#52458A"), (1500, "#6D5CA8")]:
    fv.fill(fv.rect(0, y, W, H), col, texture=0.4)
fv.stars(60, box=(0, 0, W, 700), size=(1.0, 2.4))
fv.glow(300, 1250, 420, 260, "#B7A8FF", rings=4, alpha=0.12)
fv.cloud(220, 980, 320, seed=3); fv.cloud(840, 1380, 260, seed=4); fv.cloud(520, 1640, 380, seed=5)
fv.save(str(R / "anc_dusk.jpg")); fv.save(str(PUB / "anc_dusk.jpg"))
print("ok")
