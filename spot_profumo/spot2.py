import subprocess, numpy as np, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
D='/tmp/claude-0/spot/'; FPS=30; W,H=1080,1920; BW,BH=1080,608; BANDY=(H-BH)//2
def frames(path,ch):
    p=subprocess.run(['ffmpeg','-v','error','-i',path,'-f','rawvideo','-pix_fmt','gray' if ch==1 else 'rgb24','-'],capture_output=True).stdout
    return np.frombuffer(p,np.uint8).reshape((-1,BH,BW) if ch==1 else (-1,BH,BW,3))
SH=[frames(D+f'seg2/s{i}.mp4',1) for i in range(1,6)]
B6=frames(D+'seg2/s6.mp4',3)
serif=lambda s: ImageFont.truetype(D+'fonts/CormorantGaramond.ttf',s)
cin=lambda s: ImageFont.truetype(D+'fonts/Cinzel.ttf',s)
def v(f,w):
    f.set_variation_by_axes([w]); return f
# shots: (start, length)
STEP,LEN=3.0,4.2
starts=[i*STEP for i in range(5)]+[15.0]
TOT=22.0
bron=Image.open(D+'L_bronco.png'); bh=600; bron=bron.resize((int(bron.width*bh/bron.height),bh),Image.LANCZOS)
mug=Image.open(D+'L_tazza.png').resize((340,340),Image.LANCZOS)
def ease(x): x=max(0,min(1,x)); return x*x*(3-2*x)
def shot_alpha(t,s,L,last=False):
    if t<s or (not last and t>s+L): return 0
    a=ease((t-s)/1.2)
    if not last: a=min(a,ease((s+L-t)/1.2))
    return a
def steam(t):
    L=Image.new('RGBA',(BW,BH)); d=ImageDraw.Draw(L)
    for k in range(3):
        x0=420+k*26; pts=[(x0+12*math.sin(j*0.4+t*3+k*2)+j*1.5, 480-j*6) for j in range(22)]
        d.line(pts,fill=(255,255,255,150),width=11,joint='curve')
    return L.filter(ImageFilter.GaussianBlur(5))
def bronco_scene(t):
    i=min(int((t-starts[5])*FPS),len(B6)-1)
    bg=Image.fromarray(B6[i]).filter(ImageFilter.GaussianBlur(1.6)).convert('RGBA')
    f=bg; bob=-int(5*abs(math.sin((t-16.6)*7))) if 16.6<t<17.8 else 0
    f.alpha_composite(bron,(-20,BH-bh+140+bob))
    f.alpha_composite(steam(t))
    f.alpha_composite(mug,(330,BH-mug.height+75))
    # colour bloom: B/W until 15.8, colour by 17.3
    sat=ease((t-15.8)/1.5)
    g=f.convert('L').convert('RGB'); c=f.convert('RGB')
    return Image.blend(g,c,sat)
def spaced(d,txt,y,font,fill,a,sp):
    if a<=0: return
    ws=[d.textlength(c,font=font) for c in txt]; tw=sum(ws)+sp*(len(txt)-1); x=(W-tw)/2
    for c,w in zip(txt,ws): d.text((x,y),c,font=font,fill=fill+(int(255*a),)); x+=w+sp
WORDS=[  # text, start, end, y, font, size, weight, sp, colour
 ('INTENSO',4.0,6.9,0,'s',66,400,18),
 ('AUDACE',7.0,9.9,0,'s',66,400,18),
 ('INDIMENTICABILE',10.0,12.9,0,'s',58,400,10),
 ('IL NUOVO PROFUMO DI',13.0,15.6,0,'c',46,400,8),
 ('BRONCO',16.6,TOT+1,0,'c',110,700,16),
 ('Sa di caffè.',18.0,TOT+1,140,'s',84,600,2),
]
GOLD=(232,214,170); WHITE=(240,236,228)
out=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','18',D+'video2_muto.mp4'],stdin=subprocess.PIPE)
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
    fr=Image.new('RGBA',(W,H),(0,0,0,255))
    fr.paste(Image.fromarray(np.clip(band,0,255).astype('uint8')),(0,BANDY))
    d=ImageDraw.Draw(fr)
    for txt,s,e,dy,ft,sz,wg,sp in WORDS:
        a=ease((t-s)/0.8)*ease((e-t)/0.6)
        font=v(serif(sz) if ft=='s' else cin(sz),wg)
        col=GOLD if ft=='c' else WHITE
        spaced(d,txt,BANDY+BH+70+dy,font,col,a,sp)
    # Etsy line under, elegant
    if t>19.3:
        a=ease((t-19.3)/0.8)
        spaced(d,'“VAI COL TANGO!”',BANDY-200,v(cin(44),500),GOLD,a,6)
        spaced(d,'La tazza di Bronco è su Etsy',BANDY+BH+330,v(serif(52),600),WHITE,a,1)
        spaced(d,'link in bio',BANDY+BH+400,v(serif(46),500),(200,190,170),a,3)
    out.stdin.write(fr.convert('RGB').tobytes())
out.stdin.close(); out.wait(); print('ok')
