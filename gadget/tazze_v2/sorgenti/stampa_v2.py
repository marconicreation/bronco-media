# Tazze v2: personaggio scontornato con contorno a inchiostro, esplosione fumetto a retino dietro, nastro col motto davanti.
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
FONT = "/mnt/project-files/gadget/Bangers.ttf"
CUT = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = sys.argv[2] if len(sys.argv) > 2 else "."
W, H = 2717, 1146
INK = (28, 22, 20, 255)
TAZZE = [
  dict(nome="geremia_caffe", cut="geremia_strilla_birefnet-general.png", righe=["NON PARLARMI", "PRIMA DEL CAFFÈ!"], alt=640,
       burst=(246, 178, 44), dots=(226, 120, 30), nastro=(178, 36, 30), testo=(255, 244, 222)),
  dict(nome="bartolomeo_sciabadu", cut="bartolomeo_sciabadu_birefnet-general.png", righe=["SCIABADÙ!"],
       burst=(150, 196, 104), dots=(104, 152, 70), nastro=(70, 104, 52), testo=(255, 244, 222)),
  dict(nome="bronco_tango", cut="bronco_papillon_birefnet-general.png", righe=["VAI COL TANGO!"],
       burst=(96, 172, 222), dots=(50, 120, 186), nastro=(196, 44, 36), testo=(255, 244, 222)),
]

def esplosione(S, colore, dots, punte=18):
    """Esplosione a punte morbide con retino e contorno a inchiostro, lato S."""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); c = S / 2
    pts = []
    for i in range(punte * 2):
        a = math.pi * i / punte - math.pi / 2
        r = (0.49 if i % 2 == 0 else 0.40) * S * (1 + 0.035 * math.sin(i * 2.3))
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    fill = Image.new("RGBA", (S, S), colore + (255,)); d = ImageDraw.Draw(fill)
    # retino: punti piu' grandi verso il bordo
    step = 30
    for y in range(0, S, step):
        for x in range((y // step % 2) * step // 2, S, step):
            rr = math.hypot(x - c, y - c) / (S / 2)
            r = 2 + 9 * max(0, rr - 0.25) ** 1.2
            d.ellipse((x - r, y - r, x + r, y + r), fill=dots + (255,))
    # bagliore chiaro al centro
    g = Image.new("L", (S, S), 0); ImageDraw.Draw(g).ellipse((c - S * .28, c - S * .28, c + S * .28, c + S * .28), fill=150)
    fill = Image.composite(Image.new("RGBA", (S, S), (255, 250, 230, 255)), fill, g.filter(ImageFilter.GaussianBlur(S * .08)))
    ink = m.filter(ImageFilter.MaxFilter(15))
    im.paste(Image.new("RGBA", (S, S), INK), (0, 0), ink); im.paste(fill, (0, 0), m)
    return im

def inchiostro(cut, px=9):
    a = cut.split()[3].point(lambda v: 255 if v > 110 else 0)
    big = a.filter(ImageFilter.MaxFilter(px * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2))
    out = Image.new("RGBA", cut.size, (0, 0, 0, 0)); out.paste(Image.new("RGBA", cut.size, INK), (0, 0), big)
    cut = cut.copy(); cut.putalpha(ImageChops.multiply(cut.split()[3], a.filter(ImageFilter.GaussianBlur(0.8))))
    out.alpha_composite(cut); return out

def nastro(w, h, colore, righe, testo):
    """Nastro con code ripiegate."""
    pad = 70; im = Image.new("RGBA", (w + 2 * pad, h + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    dark = tuple(int(v * .6) for v in colore)
    y0 = 40; yb = y0 + h
    # code dietro
    for s in (-1, 1):
        x = pad if s < 0 else pad + w
        tail = [(x - s * 10, y0 + 30), (x + s * (pad - 5), y0 + 30), (x + s * (pad - 40), y0 + 30 + h / 2), (x + s * (pad - 5), yb + 30), (x - s * 10, yb + 30)]
        d.polygon(tail, fill=dark, outline=INK, width=8)
        d.polygon([(x, yb), (x - s * 0, yb + 30), (x + s * 40, yb + 30)], fill=tuple(int(v * .4) for v in colore), outline=INK, width=6)
    d.rounded_rectangle((pad, y0, pad + w, yb), 14, fill=colore, outline=INK, width=9)
    d.line((pad + 20, y0 + 18, pad + w - 20, y0 + 18), fill=tuple(min(255, int(v * 1.3) + 25) for v in colore), width=6)
    n = len(righe); size = int(h / n * 0.80)
    f = ImageFont.truetype(FONT, size)
    while max(d.textlength(r, font=f) for r in righe) > w - 80:
        size -= 4; f = ImageFont.truetype(FONT, size)
    for i, r in enumerate(righe):
        y = y0 + h * (i + 0.5) / n + 6
        d.text((pad + w / 2 + 6, y + 6), r, font=f, fill=INK, anchor="mm", stroke_width=7, stroke_fill=INK)
        d.text((pad + w / 2, y), r, font=f, fill=testo, anchor="mm", stroke_width=7, stroke_fill=INK)
    return im

def disegno(t):
    SW, SH = 900, 1100
    im = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    B = 760; im.alpha_composite(esplosione(B, t["burst"], t["dots"]), ((SW - B) // 2, 40))
    cut = Image.open(CUT + "/" + t["cut"]).convert("RGBA"); cut = cut.crop(cut.split()[3].getbbox())
    nh = 2 if len(t["righe"]) == 2 else 1
    ch = t.get("alt", 800)
    cut = cut.resize((int(cut.width * ch / cut.height), ch), Image.LANCZOS)
    if cut.width > SW - 40: cut = cut.resize((SW - 40, int(cut.height * (SW - 40) / cut.width)), Image.LANCZOS)
    cut = inchiostro(cut)
    hb = 190 if nh == 1 else 300
    ytop_nastro = SH - hb - 70
    im.alpha_composite(cut, ((SW - cut.width) // 2, ytop_nastro + 110 - cut.height))
    rb = nastro(SW - 170, hb, t["nastro"], t["righe"], t["testo"])
    im.alpha_composite(rb, ((SW - rb.width) // 2, ytop_nastro))
    return im.crop(im.getbbox())

if __name__ == "__main__":
    for t in TAZZE:
        d0 = disegno(t); d0.save(f"{OUT}/{t['nome']}_disegno.png")
        stampa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); slot = W // 3
        f = min(slot * 0.94 / d0.width, H * 0.96 / d0.height); d1 = d0.resize((int(d0.width * f), int(d0.height * f)), Image.LANCZOS)
        for i in range(3):
            stampa.alpha_composite(d1, (slot * i + (slot - d1.width) // 2, (H - d1.height) // 2))
        stampa.save(f"{OUT}/{t['nome']}_stampa.png", dpi=(300, 300)); print("ok", t["nome"], d0.size, d1.size)
