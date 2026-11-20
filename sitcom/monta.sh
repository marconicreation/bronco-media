#!/bin/bash
# Uso: bash sitcom/monta.sh sitcom/episodi/epNN.json  -> crea sitcom/episodi/epNN.mp4 (battuta + puntata + sigla, pronto per Instagram/Facebook)
set -e
J="$1"; D=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d)
python3 "$D/sitcom.py" "$J" "$T/ep.mp4"
# formato "battuta subito" (json con "aggancio"): sigla in coda; altrimenti sigla in testa
if grep -q '"aggancio"' "$J"; then M=--accoda; else M=--anteponi; fi
python3 "$D/sigla/sigla.py" $M "$T/ep.mp4" "$T/full.mp4"
ffmpeg -y -loglevel error -i "$T/full.mp4" -c:v copy -c:a aac -b:a 128k -movflags +faststart "${J%.json}.mp4"
# canzone esterna: una sola traccia continua dall'inizio alla fine (puntata + sigla), sfumata negli ultimi 1,5 s
IFS='|' read CANZ INIZIO <<< "$(python3 "$D/musica/canzone.py")"
if [ -n "$CANZ" ] && grep -q '"ritmo": true' "$J"; then
  L=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "${J%.json}.mp4")
  FADE=$(python3 -c "print($L-1.5)")
  if [ -f "$T/ep.mp4.voci.wav" ]; then  # voci dei personaggi sopra la canzone, che si abbassa quando parlano
    ffmpeg -y -loglevel error -i "${J%.json}.mp4" -ss "$INIZIO" -i "$CANZ" -i "$T/ep.mp4.voci.wav" -filter_complex \
      "[2:a]aresample=44100,apad,asplit=2[v1][v2];[1:a]aresample=44100,aformat=channel_layouts=stereo[m];[m][v1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md];[md][v2]amix=inputs=2:duration=first:normalize=0,afade=t=out:st=$FADE:d=1.5[a]" \
      -map 0:v -map "[a]" -t "$L" -c:v copy -c:a aac -b:a 160k -ac 2 -movflags +faststart "$T/m.mp4" && mv "$T/m.mp4" "${J%.json}.mp4"
  else
  ffmpeg -y -loglevel error -i "${J%.json}.mp4" -ss "$INIZIO" -i "$CANZ" -map 0:v -map 1:a -t "$L" -af "afade=t=out:st=$FADE:d=1.5" \
    -c:v copy -c:a aac -b:a 160k -ac 2 -movflags +faststart "$T/m.mp4" && mv "$T/m.mp4" "${J%.json}.mp4"
  fi
fi
echo "${J%.json}.mp4"
