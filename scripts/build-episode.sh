#!/usr/bin/env bash
# Full pipeline for one episode, every stage timed into metrics/runs.jsonl (wall, CPU, peak RAM, output size, $0).
# Usage: scripts/build-episode.sh <slug> <CompositionId> [iteration=1] [--skip-tts]
#   script.txt -> TTS (Kokoro am_michael 1.08) -> loudnorm -14 LUFS -> captions (whisper.cpp DTW, fallback faster-whisper)
#   -> bed + mix -> durations.json -> shot lint -> render renders/<Id>_v2.mp4 -> QA (qa/<Id>/report_it<N>.json)
set -euo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"; S="$1"; ID="$2"; IT="${3:-1}"; PY="$P/.venv-tts/bin/python"; M="python3 $P/scripts/metrics.py run --ep $S"
E="$P/episodes/$S"; cd "$P"
if [[ "${4:-}" != "--skip-tts" ]]; then
  $M --stage tts --out "$E/narration_raw.wav" -- $PY scripts/tts.py am_michael 1.08 "$E/script.txt"
  $M --stage loudnorm --out "$E/narration.wav" -- bash -c "ffmpeg -loglevel error -y -i '$E/narration_raw.wav' -af loudnorm=I=-14:TP=-1.5:LRA=7 -ar 48000 -ac 1 '$E/narration.wav' && ffmpeg -loglevel error -y -i '$E/narration.wav' -ar 16000 -ac 1 '$E/narration16k.wav'"
fi
$M --stage captions --out "$E/captions.json" -- $PY scripts/captions.py "episodes/$S"
cp "$E/captions.json" "remotion/src/$S.captions.json"
$M --stage mix --out "remotion/public/$S.wav" -- scripts/mix_one.sh "$S"
python3 - "$S" <<'PY'
import json, subprocess, sys
s = sys.argv[1]; p = "remotion/src/durations.json"; d = json.load(open(p))
d[s] = round(float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"remotion/public/{s}.wav"])), 6)
json.dump(d, open(p, "w")); print("duration", s, d[s])
PY
python3 scripts/lint_shots.py "$S" || echo "LINT: fix shots.md before publishing (render continues for review)"
(cd remotion && npx tsc --noEmit -p .)
scripts/render.sh "$ID" v2 "$IT" "$S"
$M --stage qa --iter "$IT" -- scripts/qa.py "$ID" "$S" "$IT"
