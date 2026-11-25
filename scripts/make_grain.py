#!/usr/bin/env python3
"""Procedural film-grain tiles (ours, CC0) for the GrainOverlay component.
Replaces the Texturelabs grain idea: their terms forbid sharing/redistributing textures, so we generate our own.
Writes remotion/public/grain/g0..g3.png (360x640 greyscale, scaled 3x; overlay blend)."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

out = Path(__file__).resolve().parent.parent / "remotion" / "public" / "grain"
out.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(20261125)
for i in range(4):
    n = rng.normal(0.5, 0.16, (640, 360)).clip(0, 1)  # grey L tile; used with mix-blend-mode: overlay (mid-grey = neutral)
    img = Image.fromarray((n * 255).astype("uint8"), "L").filter(ImageFilter.GaussianBlur(0.5))
    img.save(out / f"g{i}.png", optimize=True)
print("grain tiles ->", out)
