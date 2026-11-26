#!/usr/bin/env bash
# One render->QA iteration for the given compositions, all timed into metrics/.  Usage: scripts/iterate.sh <iter> QR Elevator Sky
set -uo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"; IT="$1"; shift
python3 "$P/scripts/check_portability.py" || { echo "portability gate failed - fix before rendering (L-31/L-34)"; exit 1; }
PY="$P/.venv-tts/bin/python"; [[ -x "$PY" ]] || PY=python3   # qa.py needs numpy/soundfile/scipy from the venv
for ID in "$@"; do
  case "$ID" in QR) EP=01-qr-code;; Elevator) EP=02-elevator;; Sky) EP=03-sky;; *) EP=$(grep -l "\"$ID\"" "$P"/remotion/src/Root.tsx >/dev/null && grep -o "id=\"$ID\".*durations as Record<string, number>)\[\"[^\"]*" "$P/remotion/src/Root.tsx" | sed "s/.*\[\"//");; esac
  python3 "$P/scripts/lint_shots.py" "$EP" || echo "LINT FAILED ($EP) — continuing to render for review"
  # r10 (E) fail fast: the source-level gates qa.py would fail anyway, before ~5 min of render + ~10 min of QA
  if ! "$PY" "$P/scripts/static_check.py" "$ID" "$EP"; then
    if [[ "${FORCE_RENDER:-0}" == 1 ]]; then echo "static gates failed - rendering anyway (FORCE_RENDER=1)"
    else echo "STATIC GATES FAILED ($ID it$IT) - fix the source first, or FORCE_RENDER=1 to render anyway"; continue; fi
  fi
  "$P/scripts/render.sh" "$ID" "${SUF:-v2}" "$IT" "$EP" || { echo "RENDER FAILED ($ID it$IT) - skipping master + QA so a stale MP4 is not judged"; continue; }
  [[ "${MASTER:-0}" == 1 ]] && "$P/scripts/master.sh" "$P/renders/${ID}_${SUF:-v2}.mp4" "$EP" "$IT"
  python3 "$P/scripts/metrics.py" run --ep "$EP" --stage qa --iter "$IT" -- "$PY" "$P/scripts/qa.py" "$ID" "$EP" "$IT"
done
