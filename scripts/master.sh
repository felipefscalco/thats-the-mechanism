#!/usr/bin/env bash
# Final mastering: two-pass EBU R128 (linear) loudness with ffmpeg-normalize, video stream copied.
# Usage: scripts/master.sh <mp4> [episode-slug] [iteration]   (in place; timed into metrics as stage "master")
set -euo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"; IN="$1"; EP="${2:-x}"; IT="${3:-1}"
TMP="${IN%.mp4}.master.mp4"
python3 "$P/scripts/metrics.py" run --ep "$EP" --stage master --iter "$IT" --out "$IN" -- \
  "$P/tools/fn-venv/bin/ffmpeg-normalize" "$IN" -nt ebu -t -14 -tp -1.5 -lrt 7 -c:a aac -b:a 192k -ar 48000 -c:v copy -o "$TMP" -f -q
mv "$TMP" "$IN"; echo "mastered $IN"
