#!/usr/bin/env bash
# Usage: scripts/render.sh <CompositionId> [suffix] [iteration] [episode-slug]  -> renders/<Id>_<suffix|v2>.mp4 (timed into metrics/)
set -euo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"
ID="$1"; SUF="${2:-v2}"; IT="${3:-1}"
EP="${4:-}"; [[ -z "$EP" ]] && case "$ID" in QR) EP=01-qr-code;; Elevator) EP=02-elevator;; Sky) EP=03-sky;; *) EP="$ID";; esac
OUT="$P/renders/${ID}_${SUF}.mp4"
# r10: RENDER_CONCURRENCY=N overrides the default 6. Not raised by default: on battery the r10 benchmark could not
# separate concurrency from throttling, and oversubscribing the 15 cores made the main render 3.8x slower.
CONC="${RENDER_CONCURRENCY:-6}"
cd "$P/remotion"
python3 "$P/scripts/metrics.py" run --ep "$EP" --stage render --iter "$IT" --out "$OUT" -- \
  npx remotion render "$ID" "$OUT" --codec=h264 --crf=18 --audio-codec=aac --audio-bitrate=192k --concurrency=$CONC --log=error
echo "rendered $OUT"
