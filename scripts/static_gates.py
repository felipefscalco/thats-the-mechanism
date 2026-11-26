#!/usr/bin/env python3
"""Source-level gates shared by qa.py (full render) and preview.py (stills): run on the episode .tsx + brand kit, no render."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
HUD_RE = re.compile(r"[\"'>`]\s*((?:\d{1,2}:\d{2}(?::\d{2})?(?:[.:]\d{1,3})?)|REC\b[^\"'<`]{0,8}|T\s?[+-]\s?\d+[^\"'<`]{0,6}|\d+\s?FPS|ISO\s?\d+|HUD\b)")


def checks(comp_id: str):
    out = []
    ep = ROOT / "remotion" / "src" / "episodes" / f"{comp_id}.tsx"
    if not ep.exists():
        return out
    src = ep.read_text()
    small = [int(m) for m in re.findall(r"<Label[^>]*\bsize=\{(\d+)\}", src) if int(m) < 30]
    out.append(("labels: minimum font size >= 30 px on all <Label> elements", not small, dict(min_allowed=30, small_labels=small)))
    raw_small = []
    for f in [ep, *sorted((ROOT / "remotion" / "src" / "brand").glob("*.tsx"))]:
        for ln, line in enumerate(f.read_text().splitlines(), 1):
            for m in re.finditer(r"fontSize(?:=\{|:\s*)(\d+)", line):
                if int(m.group(1)) < 30: raw_small.append(f"{f.name}:{ln}:{m.group(1)}px")
    out.append(("text: no raw SVG/CSS fontSize < 30 px (episode + brand kit)", not raw_small, dict(min_allowed=30, small=raw_small)))
    hud = sorted(set(HUD_RE.findall(src)))
    out.append(("text: no decorative HUD / fake timecode strings in the episode", not hud, dict(matches=hud)))
    return out
