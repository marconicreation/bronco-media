#!/usr/bin/env python3
"""Fumetto per Bronco. Uso:
python3 tools/caption.py IN.jpg OUT.jpg "Testo battuta" --hl parola1,parola2 --pos top|bottom --shape pill|rect --color 0..4 --tx 0.5 --lines 2
pos: top (default) o bottom. tx = posizione orizzontale della codina (0..1), puntala verso il corpo/guancia di Bronco, MAI sul muso.
Dopo il render CONTROLLA l'immagine: muso (occhi, naso, bocca) deve restare libero. Se coperto: cambia pos/tx/lines/shape."""
import argparse,os
from PIL import Image,ImageDraw,ImageFont
FONT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","Bangers-Regular.ttf")
COLS=[(255,224,64),(120,220,255),(255,150,200),(160,235,120),(255,170,90)]
K=(20,20,20);RED=(214,40,57)
def wrap(d,t,f,w):
    out=[];cur=""
    for wd in t.split():
        c=(cur+" "+wd).strip()
        if d.textlength(c,font=f)<=w:cur=c
        else:out.append(cur);cur=wd
    out.append(cur);return out
def main():
    a=argparse.ArgumentParser();a.add_argument("src");a.add_argument("dst");a.add_argument("text")
    a.add_argument("--hl",default="");a.add_argument("--pos",default="top");a.add_argument("--shape",default="pill")
    a.add_argument("--color",type=int,default=0);a.add_argument("--tx",type=float,default=0.5);a.add_argument("--lines",type=int,default=2)
    a.add_argument("--width",type=float,default=0.9,help="larghezza fumetto come frazione (0.4-0.95); stretto+lines 3-4 = fumetto verticale")
    o=a.parse_args()
    im=Image.open(o.src).convert("RGB");W,H=im.size;d=ImageDraw.Draw(im)
    bw=int(W*o.width);x0=(W-bw)//2;x1=x0+bw
    size=100
    while True:
        f=ImageFont.truetype(FONT,size);lines=wrap(d,o.text,f,bw-110)
        if len(lines)<=o.lines:break
        size-=4
    lh=int(size*1.06);h=lh*len(lines)+56
    y0=40 if o.pos=="top" else H-40-h-110
    y1=y0+h;tx=int(W*o.tx);fill=COLS[o.color%5]
    r=min(h//2,90) if o.shape=="pill" else 55
    hl=[k.strip().lower() for k in o.hl.split(",") if k.strip()]
    def shape(off,col):
        d.rounded_rectangle([x0+off,y0+off,x1+off,y1+off],radius=r,fill=col,outline=K,width=10)
        pts=[(tx-55+off,y1-8+off),(tx+65+off,y1-8+off),(tx+5+off,y1+(90 if o.pos=="top" else 110)+off)]
        d.polygon(pts,fill=col,outline=K)
    shape(12,K);shape(0,fill);d.rectangle([tx-47,y1-14,tx+57,y1-2],fill=fill)
    y=y0+28
    for ln in lines:
        w=d.textlength(ln,font=f);x=(W-w)/2
        for wd in ln.split(" "):
            c=RED if any(k in wd.lower() for k in hl) else K
            d.text((x,y),wd,font=f,fill=c);x+=d.textlength(wd+" ",font=f)
        y+=lh
    im.save(o.dst,quality=92)
main()
