import subprocess, numpy as np, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D='/tmp/claude-0/spot/'; FPS=30; W,H=1080,1920
def frames(path,w,h,gray=False):
    p=subprocess.run(['ffmpeg','-v','error','-i',path,'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    a=np.frombuffer(p,np.uint8).reshape(-1,h,w,3); return a
S=[frames(D+f'seg/s{i}.mp4',1080,608) for i in (1,2,3)]
BG=frames(D+'seg/bg.mp4',1080,1920)
serif=lambda s: ImageFont.truetype(D+'fonts/CormorantGaramond.ttf',s)
cin=lambda s: ImageFont.truetype(D+'fonts/Cinzel.ttf',s)
bang=lambda s: ImageFont.truetype('/home/user/bronco-media/Bangers-Regular.ttf',s)
def fnt(f,wght): 
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f
bron=Image.open(D+'L_bronco.png'); mug=Image.open(D+'L_tazza.png').resize((620,620),Image.LANCZOS); cnt=Image.open(D+'L_bancone.png')
BANDY=(H-608)//2
T1,T2,T3=2.2,4.4,6.6   # band shots
TT=7.6                 # "Il nuovo profumo." card ends -> reveal
TOT=12.0
def spaced(d,txt,y,font,fill,alpha=255,sp=14):
    # letter spaced centered
    ws=[d.textlength(c,font=font) for c in txt]; tw=sum(ws)+sp*(len(txt)-1); x=(W-tw)/2
    for c,w in zip(txt,ws):
        d.text((x,y),c,font=font,fill=fill+(alpha,)); x+=w+sp
def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def steam(t):
    L=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(L)
    for k in range(3):
        x0=290+k*55; pts=[]
        for j in range(30):
            yy=1290-j*9
            xx=x0+28*math.sin(j*0.35+t*4+k*2)+j*4.5
            pts.append((xx,yy))
        a=int(170*ease((t-TT)/0.6))
        d.line(pts,fill=(255,255,255,a),width=20,joint='curve')
    return L.filter(ImageFilter.GaussianBlur(7))
def bubble(img,txt,alpha=1.0,scale=1.0):
    L=Image.new('RGBA',(W,H)); d=ImageDraw.Draw(L)
    f=bang(int(118*scale)); tw=d.textlength(txt,font=f)
    cx,cy=470,640; bw,bh=tw/2+70,110*scale
    d.polygon([(cx+40,cy+bh-20),(cx+170,cy+bh-20),(cx+250,cy+bh+170)],fill='white',outline='black')
    d.ellipse((cx-bw,cy-bh,cx+bw,cy+bh),fill='white',outline='black',width=8)
    d.polygon([(cx+50,cy+bh-30),(cx+160,cy+bh-30),(cx+240,cy+bh+150)],fill='white')
    d.line([(cx+40,cy+bh-14),(cx+250,cy+bh+170),(cx+170,cy+bh-14)],fill='black',width=8)
    d.text((cx-tw/2,cy-int(64*scale)),txt,font=f,fill=(205,40,30),stroke_width=3,stroke_fill='black')
    if alpha<1: L.putalpha(L.split()[3].point(lambda v:int(v*alpha)))
    img.alpha_composite(L)
def scene(t,i):
    f=Image.fromarray(BG[min(i,len(BG)-1)]).convert('RGBA')
    # sniff bob
    bob=0
    if TT+0.3<t<TT+1.5: bob=-int(10*abs(math.sin((t-TT)*9)))
    bx=(W-bron.width)//2+60; by=H-300-bron.height+120+bob
    f.alpha_composite(bron,(bx,by))
    f.alpha_composite(steam(t))
    f.alpha_composite(cnt,(0,1620)); f.alpha_composite(mug,(60,1700-mug.height+50))
    return f
out=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','medium',D+'video_muto.mp4'],stdin=subprocess.PIPE)
N=int(TOT*FPS)
for n in range(N):
    t=n/FPS
    if t<T3:
        k=0 if t<T1 else 1 if t<T2 else 2; st=[0,T1,T2][k]
        fr=Image.new('RGBA',(W,H),(0,0,0,255))
        j=min(int((t-st)*FPS),len(S[k])-1); band=Image.fromarray(S[k][j]).convert('RGBA')
        # fade in/out per shot
        a=min(1,(t-st)/0.35, ((st+2.2)-t)/0.25 if k<2 else 1)
        band.putalpha(int(255*max(0,a)))
        fr.alpha_composite(band,(0,BANDY))
        d=ImageDraw.Draw(fr)
        word=['INTENSO','AUDACE','INDIMENTICABILE'][k]
        ta=int(255*ease((t-st-0.4)/0.5)*max(0,min(1,((st+2.2)-t)/0.25)) )
        spaced(d,word,BANDY+608+70,fnt(serif(64 if k<2 else 56),400),(240,236,228),ta,sp=18 if k<2 else 10)
    elif t<TT:
        fr=Image.new('RGBA',(W,H),(0,0,0,255)); d=ImageDraw.Draw(fr)
        a=int(255*ease((t-T3)/0.35))
        spaced(d,'IL NUOVO PROFUMO',880,fnt(cin(54),400),(225,200,150),a,sp=10)
        spaced(d,'di',960,fnt(serif(60),400),(225,200,150),a,sp=4)
    else:
        i=int((t-TT)*FPS)
        fr=scene(t,i)
        # reveal: black curtains opening from band
        o=ease((t-TT)/0.3)
        if o<1:
            gap=int(608+(H-608)*o); top=(H-gap)//2
            d=ImageDraw.Draw(fr); d.rectangle((0,0,W,top),fill='black'); d.rectangle((0,top+gap,W,H),fill='black')
        # flash
        if t<TT+0.12:
            fl=Image.new('RGBA',(W,H),(255,255,255,int(200*(1-(t-TT)/0.12)))); fr.alpha_composite(fl)
        if TT+0.5<t<10.0:
            p=(t-TT-0.5); sc=1.0 if p>0.15 else 0.6+0.4*p/0.15
            bubble(fr,'VAI COL TANGO!',alpha=min(1,(10.0-t)/0.2),scale=sc)
        if t>=10.0:
            d=ImageDraw.Draw(fr); a=ease((t-10.0)/0.3)
            sh=Image.new('RGBA',(W,H)); sd=ImageDraw.Draw(sh)
            for dd,(txt,y,font,col,sp) in enumerate([('BRONCO',260,fnt(cin(120),700),(255,236,190),16),('IL NUOVO PROFUMO',420,fnt(cin(50),500),(255,255,255),8),('Sa di caffè.',520,fnt(serif(92),600),(255,255,255),2)]):
                spaced(sd,txt,y+4,font,(0,0,0),int(170*a),sp); 
            sh=sh.filter(ImageFilter.GaussianBlur(6)); fr.alpha_composite(sh); d=ImageDraw.Draw(fr)
            spaced(d,'BRONCO',260,fnt(cin(120),700),(255,236,190),int(255*a),16)
            spaced(d,'IL NUOVO PROFUMO',420,fnt(cin(50),500),(255,255,255),int(255*a),8)
            spaced(d,'Sa di caffè.',520,fnt(serif(92),600),(255,255,255),int(255*a),2)
            if t>=10.5:
                b=ease((t-10.5)/0.25); fb=bang(78); tw=d.textlength('LA TAZZA È SU ETSY',font=fb)
                d.rounded_rectangle(((W-tw)/2-40,700,(W+tw)/2+40,800),radius=24,fill=(205,40,30,int(255*b)))
                d.text(((W-tw)/2,708),'LA TAZZA È SU ETSY',font=fb,fill=(255,255,255,int(255*b)))
                fs=fnt(serif(64),700); s2='link in bio'; tw2=d.textlength(s2,font=fs)
                d.text(((W-tw2)/2,820),s2,font=fs,fill=(255,255,255,int(255*b)),stroke_width=2,stroke_fill=(0,0,0,int(160*b)))
    out.stdin.write(fr.convert('RGB').tobytes())
out.stdin.close(); out.wait(); print('done')
