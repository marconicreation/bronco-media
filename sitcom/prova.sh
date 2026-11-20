#!/bin/bash
# "Reel di prova" (Robi 20/11, campagna Natale al bancone): versione corta della puntata per chi non ci segue.
# Uso: bash sitcom/prova.sh sitcom/episodi/epNN.json -> sitcom/episodi/epNN_prova.mp4 (~25 s, senza sigla)
# Apertura: la battuta intera di Geremia (l'aggancio della puntata è la sua versione corta),
# poi solo il cuore della scenetta (invenzione, battuta finale, Sciabadù, reazione, Bronco). Niente trio, niente saga.
set -e
J="$1"; D=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d); OUT="${J%.json}_prova.mp4"
python3 - "$J" "$D/episodi/.prova_tmp.json" <<'PY'
import json, sys
ep = json.load(open(sys.argv[1]))
ag = (ep.get('aggancio') or {}).get('testo', '')
sc = [s for s in ep['scene'] if 'trio' not in s.get('img', '')]
dial = [s for s in sc if s.get('chi') and s.get('testo') not in ('', 'Sciabadù!', '...')]
# chi guarda i Reel di prova di solito non ha visto la puntata delle 13: si apre sempre con l'esplosione di Geremia
cand = [s for s in dial if s['chi'] == 'GEREMIA'] or [s for s in dial if s['chi'] == 'BARTOLOMEO'][-1:]
apri = dict(cand[0]); apri['battute'] = 2
resto = [s for s in sc if s is not cand[0]]
p = {k: v for k, v in ep.items() if k not in ('saga', 'scene', 'aggancio', 'avvento')}
p.update(aggancio=apri, scene=resto, ritmo=True)
json.dump(p, open(sys.argv[2], 'w'), ensure_ascii=False)
PY
python3 "$D/sitcom.py" "$D/episodi/.prova_tmp.json" "$T/v.mp4"; rm -f "$D/episodi/.prova_tmp.json"
IFS='|' read CANZ INIZIO <<< "$(python3 "$D/musica/canzone.py")"
L=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$T/v.mp4")
if [ -n "$CANZ" ]; then
  FADE=$(python3 -c "print($L-1.5)")
  if [ -f "$T/v.mp4.voci.wav" ]; then
    ffmpeg -y -loglevel error -i "$T/v.mp4" -ss "$INIZIO" -i "$CANZ" -i "$T/v.mp4.voci.wav" -filter_complex \
      "[2:a]aresample=44100,apad,asplit=2[v1][v2];[1:a]aresample=44100,aformat=channel_layouts=stereo[m];[m][v1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md];[md][v2]amix=inputs=2:duration=first:normalize=0,afade=t=out:st=$FADE:d=1.5[a]" \
      -map 0:v -map "[a]" -t "$L" -c:v copy -c:a aac -b:a 160k -ac 2 -movflags +faststart "$OUT"
  else
  ffmpeg -y -loglevel error -i "$T/v.mp4" -ss "$INIZIO" -i "$CANZ" -map 0:v -map 1:a -t "$L" \
    -af "afade=t=out:st=$FADE:d=1.5" -c:v copy -c:a aac -b:a 160k -ac 2 -movflags +faststart "$OUT"
  fi
else
  ffmpeg -y -loglevel error -i "$T/v.mp4" -c:v copy -c:a aac -movflags +faststart "$OUT"
fi
echo "$OUT"
