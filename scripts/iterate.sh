#!/usr/bin/env bash
# One render->QA iteration for the given compositions, all timed into metrics/.  Usage: scripts/iterate.sh <iter> QR Elevator Sky
set -uo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"; IT="$1"; shift
for ID in "$@"; do
  case "$ID" in QR) EP=01-qr-code;; Elevator) EP=02-elevator;; Sky) EP=03-sky;; *) EP=$(grep -l "\"$ID\"" "$P"/remotion/src/Root.tsx >/dev/null && grep -o "id=\"$ID\".*durations as Record<string, number>)\[\"[^\"]*" "$P/remotion/src/Root.tsx" | sed "s/.*\[\"//");; esac
  python3 "$P/scripts/lint_shots.py" "$EP" || echo "LINT FAILED ($EP) — continuing to render for review"
  "$P/scripts/render.sh" "$ID" v2 "$IT" "$EP"
  python3 "$P/scripts/metrics.py" run --ep "$EP" --stage qa --iter "$IT" -- "$P/scripts/qa.py" "$ID" "$EP" "$IT"
done
