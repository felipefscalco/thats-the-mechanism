#!/usr/bin/env python3
"""Raster backdrops for style frames, drawn with cloveric/claude-drawing-skill (MIT, lib/flatvector.py) in the brand palette.
Test of the skill for round 4 (see TESTS_R4.md). 1080x1920, then saved as JPG into remotion/public/library/."""
import sys, time, json
from pathlib import Path
sys.path.insert(0, "/workspace/skill-eval/claude-drawing-skill/lib")
from flatvector import FlatVector, tone, mix
R = Path(__file__).resolve().parent; P = json.loads((R.parent / "palette.json").read_text())
PUB = R.parents[2] / "remotion" / "public" / "library"
W, H = 1080, 1920
NAVY, INK = "#14203A", P["ink"]
out = {}

def city(fv, base, col, seed, lit=0.3):
    import random; rb = random.Random(seed); x = -20
    while x < W:
        w = rb.randint(90, 170); h = rb.randint(180, 520)
        m = fv.rect(x, base - h, x + w, base, round=4); fv.fill(m, col, lift=6)
        fv.face(m, (x + w * 0.62, base - h), (x + w * 0.62, base), tone(col, -0.25))
        for yy in range(base - h + 26, base - 30, 44):
            for xx in range(x + 14, x + w - 24, 30):
                if rb.random() < lit: fv.fill(fv.rect(xx, yy, xx + 14, yy + 20), P["amber"], alpha=0.85, texture=0)
        x += w + rb.randint(-10, 12)

t = time.time()
# 1 Sky: sunset (warm bands, low sun, hills, city) -- the "leftovers" half
fv = FlatVector(W, H, seed=5); fv.backdrop("#2A1E3F")
for i, (y, col) in enumerate([(0, "#2A1E3F"), (380, "#4B2A55"), (620, "#8A3B5C"), (820, "#D2553F"), (980, "#F08A3A"), (1090, "#FFB020")]):
    fv.fill(fv.rect(0, y, W, H), col, texture=0.4)
fv.glow(540, 1150, 520, 300, P["sunCore"], rings=4, alpha=0.16)
fv.fill(fv.circle(540, 1160, 120), P["sunCore"], texture=0)
fv.land([(-60, 1180), (300, 1150), (700, 1190), (1140, 1160)], "#5A2A48", lift=10)
city(fv, 1330, "#2B1B33", 3, lit=0.25)
fv.land([(-60, 1330), (540, 1320), (1140, 1335)], INK, lift=10, shadow=0.5)
fv.save(str(R / "sky_sunset.jpg")); out["sky_sunset"] = time.time() - t

t = time.time()
# 2 Sky: noon (bright blue, sun high, clouds) -- the "scattered blue" half
fv = FlatVector(W, H, seed=6); fv.backdrop("#2F7FD6")
for y, col in [(500, "#3E8FE0"), (900, "#5AA6EC"), (1150, "#83C0F3")]: fv.fill(fv.rect(0, y, W, H), col, texture=0.4)
fv.glow(800, 420, 300, 300, "#FFF4C8", rings=4, alpha=0.18); fv.fill(fv.circle(800, 420, 95), "#FFF4C8", texture=0)
fv.cloud(300, 640, 300, seed=1); fv.cloud(820, 880, 220, seed=2)
fv.land([(-60, 1240), (400, 1210), (800, 1250), (1140, 1225)], tone(P["eng"], -0.15), lift=10)
fv.land([(-60, 1320), (540, 1305), (1140, 1320)], P["engD"], lift=10)
fv.save(str(R / "sky_noon.jpg")); out["sky_noon"] = time.time() - t

t = time.time()
# 3 Elevator: dusk city with one tall office tower (where the elevator lives)
fv = FlatVector(W, H, seed=7); fv.backdrop(NAVY)
for y, col in [(700, "#1B2A48"), (1000, "#243556")]: fv.fill(fv.rect(0, y, W, H), col, texture=0.4)
fv.stars(70, box=(0, 0, W, 700), size=(1.0, 2.6))
fv.moon(860, 300, 70, rays=0, halo=True, craters=True)
city(fv, 1500, "#18223A", 11, lit=0.18)
m = fv.rect(330, 260, 750, 1500, round=6); fv.fill(m, "#2A3550", lift=12); fv.face(m, (600, 260), (600, 1500), "#1F2840")
for yy in range(300, 1460, 60):
    for xx in range(360, 720, 52):
        fv.fill(fv.rect(xx, yy, xx + 30, yy + 36), P["amber"] if (xx * 7 + yy) % 5 < 2 else "#3A4766", alpha=0.9, texture=0)
fv.land([(-60, 1500), (540, 1495), (1140, 1500)], INK, lift=10, shadow=0.5)
fv.save(str(R / "city_dusk.jpg")); out["city_dusk"] = time.time() - t

t = time.time()
# 4 QR: night street wall with a poster board (QR lives on posters/screens)
fv = FlatVector(W, H, seed=8); fv.backdrop("#101A2A")
fv.fill(fv.rect(0, 0, W, 1400), "#1A2638", texture=0.8)
for i in range(0, W, 120): fv.fill(fv.rect(i, 0, i + 4, 1400), "#223049", texture=0)
fv.glow(540, 300, 600, 380, P["tech"], rings=4, alpha=0.06)
fv.land([(-60, 1400), (540, 1395), (1140, 1400)], "#0C121C", lift=10, shadow=0.5)
fv.dashes((0, 1440, W, 1900), ["#1A2638", "#22314A"], n=12, seed=2, horizon=1400)
fv.save(str(R / "street_wall.jpg")); out["street_wall"] = time.time() - t

PUB.mkdir(parents=True, exist_ok=True)
for k in out: (PUB / f"{k}.jpg").write_bytes((R / f"{k}.jpg").read_bytes())
print(json.dumps({k: round(v, 1) for k, v in out.items()}))
