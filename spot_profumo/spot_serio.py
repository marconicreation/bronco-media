import subprocess, numpy as np, math, sys
# Spot "serio" parametrico: python3 spot_serio.py bronco|geremia|bartolomeo  (regole: REGOLE_SPOT_SERI.md)
CFG={
 'bronco':dict(seg='segR',char='L_bronco.png',cx=500,cdy=70,mug='L_tazza_hi.png',mx=445,ycut=568,zc=(710,400),name='BRONCO',line='Sa di caffè.',top='VAI COL TANGO!',
   words=['INTENSO','AUDACE','INDIMENTICABILE','IL NUOVO PROFUMO DI'],bright=0.93),
 'geremia':dict(seg='segG',char='L_geremia.png',cx=490,cdy=95,mug='L_tazza_geremia.png',mx=350,ycut=560,zc=(680,400),name='GEREMIA',line='Non parlarmi|prima del caffè.',top='',
   words=['CALMA','SILENZIO','ARMONIA','LA NUOVA SERENITÀ DI'],bright=0.97),
 'bartolomeo':dict(seg='segB',char='L_bartolomeo.png',cx=575,cdy=110,mug='L_tazza_bartolomeo.png',mx=300,ycut=548,zc=(670,390),name='BARTOLOMEO',tl=19.5,line='Sciabadù.',top='',
   words=['VISIONE','GENIO','FUTURO','LA NUOVA INVENZIONE DI'],bright=0.97),
}
WHO=sys.argv[1]; C=CFG[WHO]
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
D='/tmp/claude-0/spot/'; FPS=30; W,H=1080,1920; BW,BH=1080,608; BANDY=(H-BH)//2
def frames(path,ch):
    p=subprocess.run(['ffmpeg','-v','error','-i',path,'-f','rawvideo','-pix_fmt','gray' if ch==1 else 'rgb24','-'],capture_output=True).stdout
    return np.frombuffer(p,np.uint8).reshape((-1,BH,BW) if ch==1 else (-1,BH,BW,3))
SH=[frames(D+f"{C['seg']}/s{i}.mp4",1) for i in range(1,6)]
S=1.5; HW,HH=int(BW*S),int(BH*S)
class Seq:
    def __init__(s,path):
        s.p=subprocess.Popen(['ffmpeg','-v','error','-i',path,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE); s.i=-1; s.cur=None
    def get(s,i):
        while s.i<i:
            b=s.p.stdout.read(HW*HH*3)
            if len(b)<HW*HH*3: break
            s.cur=np.frombuffer(b,np.uint8).reshape(HH,HW,3); s.i+=1
        return s.cur
B6=Seq(D+C['seg']+'/bg_hi.mp4')
serif=lambda s: ImageFont.truetype(D+'fonts/CormorantGaramond.ttf',s)
cin=lambda s: ImageFont.truetype(D+'fonts/Cinzel.ttf',s)
pd=lambda s: ImageFont.truetype('/mnt/project-files/fonts/Pricedown_Bl.otf',s)
def v(f,w):
    f.set_variation_by_axes([w]); return f
# shots: (start, length)
STEP,LEN=3.0,4.2
starts=[i*STEP for i in range(5)]+[15.0]
TOT=22.0
bron=Image.open(D+C['char']); bh=540; bron=bron.resize((int(bron.width*bh*S/bron.height),int(bh*S)),Image.LANCZOS)
mug=Image.open(D+C['mug']).resize((int(270*S),int(270*S)),Image.LANCZOS); MUGH=270
def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def shot_alpha(t,s,L,last=False):
    if t<s or (not last and t>s+L): return 0
    a=ease((t-s)/1.2)
    if not last: a=min(a,ease((s+L-t)/1.2))
    return a
def steam(t):
    L=Image.new('RGBA',(BW,BH)); d=ImageDraw.Draw(L)
    a=int(150*ease((t-17.4)/0.6))
    for k in range(3):
        x0=C['mx']+92+k*22; pts=[(x0+9*math.sin(j*0.5+t*3+k*2)+j*5.0, 332-j*5) for j in range(16)]
        d.line(pts,fill=(255,255,255,a),width=10,joint='curve')
    return L.filter(ImageFilter.GaussianBlur(5))
import numpy as _np
from PIL import ImageEnhance as _IE
bron2=_IE.Brightness(bron).enhance(C['bright'])
def fgmask(arr):
    # cespugli in primo piano (in basso): non blu mare
    r,g,b=[arr[...,i].astype(int) for i in range(3)]
    m=((g>=b-5)|(r>b+10)).astype(_np.uint8)*255
    m[:int(C['ycut']*S),:]=0
    mi=Image.fromarray(m).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(2.2))
    return mi
