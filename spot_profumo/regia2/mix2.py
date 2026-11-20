#!/usr/bin/env python3
# mix2.py bronco|geremia|bartolomeo : audio della "regia 2" (musica su misura, suoni d'ambiente, voci Melania/Tommy invariate)
import subprocess, sys
WHO = sys.argv[1]
D = '/tmp/claude-0/spot/'
A = D + 'gen/a/'
P = {'bronco': 'R', 'geremia': 'G', 'bartolomeo': 'B'}[WHO]
T2 = {'bronco': 18900, 'geremia': 18900, 'bartolomeo': 19500}[WHO]
FL = 15.5
ins = []; fc = []; labels = []

def add(path):
    ins.extend(['-i', path]); return len(ins) // 2 - 1

def sfx(name, at, gain, dur=None, fin=0.3, fout=0.5, ss=0):
    i = add(A + name + '.mp3'); l = f's{len(labels)}'
    f = f'[{i}]aresample=44100,aformat=channel_layouts=stereo'
    if ss or dur: f += f',atrim=start={ss}' + (f':end={ss + dur}' if dur else '') + ',asetpts=PTS-STARTPTS'
    f += f',volume={gain}dB'
    if dur: f += f',afade=t=in:d={fin},afade=t=out:st={max(0, dur - fout)}:d={fout}'
    ms = int(at * 1000)
    f += f',adelay={ms}|{ms}[{l}]'
    fc.append(f); labels.append(l)

# --- voci (come nello spot approvato) ---
v = [add(D + f'el2/{P}_{n}.wav') for n in ('f1', 'f2', 'f3', 'f4', 'm1', 'm2')]
fc.append(f'[{v[0]}]adelay=4300|4300[a1];[{v[1]}]adelay=7300|7300[a2];[{v[2]}]volume=3dB,adelay=10300|10300[a3];[{v[3]}]volume=-5dB,adelay=13200|13200[a4];'
          f'[{v[4]}]volume=-1dB,adelay=17550|17550[a5];[{v[5]}]volume=-1dB,adelay={T2}|{T2}[a6];'
          '[a1][a2][a3][a4]amix=inputs=4:normalize=0,aecho=0.8:0.5:70:0.15[fv];[a5][a6]amix=inputs=2:normalize=0,aecho=0.8:0.5:70:0.12[mv];'
          '[fv][mv]amix=inputs=2:normalize=0,volume=3dB,aformat=channel_layouts=stereo,aresample=44100,apad=whole_dur=22,asplit[v][sc]')

# --- musica su misura, tagliata perche' il colpo cada sul lampo (15,5 s) ---
m = add(A + f'mus{P}.mp3')
if WHO == 'bartolomeo':   # colpo d'orchestra a 19,10 s del brano -> 15,5 s; inizio molto piano: lo alzo
    fc.append(f"[{m}]aresample=44100,atrim=start=3.6,asetpts=PTS-STARTPTS,volume='if(lt(t,3.2),12,if(lt(t,4.2),12*(4.2-t)/1.0,0))+1':eval=frame:precision=float,volume=1.0,"
              "afade=t=in:d=0.6,afade=t=out:st=21.3:d=0.7,apad=whole_dur=22[m0]")
elif WHO == 'bronco':     # accento finale a 25,75 s -> 15,5 s; poi ripresa della chiusura sul timbro Etsy
    r = add(A + f'mus{P}.mp3')
    fc.append(f"[{m}]aresample=44100,atrim=start=10.25,asetpts=PTS-STARTPTS,volume=-3dB,afade=t=in:d=0.6[ma];"
              f"[{r}]aresample=44100,atrim=start=27.2,asetpts=PTS-STARTPTS,volume=-3dB,afade=t=in:d=0.05,adelay=19750|19750[mb];"
              "[ma][mb]amix=inputs=2:normalize=0,afade=t=out:st=21.4:d=0.6,apad=whole_dur=22[m0]")
else:                     # geremia: la calma si spezza di colpo sul lampo, poi silenzio (la gag e' il silenzio)
    fc.append(f"[{m}]aresample=44100,atrim=start=2.0:end={2.0 + FL - 0.05},asetpts=PTS-STARTPTS,volume=1dB,afade=t=in:d=0.8,afade=t=out:st={FL - 0.13}:d=0.08,apad=whole_dur=22[m0]")
fc.append('[m0]aformat=channel_layouts=stereo,volume=0.40[m]')

