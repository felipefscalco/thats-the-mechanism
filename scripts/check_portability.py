#!/usr/bin/env python3
"""Portability gate (L-31, L-34): blocks iterate.sh / build-episode.sh before rendering when a pipeline script
would only run on the machine that wrote it. Every failure here broke a fresh macOS checkout once:
  - absolute interpreter shebangs (#!/workspace/.../python)  -> "No such file or directory" for an existing script
  - absolute paths into another box's workspace (/workspace/ttm-...)
  - ffmpeg -vsync (removed in FFmpeg 7+; use -fps_mode)
  - GNU-only `sed -i "..."` / `sed -i '...'` (BSD/macOS sed needs a suffix argument)
and agent-safety rules (r10): no script may start an agent CLI with its permission checks bypassed
  - --dangerously-skip-permissions / bypassPermissions (Claude Code, Antigravity)
  - "--force" as an agent argument (cursor-agent auto-approves every command)
Usage: scripts/check_portability.py   (exit 1 + one line per violation)"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = sorted([*ROOT.glob("scripts/*.py"), *ROOT.glob("scripts/*.sh"), *ROOT.glob("remotion/*.mjs")])
OK_SHEBANG = re.compile(r"^#!(/usr/bin/env (python3|bash|sh|node)|/bin/(ba)?sh)\s*$")
RULES = [
    (re.compile(r"/workspace/"), "absolute path into another machine's workspace"),
    (re.compile(r"-vsync\b"), "ffmpeg -vsync was removed in FFmpeg 7+; use -fps_mode passthrough"),
    (re.compile(r"\bsed\s+-i\s+[\"']"), "GNU-only `sed -i \"...\"`; BSD/macOS sed needs `sed -i '' ...` (or edit with python)"),
    (re.compile(r"dangerously-skip-permissions|bypassPermissions"), "agent started with permission checks bypassed; use a tool allowlist (scripts/llm.py WRITE_TOOLS)"),
    (re.compile(r"[\"']--force[\"']\s*\]"), "agent CLI started with --force (auto-approves every command); use an allowlisted provider"),
]
SELF = Path(__file__).resolve()

bad = []
for f in FILES:
    if f.resolve() == SELF:
        continue
    lines = f.read_text(errors="replace").splitlines()
    if lines and lines[0].startswith("#!") and not OK_SHEBANG.match(lines[0]):
        bad.append(f"{f.relative_to(ROOT)}:1: non-portable shebang {lines[0]!r} (use #!/usr/bin/env python3|bash)")
    for i, line in enumerate(lines, 1):
        for rx, why in RULES:
            if rx.search(line):
                bad.append(f"{f.relative_to(ROOT)}:{i}: {why}")
for b in bad:
    print("PORTABILITY FAIL |", b)
if bad:
    sys.exit(1)
print(f"portability: PASS ({len(FILES) - 1} scripts)")
