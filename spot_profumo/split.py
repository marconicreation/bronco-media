# split.py file.mp3 prefisso n : trova le n battute (pause > 0,35 s) e le ritaglia con cut.sh
import subprocess,sys,re
f,pre,n=sys.argv[1],sys.argv[2],int(sys.argv[3])
dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
o=subprocess.run(['ffmpeg','-hide_banner','-i',f,'-af','silencedetect=n=-40dB:d=0.35','-f','null','-'],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',o)]; en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',o)]
sil=list(zip(st,en+[dur]*(len(st)-len(en))))
seg=[];p=0.0
for a,b in sil:
    if a-p>0.15: seg.append((p,a))
    p=b
if dur-p>0.15: seg.append((p,dur))
print(f,[(round(a,2),round(b,2)) for a,b in seg]); assert len(seg)==n,(len(seg),n)
for i,(a,b) in enumerate(seg,1): subprocess.run(['bash','cut.sh',f,str(max(0,a-0.05)),str(min(dur,b+0.08)),f'{pre}{i}.wav'])
