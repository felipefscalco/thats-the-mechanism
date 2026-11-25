#!/bin/bash
# Synthesized ambient bed (original, no license needed) + narration mix
set -e
cd "$(dirname "$0")/.."
i=0
for ep in 01-qr-code 02-elevator 03-sky; do
  i=$((i+1))
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 episodes/$ep/narration.wav)
  st=$(python3 -c "print($d-1.2)")
  case $i in 1) f="110 164.81 246.94 277.18 415.3";; 2) f="98 146.83 220 246.94 369.99";; 3) f="87.31 130.81 196 220 329.63";; esac
  set -- $f
  expr="0.30*sin(2*PI*$1*t)+0.22*sin(2*PI*$2*t)*(0.6+0.4*sin(2*PI*0.07*t))+0.16*sin(2*PI*$3*t)*(0.5+0.5*sin(2*PI*0.11*t+1))+0.12*sin(2*PI*$4*t)*(0.5+0.5*sin(2*PI*0.05*t+2))+0.08*sin(2*PI*$5*t)*(0.5+0.5*sin(2*PI*0.13*t))"
  ffmpeg -loglevel error -y -f lavfi -i "aevalsrc='$expr':s=48000:d=$d" -f lavfi -i "anoisesrc=color=pink:amplitude=0.05:d=$d:r=48000" \
    -filter_complex "[0][1]amix=inputs=2:weights=1 0.6,lowpass=f=1800,aecho=0.8:0.7:420|700:0.35|0.25,afade=t=in:d=0.4,afade=t=out:st=$st:d=1.2,volume=0.5" -ac 2 episodes/$ep/bed.wav
  ffmpeg -loglevel error -y -i episodes/$ep/narration.wav -i episodes/$ep/bed.wav \
    -filter_complex "[1]volume=${BED_DB:--26}dB[b];[0]aformat=channel_layouts=stereo[v];[v][b]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89" -ar 48000 remotion/public/$ep.wav
  echo "$ep $d"
done
