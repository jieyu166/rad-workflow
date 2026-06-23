#!/usr/bin/env bash
# pdf-to-tts-zh helper: rasterize, synthesize, concatenate.
# Step 2 (reading each page image and writing scripts/page-NN.txt) must be done
# by a model/human first — this script handles the mechanical steps around it.
#
# Usage:
#   ./build.sh rasterize INPUT.pdf      # step 1: PDF -> pages/page-NN.png
#   ./build.sh tts [VOICE]              # step 3: scripts/*.txt -> audio/*.mp3
#   ./build.sh combine OUTPUT.mp3       # step 4: audio/*.mp3 -> single mp3
set -euo pipefail

VOICE_DEFAULT="zh-TW-HsiaoChenNeural"

cmd="${1:-}"
case "$cmd" in
  rasterize)
    pdf="${2:?usage: build.sh rasterize INPUT.pdf}"
    mkdir -p pages scripts audio
    pdftoppm -png -r 150 "$pdf" pages/page
    shopt -s nullglob
    pngs=(pages/*.png)
    echo "rasterized ${#pngs[@]} page(s) -> pages/"
    ;;
  tts)
    voice="${2:-$VOICE_DEFAULT}"
    shopt -s nullglob
    files=(scripts/page-*.txt)
    [ ${#files[@]} -gt 0 ] || { echo "no scripts/page-*.txt found — do step 2 first" >&2; exit 1; }
    for f in "${files[@]}"; do
      n=$(basename "$f" .txt)
      edge-tts --voice "$voice" --file "$f" --write-media "audio/$n.mp3"
      echo "synthesized $n"
    done
    ;;
  combine)
    out="${2:?usage: build.sh combine OUTPUT.mp3}"
    : > audio/list.txt
    shopt -s nullglob
    for f in $(printf '%s\n' scripts/page-*.txt | sort); do
      n=$(basename "$f" .txt)
      echo "file '$PWD/audio/$n.mp3'" >> audio/list.txt
    done
    ffmpeg -y -f concat -safe 0 -i audio/list.txt -c:a libmp3lame -b:a 128k "$out"
    ffprobe -v error -show_entries format=duration \
      -of default=noprint_wrappers=1:nokey=1 "$out" \
      | awk '{printf "duration: %d:%02d -> '"$out"'\n", $1/60, $1%60}'
    ;;
  *)
    echo "usage: build.sh {rasterize INPUT.pdf | tts [VOICE] | combine OUTPUT.mp3}" >&2
    exit 1
    ;;
esac
