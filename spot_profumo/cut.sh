# cut.sh in.mp3 start end out.wav : ritaglia una battuta e la porta a picco -3 dB
p=$(ffmpeg -hide_banner -i $1 -af "atrim=$2:$3,volumedetect" -f null - 2>&1 | grep max_volume | sed 's/.*max_volume: \(.*\) dB/\1/')
g=$(python3 -c "print(min(14,-3-($p)))")
ffmpeg -loglevel error -y -i $1 -af "atrim=$2:$3,asetpts=PTS-STARTPTS,volume=${g}dB,afade=t=in:d=0.03,areverse,afade=t=in:d=0.08,areverse,aresample=44100" -ac 1 $4
echo -n "$4 gain $g "; ffmpeg -hide_banner -i $4 -af volumedetect -f null - 2>&1 | grep mean_volume | sed 's/.*] //'
