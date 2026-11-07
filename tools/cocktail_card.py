#!/usr/bin/env python3
"""Card "Il cocktail col tuo nome" 1080x1350 (formato Instagram/WhatsApp, stampabile).
Uso: python3 tools/cocktail_card.py SPEC.json OUT.jpg
SPEC.json: {"per": "Giulia", "nome": "Tramonto di Giulia", "dedica": "...",
            "ingredienti": ["4 cl gin", ...], "metodo": "...", "bicchiere": "...",
            "guarnizione": "...", "analcolico": "...", "posa": "shaker"}"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(D)
W, H = 1080, 1350
CREAM = (248, 240, 226); INK = (38, 30, 24); RUST = (179, 96, 26); GOLD = (214, 168, 80)


def play(sz, w=500):
    f = ImageFont.truetype(os.path.join(D, "PlayfairDisplay-Italic.ttf"), sz)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f


def bang(sz):
    return ImageFont.truetype(os.path.join(R, "Bangers-Regular.ttf"), sz)


def find_pose(name):
    for sub in ("nuove", "usate"):
        p = os.path.join(R, "pose", sub, name + ".jpg")
        if os.path.exists(p): return p
    return os.path.join(R, "pose", "nuove", "shaker.jpg")


def main(spec_path, out):
    s = json.load(open(spec_path, encoding="utf-8"))
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)

    # foto di Bronco in alto (520 px), sfumata verso il crema
    TOP = 540
    ph = Image.open(find_pose(s.get("posa", "shaker"))).convert("RGB")
    ph = ph.resize((W, W))
    ph = ph.crop((0, 120, W, 120 + TOP))
    im.paste(ph, (0, 0))
    fade = Image.new("L", (W, 120), 0)
    for y in range(120): ImageDraw.Draw(fade).line([(0, y), (W, y)], fill=int(255 * y / 119))
    im.paste(Image.new("RGB", (W, 120), CREAM), (0, TOP - 120), fade)

    # nastro "IL COCKTAIL DI ..."
    per = s["per"].upper()
    fb = bang(64)
    t = "IL COCKTAIL DI " + per
    tw = d.textlength(t, font=fb)
    bx0, by0 = (W - tw) / 2 - 34, TOP - 70
    d.rounded_rectangle([bx0, by0, bx0 + tw + 68, by0 + 84], 16, fill=RUST)
    d.text(((W - tw) / 2, by0 + 8), t, font=fb, fill=CREAM)

    y = by0 + 104

    def center(txt, f, col, yy):
        d.text(((W - d.textlength(txt, font=f)) / 2, yy), txt, font=f, fill=col)

    def wrap(txt, f, maxw):
        out, cur = [], ""
        for w_ in txt.split():
            n = (cur + " " + w_).strip()
            if d.textlength(n, font=f) <= maxw: cur = n
            else: out.append(cur); cur = w_
        out.append(cur); return out

    # nome del cocktail
    sz = 70
    while d.textlength(s["nome"], font=play(sz, 700)) > W - 140 and sz > 40: sz -= 2
    center(s["nome"], play(sz, 700), INK, y); y += sz + 18

    # dedica
    fd = play(32, 400)
    for l in wrap(s["dedica"], fd, W - 200):
        center(l, fd, (90, 70, 55), y); y += 42
    y += 10
    d.line([(W / 2 - 70, y), (W / 2 + 70, y)], fill=GOLD, width=3); y += 24

    # due colonne: ingredienti | metodo
    L, M = 80, W // 2 + 10
    fh = bang(40); fi = play(30, 500); fs = play(27, 400)
    d.text((L, y), "INGREDIENTI", font=fh, fill=RUST)
    d.text((M, y), "COME SI FA", font=fh, fill=RUST)
    yl = yr = y + 54
    for ing in s["ingredienti"]:
        for i, l in enumerate(wrap(ing, fi, M - L - 40)):
            d.text((L + (0 if i == 0 else 22), yl), ("• " if i == 0 else "") + l, font=fi, fill=INK); yl += 40
    for l in wrap(s["metodo"], fs, W - M - 70):
        d.text((M, yr), l, font=fs, fill=INK); yr += 37
    yr += 8
    for lab, key in (("Bicchiere: ", "bicchiere"), ("Guarnizione: ", "guarnizione")):
        if s.get(key):
            for i, l in enumerate(wrap(lab + s[key], fs, W - M - 70)):
                d.text((M, yr), l, font=fs, fill=INK); yr += 37
    y = max(yl, yr) + 16

    # versione analcolica
    if s.get("analcolico"):
        box = wrap("Senza alcol: " + s["analcolico"], fs, W - 220)
        hh = 24 + len(box) * 37
        d.rounded_rectangle([80, y, W - 80, y + hh], 14, fill=(240, 226, 202))
        yy = y + 12
        for l in box: d.text((110, yy), l, font=fs, fill=INK); yy += 37
        y += hh + 10

    # firma
    lg = Image.open(os.path.join(D, "bronco_logo.png")).convert("RGB").resize((96, 96))
    m = Image.new("L", (96, 96), 0); ImageDraw.Draw(m).ellipse([0, 0, 95, 95], fill=255)
    im.paste(lg, (80, H - 130), m)
    d.ellipse([78, H - 132, 178, H - 32], outline=GOLD, width=3)
    d.text((196, H - 118), "Creato da Bronco, il barista IA", font=play(30, 600), fill=INK)
    d.text((196, H - 78), "MarconiCreation · bevi responsabilmente", font=play(24, 400), fill=(110, 90, 70))
    d.rectangle([14, 14, W - 15, H - 15], outline=GOLD, width=3)
    if y > H - 140:
        print("ATTENZIONE: testo troppo lungo, accorcia (y=%d)" % y, file=sys.stderr)
    im.save(out, quality=93)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
