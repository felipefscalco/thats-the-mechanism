#!/usr/bin/env bash
# Synthesised ambient bed (original, no licence needed) + narration mix for ONE episode -> remotion/public/<slug>.wav
# Usage: scripts/mix_one.sh <slug> [chord: "f1 f2 f3 f4 f5" Hz]
set -euo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"; S="$1"; F="${2:-98 146.83 220 246.94 369.99}"
E="$P/episodes/$S"
# r9 payoff hold (gate: qa.py "end card ... payoff settled >= 1.5 s"; Sky v8 settled 0.4 s): the episode always ends with
# >= hold_s of settled payoff after the LAST spoken word, then the loop whip (LOOP_FRAMES + T_FRAMES = 0.8 s). The tail is
# computed from the aligned captions, so it holds for every episode; episodes/<slug>/tail.txt can only make it longer.
NARR="$E/narration_tail.wav"
TAIL=$(python3 - "$E" "$P/pipeline.config.json" <<'PY'
import json, subprocess, sys
e, cfg = sys.argv[1], json.load(open(sys.argv[2])).get("qa_gates", {}).get("payoff", {})
hold, whip, margin = cfg.get("hold_s", 1.5), 0.8, cfg.get("margin_s", 0.3)
w = json.load(open(f"{e}/captions.json")); w = w if isinstance(w, list) else w.get("words", w)
d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{e}/narration.wav"]))
try: manual = float(open(f"{e}/tail.txt").read().strip())
except Exception: manual = 0.0
print(round(max(manual, w[-1]["end"] + hold + whip + margin - d, 0.0), 3))
PY
)
ffmpeg -loglevel error -y -i "$E/narration.wav" -af "apad=pad_dur=$TAIL" "$NARR"
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$NARR"); st=$(python3 -c "print($d-1.2)")
set -- $F
expr="0.30*sin(2*PI*$1*t)+0.22*sin(2*PI*$2*t)*(0.6+0.4*sin(2*PI*0.07*t))+0.16*sin(2*PI*$3*t)*(0.5+0.5*sin(2*PI*0.11*t+1))+0.12*sin(2*PI*$4*t)*(0.5+0.5*sin(2*PI*0.05*t+2))+0.08*sin(2*PI*$5*t)*(0.5+0.5*sin(2*PI*0.13*t))"
ffmpeg -loglevel error -y -f lavfi -i "aevalsrc='$expr':s=48000:d=$d" -f lavfi -i "anoisesrc=color=pink:amplitude=0.05:d=$d:r=48000" \
  -filter_complex "[0][1]amix=inputs=2:weights=1 0.6,lowpass=f=1800,aecho=0.8:0.7:420|700:0.35|0.25,afade=t=in:d=0.4,afade=t=out:st=$st:d=1.2,volume=0.5" -ac 2 "$E/bed.wav"
# r5 dramatic beat: duck the bed to silence for ~0.3 s before "That's the mechanism." (Gemini technique; qa.py check 6e)
t1=$(python3 -c "
import json,re
w=json.load(open('$E/captions.json')); w=w if isinstance(w,list) else w.get('words',w)
n=lambda s: re.sub('[^a-z]','',s.lower())
print(next((w[i]['start'] for i in range(len(w)-2) if n(w[i]['text'])=='thats' and n(w[i+1]['text'])=='the' and n(w[i+2]['text']).startswith('mechanism')), -9))")
duck="volume='if(between(t,$t1-0.42,$t1+0.04),max(0,1-(t-($t1-0.42))/0.10),1)':eval=frame"
ffmpeg -loglevel error -y -i "$NARR" -i "$E/bed.wav" \
  -filter_complex "[1]volume=${BED_DB:--9}dB,$duck[b];[0]aformat=channel_layouts=stereo[v];[v][b]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89" -ar 48000 "$P/remotion/public/$S.wav"
echo "$S $d"
