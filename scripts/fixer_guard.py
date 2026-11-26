#!/usr/bin/env python3
"""Fixer allowlist guard (r7). The fixer role may only tune values, never restructure a scene.

ALLOWED  copy (string literals / ALL-CAPS JSX text), numbers (font/element size, clearance, edge margin, position, timing),
         colour swaps to an existing palette token or a colour already in the file, easing swaps (EASE.* / Easing.*),
         Label <-> TagLabel (adds an ink backing for contrast), and inserting/removing a value prop
         (size, fontSize, color, fill, o, opacity, anchor, weight, x, y, dx, dy, strokeWidth, stroke, letterSpacing).
FORBIDDEN new or removed elements/shots/components, new logic, layout redesign (any non-value token change), new colours
         (palette), and ANY change on a camera line (cam/camera/zoom/punch/push/whip/glide/orbit/pull/scale(...) on a Shot).
Usage:   fixer_guard.py <before.tsx> <after.tsx> [--json]      exit 0 = allowed, 3 = rejected (caller reverts)
"""
from __future__ import annotations
import difflib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOK = re.compile(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'|\d+\.\d*|\.\d+|\d+|[A-Za-z_$][\w$]*|==?=?|=>|[^\s\w]')
NUM = re.compile(r"^(\d+\.\d*|\.\d+|\d+)$")
STR = re.compile(r"^(\"|').*(\"|')$", re.S)
HEX = re.compile(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b")
CAMERA = re.compile(r"\b(cam|camera|zoom|punch|push|whip|whipUp|glide|orbit|pull|dolly|Camera)\b")
ALLOWED_PROPS = {"size", "fontSize", "color", "fill", "o", "opacity", "anchor", "weight", "x", "y", "dx", "dy",
                 "strokeWidth", "stroke", "letterSpacing", "textColor", "w", "fontWeight"}
OPS = {"-", "+", "*", "/", "."}


def palette() -> set[str]:
    t = (ROOT / "remotion/src/brand/tokens.ts").read_text()
    names = set(re.findall(r"\b([a-z][a-z0-9]*)\s*:\s*\"#", t))
    return names


def ease_names() -> set[str]:
    t = (ROOT / "remotion/src/brand/timing.ts").read_text()
    m = re.search(r"export const EASE = \{(.*?)\n\};", t, re.S)
    names = set(re.findall(r"\b([A-Z_]{2,})\s*:", m.group(1))) if m else set()
    return names | {"EASE", "Easing", "in", "out", "inOut", "cubic", "quad", "exp", "sin", "back", "bezier", "elastic", "linear", "ease", "circle", "poly"}


def tokens(src: str):
    out = []
    for m in TOK.finditer(src):
        out.append((m.group(0), src.count("\n", 0, m.start()) + 1))
    return out


def is_value(tok: str, allowed_ident: set[str]) -> bool:
    return bool(NUM.match(tok) or STR.match(tok) or tok in OPS or tok in allowed_ident or re.fullmatch(r"[A-Z][A-Z0-9_]+", tok))


def check(before: str, after: str) -> dict:
    a, b = tokens(before), tokens(after)
    ta, tb = [t for t, _ in a], [t for t, _ in b]
    lines_a, lines_b = before.splitlines(), after.splitlines()
    pal = palette(); ident = pal | ease_names() | {"C", "Label", "TagLabel", "true", "false"}
    known_hex = {h.upper() for h in HEX.findall(before)} | {h.upper() for h in HEX.findall((ROOT / "remotion/src/brand/tokens.ts").read_text())}
    viol = []
    sm = difflib.SequenceMatcher(a=ta, b=tb, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal": continue
        old, new = ta[i1:i2], tb[j1:j2]
        ln_b = b[j1][1] if j1 < len(b) else (b[-1][1] if b else 0)
        ln_a = a[i1][1] if i1 < len(a) else (a[-1][1] if a else 0)
        ctx = (lines_a[ln_a - 1] if 0 < ln_a <= len(lines_a) else "") + " " + (lines_b[ln_b - 1] if 0 < ln_b <= len(lines_b) else "")
        rec = dict(line=ln_b, old=" ".join(old)[:120], new=" ".join(new)[:120])
        if CAMERA.search(ctx):
            viol.append(dict(rec, reason="camera line is off-limits for the fixer")); continue
        changed = old + new
        if all(is_value(t, ident) for t in changed):
            continue
        # prop insertion/removal:  IDENT = { values }  |  IDENT = "str"
        seq = new if op == "insert" else old if op == "delete" else None
        if seq is not None and _is_prop_run(seq, ident):
            continue
        if op == "replace" and _is_prop_run(new, ident) and _is_prop_run(old, ident):
            continue
        viol.append(dict(rec, reason="structural change (only values, copy, colours, easing and value props are allowed)"))
    for h in sorted({h.upper() for h in HEX.findall(after)} - known_hex):
        viol.append(dict(line=None, old="", new=h, reason="new colour outside the palette"))
    return dict(ok=not viol, violations=viol, changed_ops=sum(1 for o in sm.get_opcodes() if o[0] != "equal"))


def _is_prop_run(seq, ident) -> bool:
    # alignment-agnostic: difflib may shift an inserted `name={v}` run by a token (`} name={v`)
    nv = [t for t in seq if not is_value(t, ident)]
    props = [t for t in nv if t in ALLOWED_PROPS]
    rest = [t for t in nv if t not in ALLOWED_PROPS]
    if props and all(t in "={}" for t in rest) and rest.count("=") == len(props) and rest.count("{") == rest.count("}") <= len(props):
        return True
    i = 0
    if not seq: return True
    while i < len(seq):
        if seq[i] not in ALLOWED_PROPS: return False
        if i + 1 >= len(seq) or seq[i + 1] != "=": return False
        if i + 2 < len(seq) and STR.match(seq[i + 2]): i += 3; continue
        if i + 2 < len(seq) and seq[i + 2] == "{":
            k = seq.index("}", i + 2) if "}" in seq[i + 2:] else -1
            if k < 0 or not all(is_value(t, ident) for t in seq[i + 3:k]): return False
            i = k + 1; continue
        return False
    return True


def main() -> int:
    before, after = Path(sys.argv[1]).read_text(), Path(sys.argv[2]).read_text()
    r = check(before, after)
    print(json.dumps(r, indent=1) if "--json" in sys.argv else ("ALLOWED" if r["ok"] else "REJECTED " + json.dumps(r["violations"][:8])))
    return 0 if r["ok"] else 3


if __name__ == "__main__":
    sys.exit(main())
