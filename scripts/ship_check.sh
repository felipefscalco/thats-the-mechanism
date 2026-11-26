#!/usr/bin/env bash
# r6 judge role: agy (Antigravity) is the independent critic. The builder never judges its own render.
# Usage: scripts/ship_check.sh <CompId> <new.mp4> <prev.mp4> <qa-report.json> <out-dir>
#   1. pairwise gemini-3.8-flash-high: A = prev, B = new   (cmp_prev_vs_new.json)
#   2. swap order:                     A = new,  B = prev  (cmp_new_vs_prev_swap.json)
#   3. calibrated gemini-4-neon-high with --qa-report       (critic_cal.json)
#   4. scripts/lessons.py (merge general_rules -> docs/STYLE_RULES.md, active_rules_prompt.txt)
# SHIP = new preferred in at least one order and never preferred-against (ties allowed in the other order).
set -uo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"; PY="$P/.venv-tts/bin/python"
ID="$1"; NEW="$2"; PREV="$3"; QAR="$4"; OUT="$5"; mkdir -p "$OUT"
FAST="${CRITIC_FAST:-gemini-3.8-flash-high}"; DEEP="${CRITIC_DEEP:-gemini-4-neon-high}"
"$PY" "$P/scripts/critic.py" "$ID" --backend agy --models "$FAST" --compare "$PREV" --mp4 "$NEW" --qa-report "$QAR" --out-dir "$OUT" --name cmp_prev_vs_new --label ship &
"$PY" "$P/scripts/critic.py" "$ID" --backend agy --models "$FAST" --compare "$NEW" --mp4 "$PREV" --out-dir "$OUT" --name cmp_new_vs_prev_swap --label ship_swap &
wait
"$PY" "$P/scripts/critic.py" "$ID" --backend agy --models "$DEEP" --mp4 "$NEW" --qa-report "$QAR" --out-dir "$OUT" --name critic_cal --label ship_cal
"$PY" "$P/scripts/lessons.py" || "$PY" "$P/scripts/lessons.py" --local
"$PY" - "$OUT" <<'PYEOF'
import json, sys
from pathlib import Path
o = Path(sys.argv[1])
a = json.loads((o / "cmp_prev_vs_new.json").read_text()); b = json.loads((o / "cmp_new_vs_prev_swap.json").read_text())
new1 = a.get("preferred") == "B"; old1 = a.get("preferred") == "A"
new2 = b.get("preferred") == "A"; old2 = b.get("preferred") == "B"
ship = (new1 or new2) and not (old1 or old2)
cal = json.loads((o / "critic_cal.json").read_text()) if (o / "critic_cal.json").exists() else {}
res = dict(ship=ship, order1=dict(preferred="new" if new1 else "prev" if old1 else "tie", margin_new_minus_prev=a.get("weighted_margin_B_minus_A"), strength=a.get("preference_strength")),
           swap=dict(preferred="new" if new2 else "prev" if old2 else "tie", margin_new_minus_prev=(-b["weighted_margin_B_minus_A"] if b.get("weighted_margin_B_minus_A") is not None else None), strength=b.get("preference_strength")),
           calibrated=dict(overall=cal.get("overall_score"), verdict=cal.get("verdict"), model=cal.get("model")))
(o / "ship.json").write_text(json.dumps(res, indent=2)); print("SHIP" if ship else "NO-SHIP", json.dumps(res))
PYEOF
