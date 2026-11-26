#!/usr/bin/env python3
"""Fail-fast source gates (r10 efficiency, item E): the static checks qa.py would report anyway (scripts/static_gates.py),
run BEFORE the ~5 min render + ~10 min QA. iterate.sh skips the render when one fails (FORCE_RENDER=1 overrides).
Usage: scripts/static_check.py <CompId> <slug>     exit 1 + one FAIL line per failing check"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from static_gates import checks

comp_id, slug = sys.argv[1], sys.argv[2]
fails = [c for c in checks(comp_id, slug) if not c[1]]
for name, _, detail in fails:
    print(f"STATIC FAIL | {name} | {json.dumps(detail)[:300]}")
print(f"static gates {comp_id}: {'FAIL' if fails else 'PASS'} ({len(fails)} failing)")
sys.exit(1 if fails else 0)
