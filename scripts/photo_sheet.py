#!/usr/bin/env python3
"""Contact sheet of OK photo candidates for a human/bot visual check (people, logos, readability). Usage: photo_sheet.py <slug> [regex]"""
import io, json, re, sys
from pathlib import Path
import requests
from PIL import Image, ImageDraw
R = Path(__file__).resolve().parents[1]; slug = sys.argv[1]; rx = re.compile(sys.argv[2] if len(sys.argv) > 2 else ".", re.I)
db = json.loads((R / f"assets/photos/_candidates/{slug}.json").read_text())
items = [c for c in db.values() if c["ok"] and rx.search(c["title"])][:16]
tiles = []
for i, c in enumerate(items):
    u = c["url"]
    try: im = Image.open(io.BytesIO(requests.get(u, headers={"User-Agent": "TTM/0.4"}, timeout=40).content)).convert("RGB")
    except Exception as e: print("fail", c["key"], e); continue
    im.thumbnail((400, 400)); t = Image.new("RGB", (400, 440), "white"); t.paste(im, ((400 - im.width) // 2, 0))
    ImageDraw.Draw(t).text((4, 404), f"{i}: {c['title'][:58]}", fill="black"); ImageDraw.Draw(t).text((4, 420), c["license"][:60], fill="black")
    tiles.append(t); print(i, c["key"])
cols = 4; sheet = Image.new("RGB", (400 * cols, 440 * ((len(tiles) + cols - 1) // cols)), "white")
for i, t in enumerate(tiles): sheet.paste(t, ((i % cols) * 400, (i // cols) * 440))
out = R / f"assets/photos/_candidates/{slug}_sheet.jpg"; sheet.save(out, quality=85); print(out)
