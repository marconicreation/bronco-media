#!/usr/bin/env python3
"""Card citazione 1080x1080. Uso: python3 tools/quote.py OUT.jpg "Citazione" "Autore" ["Opera/anno"]
Solo citazioni VERE e verificate (cerca la fonte sul web), brevi (max ~25 parole)."""
import sys,os
from PIL import Image,ImageDraw,ImageFont
D=os.path.dirname(os.path.abspath(__file__))
def font(sz,w=500):
    f=ImageFont.truetype(os.path.join(D,"PlayfairDisplay-Italic.ttf"),sz)
    try:f.set_variation_by_axes([w])
    except Exception:pass
    return f
out,quote,author=sys.argv[1:4];work=sys.argv[4] if len(sys.argv)>4 else ""
S=1080;im=Image.new("RGB",(S,S));px=im.load()
for y in range(S):
    t=y/S;c=(int(14+22*t),int(26+36*t),int(46+52*t))
    for x in range(S):px[x,y]=c
d=ImageDraw.Draw(im);GOLD=(232,190,96);CREAM=(246,238,222)
d.rectangle([36,36,S-36,S-36],outline=GOLD,width=3);d.rectangle([48,48,S-48,S-48],outline=(232,190,96,90),width=1)
d.text((90,60),"“",font=font(300,700),fill=GOLD)
def wrap(t,f,w):
    o=[];c=""
    for wd in t.split():
        n=(c+" "+wd).strip()
        if d.textlength(n,font=f)<=w:c=n
        else:o.append(c);c=wd
    o.append(c);return o
sz=76
while True:
    f=font(sz,500);ls=wrap(quote,f,S-240);lh=int(sz*1.3)
    if len(ls)*lh<=520 or sz<40:break
    sz-=3
y=max(250,(S-len(ls)*lh)//2-30)
for l in ls:
    d.text(((S-d.textlength(l,font=f))/2,y),l,font=f,fill=CREAM);y+=lh
y+=24;d.line([(S/2-60,y),(S/2+60,y)],fill=GOLD,width=3);y+=26
fa=font(46,700);t="— "+author;d.text(((S-d.textlength(t,font=fa))/2,y),t,font=fa,fill=GOLD)
if work:
    fw=font(34,400);d.text(((S-d.textlength(work,font=fw))/2,y+62),work,font=fw,fill=(200,190,170))
lg=Image.open(os.path.join(D,"bronco_logo.png")).convert("RGB").resize((120,120))
m=Image.new("L",(120,120),0);ImageDraw.Draw(m).ellipse([0,0,119,119],fill=255);im.paste(lg,(S-190,S-190),m)
d.ellipse([S-192,S-192,S-68,S-68],outline=GOLD,width=3)
im.save(out,quality=93)
