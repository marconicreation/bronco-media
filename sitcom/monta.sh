#!/bin/bash
# Uso: bash sitcom/monta.sh sitcom/episodi/epNN.json  -> crea sitcom/episodi/epNN.mp4 (sigla + puntata, pronto per Instagram/Facebook)
set -e
J="$1"; D=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d)
python3 "$D/sitcom.py" "$J" "$T/ep.mp4"
python3 "$D/sigla/sigla.py" --anteponi "$T/ep.mp4" "$T/full.mp4"
ffmpeg -y -loglevel error -i "$T/full.mp4" -c:v copy -c:a aac -b:a 128k -movflags +faststart "${J%.json}.mp4"
echo "${J%.json}.mp4"
