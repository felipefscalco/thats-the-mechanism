#!/usr/bin/env python3
"""Contact sheet of style frames: one row per episode, columns A1..A4 | B1..B4. Usage: style_sheet.py <dir> [out.png] [--ep qr]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
D = Path(sys.argv[1]); out = Path(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else D / "contact_sheet.png"
eps = [sys.argv[sys.argv.index("--ep") + 1]] if "--ep" in sys.argv else ["qr", "elevator", "sky"]
TW, TH, GAP, HDR = 300, 533, 12, 60
try: F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
except Exception: F = ImageFont.load_default()
kinds = ["1-hook", "2-mechanism", "3-proof", "4-end"]
W = 8 * TW + 9 * GAP + GAP * 3; H = HDR + len(eps) * (TH + 40 + GAP) + GAP
sheet = Image.new("RGB", (W, H), (20, 22, 28)); d = ImageDraw.Draw(sheet)
d.text((GAP, 14), "LOOK A: current brand refined", fill=(255, 176, 32), font=F); d.text((4 * (TW + GAP) + 4 * GAP, 14), "LOOK B: illustrated (library + drawing-skill backdrops)", fill=(76, 201, 240), font=F)
for r, ep in enumerate(eps):
    for c, (look, k) in enumerate([(l, k) for l in "AB" for k in kinds]):
        p = D / f"{ep}_{look}_{k}.png"
        if not p.exists(): continue
        x = GAP + c * (TW + GAP) + (3 * GAP if look == "B" else 0); y = HDR + r * (TH + 40 + GAP)
        sheet.paste(Image.open(p).convert("RGB").resize((TW, TH), Image.LANCZOS), (x, y))
        d.text((x + 4, y + TH + 8), f"{ep.upper()} {look}{k}", fill=(243, 239, 230), font=F)
sheet.save(out); print(out)
