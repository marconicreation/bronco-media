#!/usr/bin/env bash
# Reel "IL MEGLIO DELLA SETTIMANA" (domenica 18:00 su Facebook): le aperture più forti delle puntate della settimana
# + la chiusura del regalo presa da un Reel FB recente. Gratis, solo ffmpeg.
# Uso: bash tools/meglio.sh OUT.mp4 CHIUSURA.mp4 EP1.mp4 EP2.mp4 EP3.mp4 [EP4.mp4]
#  - EPn: puntate della settimana (sitcom/episodi/epNN.mp4), di solito le 3-4 con più visualizzazioni (Metricool).
#  - CHIUSURA: un Reel FB "_2" recente (promo/fb/AAAA-MM-GG_2.mp4): se ne usano gli ultimi 3,5 s (card regalo / segui).
# Da ogni puntata prende i primi 3,4 s (l'"aggancio", la battuta più forte), con la scritta "IL MEGLIO DELLA SETTIMANA" in alto.
set -euo pipefail
OUT=$1; END=$2; shift 2
R="$(cd "$(dirname "$0")/.." && pwd)"; FONT="$R/Bangers-Regular.ttf"
T=$(mktemp -d); i=0; LIST="$T/list.txt"
for EP in "$@"; do
  i=$((i+1))
  ffmpeg -v error -y -ss 0 -t 3.4 -i "$EP" -vf "drawbox=y=0:w=iw:h=170:color=black@0.55:t=fill,drawtext=fontfile=$FONT:text='IL MEGLIO DELLA SETTIMANA  $i/$#':fontsize=72:fontcolor=0xFFD65A:borderw=6:bordercolor=black:x=(w-text_w)/2:y=50" \
    -c:v libx264 -preset veryfast -crf 20 -r 30 -pix_fmt yuv420p -c:a aac -ar 44100 -ac 2 "$T/p$i.mp4"
  echo "file '$T/p$i.mp4'" >> "$LIST"
done
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$END")
S=$(python3 -c "print(max(0,$D-3.5))")
ffmpeg -v error -y -ss "$S" -i "$END" -c:v libx264 -preset veryfast -crf 20 -r 30 -pix_fmt yuv420p -c:a aac -ar 44100 -ac 2 "$T/end.mp4"
echo "file '$T/end.mp4'" >> "$LIST"
ffmpeg -v error -y -f concat -safe 0 -i "$LIST" -c:v libx264 -preset veryfast -crf 21 -pix_fmt yuv420p -c:a aac -ar 44100 -ac 2 -movflags +faststart "$OUT"
rm -rf "$T"; echo "ok $OUT"
