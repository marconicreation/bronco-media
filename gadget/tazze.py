# Tazze dei personaggi: file di stampa (avvolgente 11oz, 2475x1155) + anteprima.
import sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
FONT = sys.argv[1] if len(sys.argv) > 1 else "Bangers.ttf"
POSE = "/mnt/project-files/sitcom/pose/"
OUT = "/mnt/project-files/gadget/tazze/"
W, H = 2717, 1146
TAZZE = [
  dict(nome="bartolomeo_sciabadu", posa="bartolomeo_sciabadu.jpg", crop=(300,60,1200,960),
       frase="SCIABADÙ!", sotto="Ho appena avuto un'idea.", colore=(96,128,72)),
  dict(nome="geremia_caffe", posa="geremia_strilla.jpg", crop=(130,90,1160,1120),
       frase="NON PARLARMI", frase2="PRIMA DEL CAFFÈ!", sotto="", colore=(170,40,35)),
  dict(nome="bronco_tango", posa="bronco_finale_tango.jpg", crop=(140,90,1160,1110),
       frase="VAI COL TANGO!", sotto="", colore=(205,60,40)),
]
def testo(d, xy, s, size, fill, stroke=10):
    f = ImageFont.truetype(FONT, size)
    d.text(xy, s, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=(20,20,20))
def tondo(img, dia, colore):
    img = img.resize((dia, dia), Image.LANCZOS)
    m = Image.new("L", (dia, dia), 0); ImageDraw.Draw(m).ellipse((0,0,dia-1,dia-1), fill=255)
    tot = dia + 60
    c = Image.new("RGBA", (tot, tot), (0,0,0,0)); d = ImageDraw.Draw(c)
    d.ellipse((0,0,tot-1,tot-1), fill=(20,20,20)); d.ellipse((12,12,tot-13,tot-13), fill=colore)
    d.ellipse((24,24,tot-25,tot-25), fill=(20,20,20))
    c.paste(img, (30,30), m); return c
def lato(t):
    p = Image.new("RGBA", (W//2, H), (255,255,255,0)); d = ImageDraw.Draw(p)
    img = Image.open(POSE + t["posa"]).convert("RGB").crop(t["crop"])
    due = "frase2" in t
    dia = 590 if due else 700
    c = tondo(img, dia, t["colore"]); p.alpha_composite(c, ((W//2 - c.width)//2, 40))
    y = 40 + c.height + 20
    if due:
        testo(d, (W//4, y+60), t["frase"], 145, t["colore"]); testo(d, (W//4, y+235), t["frase2"], 145, t["colore"])
    else:
        testo(d, (W//4, y+95), t["frase"], 200, t["colore"])
        if t["sotto"]:
            f = ImageFont.truetype(FONT, 70); d.text((W//4, y+230), t["sotto"], font=f, fill=(30,30,30), anchor="mm")
    return p
def anteprima(lato_img):
    # tazza vista di fronte con la stampa sul lato destro (manico a sinistra per chi beve con la destra)
    S = 1400; bg = Image.new("RGB", (S, S), (236,229,218)); d = ImageDraw.Draw(bg)
    mw, mh = 820, 960; x0, y0 = (S-mw)//2 + 90, (S-mh)//2 + 40
    # ombra
    sh = Image.new("L", (S,S), 0); ImageDraw.Draw(sh).ellipse((x0-40, y0+mh-50, x0+mw+40, y0+mh+60), fill=110)
    bg.paste((150,140,128), (0,0), sh.filter(ImageFilter.GaussianBlur(30)))
    # manico
    d.ellipse((x0-250, y0+190, x0+120, y0+700), outline=(245,245,243), width=85)
    d.ellipse((x0-250, y0+190, x0+120, y0+700), outline=(205,205,200), width=6)
    body = Image.new("RGB", (mw, mh), (250,250,248))
    # stampa avvolta: porzione centrale compressa ai bordi
    src = lato_img.convert("RGBA"); bw = src.width
    vis = Image.new("RGBA", (mw, mh), (0,0,0,0))
    sc = (mh - 120) / src.height; srcs = src.resize((int(bw*sc), int(src.height*sc)), Image.LANCZOS)
    for x in range(mw):
        th = math.asin((x - mw/2) / (mw/2) * 0.999); u = int(srcs.width/2 + th/(math.pi/2) * srcs.width*0.62)
        if 0 <= u < srcs.width: vis.paste(srcs.crop((u,0,u+1,srcs.height)), (x, 60))
    body.paste(vis, (0,0), vis)
    shade = Image.new("L", (mw, mh)); sd = shade.load()
    for x in range(mw):
        v = int(70 * (abs(x - mw*0.42) / (mw/2))**2.2)
        for y in range(mh): sd[x, y] = v
    body = Image.composite(Image.new("RGB",(mw,mh),(60,60,60)), body, shade)
    m = Image.new("L", (mw, mh), 0); ImageDraw.Draw(m).rounded_rectangle((0,0,mw-1,mh-1), 40, fill=255)
    bg.paste(body, (x0, y0), m)
    d.ellipse((x0, y0-35, x0+mw, y0+35), fill=(250,250,248), outline=(200,200,195), width=4)
    d.ellipse((x0+18, y0-22, x0+mw-18, y0+22), fill=(70,45,30))
    return bg
for t in TAZZE:
    l = lato(t); stampa = Image.new("RGB", (W, H), (255,255,255))
    stampa.paste(l, (0,0), l); stampa.paste(l, (W//2,0), l)
    stampa.save(OUT + t["nome"] + "_stampa.png", dpi=(300,300))
    anteprima(l).save(OUT + t["nome"] + "_anteprima.jpg", quality=90)
    print("ok", t["nome"])