def bronco_scene(t):
    arr=B6.get(int((t-starts[5])*FPS)); raw=Image.fromarray(arr)
    bg=raw.filter(ImageFilter.GaussianBlur(1.8)).convert('RGBA')
    f=bg.copy()
    rise=ease((t-16.6)/0.8); off=int((1-rise)*420)
    bob=-int(5*abs(math.sin((t-17.6)*7))) if 17.6<t<18.8 else 0
    if rise>0:
        f.alpha_composite(bron2,(int(C['cx']*S),int((BH-bh+C['cdy']+off+bob)*S)))
        f.alpha_composite(mug,(int(C['mx']*S),int((C['ycut']+20-MUGH+int((1-ease((t-17.0)/0.6))*360))*S)))
        f.alpha_composite(steam(t).resize((HW,HH),Image.BICUBIC))
        # cespugli davanti a Bronco e alla tazza
        fg=raw.convert('RGBA'); fg.putalpha(fgmask(arr)); f.alpha_composite(fg)
    sat=ease((t-16.0)/1.4)
    g=f.convert('L').convert('RGB'); c=f.convert('RGB')
    o=Image.blend(g,c,sat)
    z=1+0.32*ease((t-17.2)/4.6)   # carrellata lenta in avanti
    w,h=HW/z,HH/z; cx,cy=C['zc'][0]*S,C['zc'][1]*S
    x0=min(max(cx-w/2,0),HW-w); y0=min(max(cy-h/2,0),HH-h)
    return o.resize((BW,BH),Image.LANCZOS,box=(x0,y0,x0+w,y0+h))
def spaced(d,txt,y,font,fill,a,sp):
    if a<=0: return
    ws=[d.textlength(c,font=font) for c in txt]; tw=sum(ws)+sp*(len(txt)-1); x=(W-tw)/2
    for c,w in zip(txt,ws): d.text((x,y),c,font=font,fill=fill+(int(255*a),)); x+=w+sp
