import subprocess, numpy as np, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
D='/tmp/claude-0/spot/'; FPS=30; W,H=1080,1920; BW,BH=1080,608; BANDY=(H-BH)//2
def frames(path,ch):
    p=subprocess.run(['ffmpeg','-v','error','-i',path,'-f','rawvideo','-pix_fmt','gray' if ch==1 else 'rgb24','-'],capture_output=True).stdout
    return np.frombuffer(p,np.uint8).reshape((-1,BH,BW) if ch==1 else (-1,BH,BW,3))
SH=[frames(D+f'seg2/s{i}.mp4',1) for i in range(1,6)]
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
B6=Seq(D+'seg2/s6b_hi.mp4')
serif=lambda s: ImageFont.truetype(D+'fonts/CormorantGaramond.ttf',s)
cin=lambda s: ImageFont.truetype(D+'fonts/Cinzel.ttf',s)
pd=lambda s: ImageFont.truetype('/mnt/project-files/fonts/Pricedown_Bl.otf',s)
def v(f,w):
    f.set_variation_by_axes([w]); return f
# shots: (start, length)
STEP,LEN=3.0,4.2
starts=[i*STEP for i in range(5)]+[15.0]
TOT=22.0
bron=Image.open(D+'L_bronco.png'); bh=540; bron=bron.resize((int(bron.width*bh*S/bron.height),int(bh*S)),Image.LANCZOS)
mug=Image.open(D+'L_tazza_hi.png').resize((int(270*S),int(270*S)),Image.LANCZOS); MUGH=270
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
        x0=537+k*22; pts=[(x0+9*math.sin(j*0.5+t*3+k*2)+j*5.0, 332-j*5) for j in range(16)]
        d.line(pts,fill=(255,255,255,a),width=10,joint='curve')
    return L.filter(ImageFilter.GaussianBlur(5))
import numpy as _np
from PIL import ImageEnhance as _IE
bron2=_IE.Brightness(bron).enhance(0.93)
def fgmask(arr):
    # cespugli in primo piano (in basso): non blu mare
    r,g,b=[arr[...,i].astype(int) for i in range(3)]
    m=((g>=b-5)|(r>b+10)).astype(_np.uint8)*255
    m[:int(568*S),:]=0
    mi=Image.fromarray(m).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(2.2))
    return mi
def bronco_scene(t):
    arr=B6.get(int((t-starts[5])*FPS)); raw=Image.fromarray(arr)
    bg=raw.filter(ImageFilter.GaussianBlur(1.8)).convert('RGBA')
    f=bg.copy()
    rise=ease((t-16.6)/0.8); off=int((1-rise)*420)
    bob=-int(5*abs(math.sin((t-17.6)*7))) if 17.6<t<18.8 else 0
    if rise>0:
        f.alpha_composite(bron2,(int(500*S),int((BH-bh+70+off+bob)*S)))
        f.alpha_composite(mug,(int(445*S),int((BH-MUGH-20+int((1-ease((t-17.0)/0.6))*360))*S)))
        f.alpha_composite(steam(t).resize((HW,HH),Image.BICUBIC))
        # cespugli davanti a Bronco e alla tazza
        fg=raw.convert('RGBA'); fg.putalpha(fgmask(arr)); f.alpha_composite(fg)
    sat=ease((t-16.0)/1.4)
    g=f.convert('L').convert('RGB'); c=f.convert('RGB')
    o=Image.blend(g,c,sat)
    z=1+0.32*ease((t-17.2)/4.6)   # carrellata lenta in avanti
    w,h=HW/z,HH/z; cx,cy=710*S,400*S
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
WORDS=[  # text, start, end, y, font, size, weight, sp, colour
 ('INTENSO',4.0,6.9,0,'s',66,400,18),
 ('AUDACE',7.0,9.9,0,'s',66,400,18),
 ('INDIMENTICABILE',10.0,12.9,0,'s',58,400,10),
 ('IL NUOVO PROFUMO DI',13.0,15.6,0,'c',46,400,8),
 ('BRONCO',17.55,TOT+1,-10,'P',180,0,22),
 ('Sa di caffè.',18.9,TOT+1,205,'p',92,0,9),
]
GOLD=(232,214,170); WHITE=(240,236,228)
out=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','18',D+'video4_muto.mp4'],stdin=subprocess.PIPE)
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
        gta(fr,'VAI COL TANGO!',BANDY-240,pd(96),(255,255,255),a,8); d=ImageDraw.Draw(fr)
        pulse(fr,t,W//2,BANDY+BH+500); d=ImageDraw.Draw(fr)
        spaced(d,'link in bio',BANDY+BH+600,v(serif(46),600),(95,75,60),a,3)
    out.stdin.write(fr.convert('RGB').tobytes())
out.stdin.close(); out.wait(); print('ok')
