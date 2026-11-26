#!/usr/bin/env bash
# Pairwise ship test against the last approved render, plus a calibrated
# review and an optional Gauntlet --verify pass.
#
# The builder is not the judge (motion-video-kit). Ship only if B is preferred.
#
# Usage:
#   scripts/critic_ship.sh --a-suf v4 --b-suf v5 QR Elevator Sky
#   scripts/critic_ship.sh --a-dir /path/to/v4-renders --a-suf v4 --b-suf v5 \
#       --it QR=3,Elevator=3,Sky=4 --verify-name critic_v5_lite QR Elevator Sky
#
# Env: BACKEND (default gemini-api; or role / agy / claude ...), MODELS (default gemini-3-flash-preview,gemini-3.8-flash)
#      PYTHON (default python3)
# Free-tier budget is 20 requests/model/day (see docs/LESSONS.md L-22).
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

A_SUF=v4
B_SUF=v5
A_DIR="$ROOT/renders"
B_DIR="$ROOT/renders"
ITS=""
VERIFY_NAME=""
MODELS="${MODELS:-gemini-3-flash-preview,gemini-3.8-flash}"
PYTHON="${PYTHON:-python3}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --a-suf) A_SUF=$2; shift 2 ;;
    --b-suf) B_SUF=$2; shift 2 ;;
    --a-dir) A_DIR=$2; shift 2 ;;
    --b-dir) B_DIR=$2; shift 2 ;;
    --it) ITS=$2; shift 2 ;;
    --verify-name) VERIFY_NAME=$2; shift 2 ;;
    --models) MODELS=$2; shift 2 ;;
    --) shift; break ;;
    -*) echo "unknown option: $1" >&2; exit 2 ;;
    *) break ;;
  esac
done
[[ $# -gt 0 ]] || { echo "usage: $0 [--a-suf v4 --b-suf v5] [Id...]" >&2; exit 2; }

it_for() {
  local e=$1
  [[ -z "$ITS" ]] && { echo ""; return; }
  local IFS=,
  for pair in $ITS; do
    if [[ "$pair" == "$e"=* ]]; then echo "${pair#*=}"; return; fi
  done
  echo ""
}

for E in "$@"; do
  A="$A_DIR/${E}_${A_SUF}.mp4"
  B="$B_DIR/${E}_${B_SUF}.mp4"
  OUT="qa/$E/$B_SUF"
  mkdir -p "$OUT"
  [[ -f "$A" && -f "$B" ]] || { echo "missing $A or $B" >&2; exit 1; }

  "$PYTHON" scripts/critic.py "$E" --backend "${BACKEND:-gemini-api}" --compare "$A" --mp4 "$B" --out-dir "$OUT" \
    --name "cmp_A-${A_SUF}_B-${B_SUF}" --label "A=${A_SUF} B=${B_SUF}" --models "$MODELS"

  IT=$(it_for "$E")
  if [[ -z "$IT" ]]; then
    REPORT=$(ls -1 "$OUT"/report_it*.json 2>/dev/null | sort | tail -1 || true)
  else
    REPORT="$OUT/report_it${IT}.json"
  fi
  CAL_ARGS=(--mp4 "$B" --out-dir "$OUT" --name "critic_${B_SUF}" --label "$B_SUF" --models "$MODELS")
  [[ -n "${REPORT:-}" && -f "${REPORT:-}" ]] && CAL_ARGS+=(--qa-report "$REPORT")
  "$PYTHON" scripts/critic.py "$E" --backend "${BACKEND:-gemini-api}" "${CAL_ARGS[@]}"

  if [[ -n "$VERIFY_NAME" && -f "$OUT/${VERIFY_NAME}.json" ]]; then
    "$PYTHON" scripts/critic.py "$E" --backend "${BACKEND:-gemini-api}" --mp4 "$B" --out-dir "$OUT" \
      --name "critic_${B_SUF}_verify" --label "${B_SUF}-verify" \
      --verify "$OUT/${VERIFY_NAME}.json" --models "$MODELS"
  fi
done
echo SHIP_CRITIC_DONE