def gta(fr,txt,y,font,fill,a,sp):
    if a<=0: return
    L=Image.new('RGBA',fr.size,(0,0,0,0)); d=ImageDraw.Draw(L); sz=font.size
    ws=[d.textlength(c,font=font) for c in txt]; tw=sum(ws)+sp*(len(txt)-1)
    so=max(5,sz//17)
    for sw,col in ((so,(0,0,0,255)),(0,fill+(255,))):
        x=(W-tw)/2
        for c,w in zip(txt,ws):
            d.text((x,y),c,font=font,fill=col,stroke_width=sw,stroke_fill=col); x+=w+sp
    if a<1: L.putalpha(L.split()[3].point(lambda p:int(p*a)))
    fr.alpha_composite(L)
def stamp(txt,font,fill,sp):
    d0=ImageDraw.Draw(Image.new('RGBA',(8,8))); ws=[d0.textlength(c,font=font) for c in txt]; tw=int(sum(ws)+sp*(len(txt)-1)); so=max(5,font.size//17)
    L=Image.new('RGBA',(tw+6*so,int(font.size*1.5)+6*so),(0,0,0,0)); d=ImageDraw.Draw(L)
    for sw,col in ((so,(0,0,0,255)),(0,fill+(255,))):
        x=3*so
        for c,w in zip(txt,ws): d.text((x,3*so),c,font=font,fill=col,stroke_width=sw,stroke_fill=col); x+=w+sp
    return L.crop(L.getbbox())
ETSY=stamp('LA TROVI SU ETSY!',pd(150),(241,100,30),12)
def pulse(fr,t,cx,cy):
    a=ease((t-19.8)/0.35)
    if a<=0: return
    k=(0.55+0.45*a)*(1+0.07*math.sin((t-19.8)*2*math.pi*1.8))*0.62
    L=ETSY.resize((int(ETSY.width*k),int(ETSY.height*k)),Image.LANCZOS).rotate(8,expand=True,resample=Image.BICUBIC)
    if a<1: L.putalpha(L.split()[3].point(lambda p:int(p*a)))
    fr.alpha_composite(L,(int(cx-L.width/2),int(cy-L.height/2)))
def fit(txt,size,sp,maxw=980):
    while size>40:
        f=pd(size); d0=ImageDraw.Draw(Image.new('RGB',(8,8)))
        if sum(d0.textlength(c,font=f) for c in txt)+sp*(len(txt)-1)<=maxw: break
        size-=4
    return size
w=C['words']
WORDS=[  # text, start, end, y, font, size, weight, sp
 (w[0],4.0,6.9,0,'s',66,400,18),(w[1],7.0,9.9,0,'s',66,400,18),(w[2],10.0,12.9,0,'s',58 if len(w[2])>10 else 66,400,10 if len(w[2])>10 else 18),
 (w[3],13.0,15.6,0,'c',46 if len(w[3])<21 else 42,400,8),
 (C['name'],17.55,TOT+1,-10,'P',fit(C['name'],180,22),0,22),
]
for i,l in enumerate(C['line'].split('|')): WORDS.append((l,C.get('tl',18.9)+0.45*i,TOT+1,(205 if '|' not in C['line'] else 180)+80*i,'p',fit(l,92 if '|' not in C['line'] else 74,9),0,9))
TWO=45 if '|' in C['line'] else 0
GOLD=(232,214,170); WHITE=(240,236,228)
out=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','18',D+f'muto_{WHO}.mp4'],stdin=subprocess.PIPE)
for n in range(int(TOT*FPS)):
    t=n/FPS
    band=np.zeros((BH,BW,3),float)
    for k in range(5):
        a=shot_alpha(t,starts[k],LEN)
        if a>0:
            j=min(int((t-starts[k])*FPS),len(SH[k])-1); band+=a*np.repeat(SH[k][j][...,None],3,2)
    a6=shot_alpha(t,starts[5],TOT,last=True)
    if a6>0: band+=a6*np.array(bronco_scene(t)).astype(float)
    # fade from black at start, to black at very end? keep end.
    kb=ease((t-16.0)/1.4); fr=Image.new('RGBA',(W,H),(int(244*kb),int(233*kb),int(208*kb),255))
    fr.paste(Image.fromarray(np.clip(band,0,255).astype('uint8')),(0,BANDY))
    d=ImageDraw.Draw(fr)
    for txt,s,e,dy,ft,sz,wg,sp in WORDS:
        a=ease((t-s)/(0.3 if ft in 'pP' else 0.8))*ease((e-t)/0.6)
        font=pd(sz) if ft in 'pP' else v(serif(sz) if ft=='s' else cin(sz),wg)
        col=GOLD if ft in 'cP' else WHITE
        if ft in 'pP': gta(fr,txt,BANDY+BH+70+dy,font,(255,255,255) if ft=='p' else (255,214,90),a,sp); d=ImageDraw.Draw(fr)
        else: spaced(d,txt,BANDY+BH+70+dy,font,col,a,sp)
    # Etsy line under, elegant
    if t>19.8:
        a=ease((t-19.8)/0.8)
        if C['top']: gta(fr,C['top'],BANDY-240,pd(96),(255,255,255),a,8); d=ImageDraw.Draw(fr)
        pulse(fr,t,W//2,BANDY+BH+500+TWO); d=ImageDraw.Draw(fr)
        spaced(d,'link in bio',BANDY+BH+600+TWO,v(serif(46),600),(95,75,60),a,3)
    out.stdin.write(fr.convert('RGB').tobytes())
out.stdin.close(); out.wait(); print('ok')
