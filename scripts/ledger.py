#!/usr/bin/env python3
"""Gauntlet ledger (r5, motion-video-kit): one row per round so fixes are traceable and the builder never grades itself.
  ledger.py add <Id> --round N --artifact PATH --critic qa/<Id>/<suf>/critic.json [--changes "..."] [--measured "..."]
  ledger.py show <Id>
Rows go to qa/<Id>/gauntlet.md: round | artifact | critic model + overall + verdict | top findings | changes made next | measured result."""
import argparse, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("id")
ap.add_argument("--round", type=int); ap.add_argument("--artifact", default=""); ap.add_argument("--critic", default="")
ap.add_argument("--changes", default=""); ap.add_argument("--measured", default="")
a = ap.parse_args()
f = ROOT / "qa" / a.id / "gauntlet.md"
if a.cmd == "show":
    print(f.read_text() if f.exists() else "(empty)"); raise SystemExit
if not f.exists():
    f.write_text(f"# Gauntlet ledger — {a.id}\n\n| round | artifact | critic | top findings | changes for next round | measured |\n|---|---|---|---|---|---|\n")
c = json.loads((ROOT / a.critic).read_text()) if a.critic else {}
items = c.get("weaknesses") or c.get("timestamped_issues") or []
top = "<br>".join(f"[{i['timestamp']}] {i['issue'][:110]}" for i in items[:4]).replace("|", "/")
crit = f"{c.get('model','')} {c.get('overall_score','')} {c.get('verdict','')}".strip()
with f.open("a") as fh:
    fh.write(f"| {a.round} | `{a.artifact}` | {crit} | {top} | {a.changes.replace('|','/')} | {a.measured.replace('|','/')} |\n")
print("ledger row added ->", f)
