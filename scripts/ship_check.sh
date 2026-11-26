#!/usr/bin/env bash
# Judge (r7, vendor-neutral). The builder never judges its own render. Providers/models come from pipeline.config.json
# llm.roles (critic, critic_deep, critic_tiebreak); override per run with LLM_CRITIC=provider:model etc.
# Usage: scripts/ship_check.sh <CompId> <new.mp4> <prev.mp4> <new-qa-report.json> <out-dir> [prev-qa-report.json]
#   1. pairwise critic, A = prev, B = new     (cmp_prev_vs_new.json)
#   2. swap order,      A = new,  B = prev    (cmp_new_vs_prev_swap.json)
#   3. if undecided: critic_tiebreak pairwise (cmp_tiebreak.json), then per-gate deltas (scripts/ship_decide.py)
#   4. calibrated critic_deep with the QA report (critic_cal.json), then scripts/lessons.py (clusterer role)
set -uo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"; PY="$P/.venv-tts/bin/python"; [[ -x "$PY" ]] || PY=python3
ID="$1"; NEW="$2"; PREV="$3"; QAR="$4"; OUT="$5"; PQA="${6:-}"; mkdir -p "$OUT"
"$PY" "$P/scripts/critic.py" "$ID" --role critic --compare "$PREV" --mp4 "$NEW" --qa-report "$QAR" --out-dir "$OUT" --name cmp_prev_vs_new --label ship &
"$PY" "$P/scripts/critic.py" "$ID" --role critic --compare "$NEW" --mp4 "$PREV" --out-dir "$OUT" --name cmp_new_vs_prev_swap --label ship_swap &
wait
"$PY" "$P/scripts/ship_decide.py" "$OUT" >/dev/null
if "$PY" -c "import json,sys; sys.exit(0 if json.load(open('$OUT/ship.json')).get('undecided') else 1)"; then
  "$PY" "$P/scripts/critic.py" "$ID" --role critic_tiebreak --compare "$PREV" --mp4 "$NEW" --qa-report "$QAR" --out-dir "$OUT" --name cmp_tiebreak --label ship_tiebreak
fi
"$PY" "$P/scripts/critic.py" "$ID" --role critic_deep --mp4 "$NEW" --qa-report "$QAR" --out-dir "$OUT" --name critic_cal --label ship_cal
"$PY" "$P/scripts/lessons.py" || "$PY" "$P/scripts/lessons.py" --local
"$PY" "$P/scripts/ship_decide.py" "$OUT" --new-qa "$QAR" ${PQA:+--prev-qa "$PQA"}
