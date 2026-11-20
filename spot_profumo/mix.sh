# mix.sh G|B tempo_seconda_battuta_ms nome_uscita
P=$1; T2=$2
cd /tmp/claude-0/spot/el
ffmpeg -loglevel error -y -i ../audio2.wav -i ${P}_f1.wav -i ${P}_f2.wav -i ${P}_f3.wav -i ${P}_f4.wav -i ${P}_m1.wav -i ${P}_m2.wav -filter_complex "[1]adelay=4300|4300[a1];[2]adelay=7300|7300[a2];[3]adelay=10300|10300[a3];[4]volume=-5dB,adelay=13200|13200[a4];[5]volume=-1dB,adelay=17550|17550[a5];[6]volume=-1dB,adelay=$T2|$T2[a6];[a1][a2][a3][a4]amix=inputs=4:normalize=0,aecho=0.8:0.5:70:0.15[fv];[a5][a6]amix=inputs=2:normalize=0,aecho=0.8:0.5:70:0.12[mv];[fv][mv]amix=inputs=2:normalize=0,apad=whole_dur=22,asplit[v][sc];[0]volume=0.45[m];[m][sc]sidechaincompress=threshold=0.02:ratio=6:attack=40:release=500[md];[md][v]amix=inputs=2:normalize=0,alimiter=limit=0.9[out]" -map "[out]" -t 22 -ac 2 -ar 44100 mix_$P.wav
ffmpeg -loglevel error -y -i mix_$P.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 44100 mixn_$P.wav
ffmpeg -loglevel error -y -i ../muto_$3.mp4 -i mixn_$P.wav -c:v copy -c:a aac -b:a 192k -shortest /mnt/project-files/spot_profumo/17_spot_serio_$3.mp4
for w in "4.3 1" "7.3 0.9" "10.3 1" "13.2 2" "17.55 1.5" "$(python3 -c "print($T2/1000)") 1.2" "1 2"; do set -- $w; echo -n "$1: "; ffmpeg -hide_banner -ss $1 -t $2 -i mixn_$P.wav -af volumedetect -f null - 2>&1 | grep mean_volume | sed 's/.*] //'; done