# --- suoni d'ambiente ---
if WHO == 'bartolomeo':
    sfx('vento', 0.0, 9, dur=3.6, fin=0.8, fout=1.0)
    sfx('penna', 3.2, 3, dur=3.6, fin=0.4, fout=1.2)
    sfx('vento', 5.6, 9, dur=3.5, fin=1.0, fout=0.15, ss=3.0)
    sfx('citta', 9.0, 4, dur=3.4, fin=0.05, fout=0.5)
    sfx('telo', 13.5, 9)
    sfx('vento', FL, 6, dur=6.5, fin=0.6, fout=1.0, ss=1.0)
elif WHO == 'bronco':
    sfx('mare', 0.0, 1, dur=11.5, fin=1.0, fout=1.5)
    sfx('mare', 10.0, 1, dur=11.9, fin=1.5, fout=1.0)
else:
    sfx('lago', 0.0, 16, dur=11.5, fin=1.0, fout=1.5)
    sfx('lago', 10.0, 16, dur=FL - 10.0, fin=1.5, fout=0.08)
    sfx('goccia', 1.45, 0)
    sfx('campana', 9.25, -16)
    sfx('lago', 16.2, 19, dur=5.8, fin=1.0, fout=0.8, ss=2.0)
sfx('vapore', 17.2, 18)
fc.append(''.join(f'[{l}]' for l in labels) + f'amix=inputs={len(labels)}:normalize=0,apad=whole_dur=22[fx]')
fc.append('[m][fx]amix=inputs=2:normalize=0[bed];[bed][sc]sidechaincompress=threshold=0.005:ratio=8:attack=25:release=450[md]')
n0 = len(labels); sfx('lampo', FL - 0.35, -9); sfx('timbro', 19.8, -10 if WHO == 'bartolomeo' else -7)
# --- suoni comici sullo stacco del personaggio (Robi 20/11): picco portato al livello voluto ---
import re, os
def comico(name, at, peak, dur=None, fout=0.4):
    if not os.path.exists(A + name + '.mp3'): return
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', A + name + '.mp3', '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    mx = float(re.search(r'max_volume: (\S+)', r).group(1))
    sfx(name, at, round(peak - mx, 1), dur=dur, fin=0.01, fout=fout)
L2 = T2 / 1000
comico('disco', FL - 0.1, -6)                                     # il disco che si ferma, sullo stacco
comico({'bronco': 'boing', 'geremia': 'trombone', 'bartolomeo': 'boing'}[WHO], 16.6, -8, dur=0.95, fout=0.25)  # il personaggio spunta
comico('fischietto', 17.0, -14, dur=0.55, fout=0.15)   # la tazza sale (corto: poi parla Tommy)
comico('piatti', 19.8, -11 if WHO == 'bartolomeo' else -8)        # colpo di piatti sul timbro Etsy
if WHO == 'bartolomeo': comico('risata', L2 + 0.9, -2.5, dur=22 - (L2 + 0.9), fout=0.5)  # Robi: in Bartolomeo si sentiva poco
else: comico('risata', max(20.3, L2 + 1.1), -9, dur=22 - max(20.3, L2 + 1.1), fout=0.6)  # Bronco e Geremia: approvata cosi'
fc.append(''.join(f'[{l}]' for l in labels[n0:]) + f'amix=inputs={len(labels) - n0}:normalize=0,apad=whole_dur=22[hit]')
if False: fc.append(f'[{labels[n0]}][{labels[n0+1]}]amix=inputs=2:normalize=0,apad=whole_dur=22[hit]')
fc.append('[md][v][hit]amix=inputs=3:normalize=0,alimiter=limit=0.9[out]')
out = D + f'gen/mix2_{WHO}.wav'
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y'] + ins + ['-filter_complex', ';'.join(fc), '-map', '[out]', '-t', '22', '-ac', '2', '-ar', '44100', out], check=True)
outn = D + f'gen/mix2n_{WHO}.wav'
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', out, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '44100', outn], check=True)
final = f'/mnt/project-files/spot_profumo/19_spot_{WHO}_regia_nuova.mp4'
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', D + f'muto2_{WHO}.mp4', '-i', outn, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', final], check=True)
for st, du in ((0.5, 3), (4.3, 1), (7.3, 0.9), (10.3, 1), (13.2, 2), (15.2, 0.8), (16.0, 1.4), (17.55, 1.3), (T2 / 1000, 1.2), (19.8, 0.6), (20.8, 1.2)):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-ss', str(st), '-t', str(du), '-i', outn, '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    mv = [x.split('] ')[1] for x in r.splitlines() if 'mean_volume' in x or 'max_volume' in x]
    print(st, ' | '.join(mv))
print(final)
