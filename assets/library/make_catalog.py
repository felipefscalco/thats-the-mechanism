#!/usr/bin/env python3
"""Thumbnails + catalog sheet for the asset library. Usage: make_catalog.py -> thumbs/*.png, catalog.png"""
from pathlib import Path
import cairosvg
from PIL import Image, ImageDraw, ImageFont
R = Path(__file__).resolve().parent; T = R / "thumbs"; T.mkdir(exist_ok=True)
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
items = []
for p in sorted((R / "svg").rglob("*.svg")):
    out = T / f"{p.parent.name}_{p.stem}.png"; cairosvg.svg2png(url=str(p), write_to=str(out), output_width=220); items.append((f"{p.parent.name}/{p.stem}", out))
for p in sorted((R / "icons").rglob("*.svg")):
    out = T / f"icon_{p.parent.name}_{p.stem}.png"; cairosvg.svg2png(url=str(p), write_to=str(out), output_width=96); items.append((f"{p.parent.name}/{p.stem}", out))
for p in sorted(T.glob("lottie_*.png")): items.append((f"lottie/{p.stem[7:]}", p))
for p in sorted((R / "backdrops").glob("*.jpg")): items.append((f"backdrop/{p.stem}", p))
cols, cw, ch = 8, 240, 270
sheet = Image.new("RGB", (cols * cw, ((len(items) + cols - 1) // cols) * ch), (23, 26, 34)); d = ImageDraw.Draw(sheet)
for i, (name, p) in enumerate(items):
    im = Image.open(p).convert("RGBA"); im.thumbnail((220, 220)); x, y = (i % cols) * cw, (i // cols) * ch
    sheet.paste(im, (x + (cw - im.width) // 2, y + 10 + (220 - im.height) // 2), im); d.text((x + 8, y + 240), name[:30], fill=(243, 239, 230), font=F)
sheet.save(R / "catalog.png"); print(len(items), "items")
