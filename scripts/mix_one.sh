#!/usr/bin/env bash
# Synthesised ambient bed (original, no licence needed) + narration mix for ONE episode -> remotion/public/<slug>.wav
# Usage: scripts/mix_one.sh <slug> [chord: "f1 f2 f3 f4 f5" Hz]
set -euo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"; S="$1"; F="${2:-98 146.83 220 246.94 369.99}"
E="$P/episodes/$S"
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$E/narration.wav"); st=$(python3 -c "print($d-1.2)")
set -- $F
expr="0.30*sin(2*PI*$1*t)+0.22*sin(2*PI*$2*t)*(0.6+0.4*sin(2*PI*0.07*t))+0.16*sin(2*PI*$3*t)*(0.5+0.5*sin(2*PI*0.11*t+1))+0.12*sin(2*PI*$4*t)*(0.5+0.5*sin(2*PI*0.05*t+2))+0.08*sin(2*PI*$5*t)*(0.5+0.5*sin(2*PI*0.13*t))"
ffmpeg -loglevel error -y -f lavfi -i "aevalsrc='$expr':s=48000:d=$d" -f lavfi -i "anoisesrc=color=pink:amplitude=0.05:d=$d:r=48000" \
  -filter_complex "[0][1]amix=inputs=2:weights=1 0.6,lowpass=f=1800,aecho=0.8:0.7:420|700:0.35|0.25,afade=t=in:d=0.4,afade=t=out:st=$st:d=1.2,volume=0.5" -ac 2 "$E/bed.wav"
ffmpeg -loglevel error -y -i "$E/narration.wav" -i "$E/bed.wav" \
  -filter_complex "[1]volume=${BED_DB:--9}dB[b];[0]aformat=channel_layouts=stereo[v];[v][b]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89" -ar 48000 "$P/remotion/public/$S.wav"
echo "$S $d"
