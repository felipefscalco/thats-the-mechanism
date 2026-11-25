#!/usr/bin/env bash
# Usage: scripts/render.sh <CompositionId> [suffix] [iteration] [episode-slug]  -> renders/<Id>_<suffix|v2>.mp4 (timed into metrics/)
set -euo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"
ID="$1"; SUF="${2:-v2}"; IT="${3:-1}"
EP="${4:-}"; [[ -z "$EP" ]] && case "$ID" in QR) EP=01-qr-code;; Elevator) EP=02-elevator;; Sky) EP=03-sky;; *) EP="$ID";; esac
OUT="$P/renders/${ID}_${SUF}.mp4"
cd "$P/remotion"
python3 "$P/scripts/metrics.py" run --ep "$EP" --stage render --iter "$IT" --out "$OUT" -- \
  npx remotion render "$ID" "$OUT" --codec=h264 --crf=18 --audio-codec=aac --audio-bitrate=192k --concurrency=6 --log=error
echo "rendered $OUT"
