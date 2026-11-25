#!/bin/bash
# usage: tile.sh video name t1 t2 ...
v=$1; n=$2; shift 2; mkdir -p frames/$n; rm -f frames/$n/*.png; i=0
for t in "$@"; do i=$((i+1)); ffmpeg -loglevel error -y -ss $t -i $v -frames:v 1 frames/$n/$(printf %02d $i).png; done
ffmpeg -loglevel error -y -i frames/$n/%02d.png -vf "scale=360:-1,tile=7x2" frames/${n}_tile.png
