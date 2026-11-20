#!/usr/bin/env python3
"""Storie Instagram di Bronco (1080x1920), approvate da Robi il 20/11/2026.

Due modi:
  python3 tools/storia.py card SFONDO.jpg OUT.jpg "TITOLO" "riga 1" "riga 2" ...
      Immagine: sfondo a tutto schermo (ritagliato 9:16), titolo grande in
      Pricedown bianco con contorno nero spesso, righe sotto, firma in basso.
  python3 tools/storia.py clip PUNTATA.mp4 OUT.mp4 "TITOLO" ["riga"]
      Video: i primi 55 secondi della puntata con il titolo in alto.

Scritte SEMPRE Pricedown col contorno nero (regola di Robi, CLAUDE.md).
Le scritte stanno nella fascia sicura (niente nei 250 px in alto e in basso,
dove Instagram mette nome e barra delle risposte).
"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FONT = "/mnt/project-files/fonts/Pricedown_Bl.otf"
RISERVA = os.path.join(os.path.dirname(__file__), "..", "Bangers-Regular.ttf")
FIRMA = "AL BANCONE DI BRONCO  ·  @marconicreation"


def font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.truetype(RISERVA, size)


def a_capo(draw, testo, f, larghezza):
    parole, righe, riga = testo.split(), [], ""
    for p in parole:
        prova = (riga + " " + p).strip()
        if draw.textlength(prova, font=f) <= larghezza or not riga:
            riga = prova
        else:
            righe.append(riga)
            riga = p
    if riga:
        righe.append(riga)
    return righe


def scritta(draw, y, testo, size, colore="white", larghezza=W - 140):
    """Scrive testo centrato stile GTA. Ritorna la y sotto il blocco."""
    while size > 40:
        f = font(size)
        righe = a_capo(draw, testo, f, larghezza)
        if len(righe) <= 4:
            break
        size -= 8
    contorno = max(6, size // 9)
    for r in righe:
        w = draw.textlength(r, font=f)
        draw.text(((W - w) / 2, y), r, font=f, fill=colore,
                  stroke_width=contorno, stroke_fill="black")
        y += int(size * 1.08)
    return y


def sfondo(path):
    img = Image.open(path).convert("RGB")
    s = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * s) + 1, int(img.height * s) + 1), Image.LANCZOS)
    x, y = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((x, y, x + W, y + H))


def velo(img, alto=0.55, basso=0.35):
    """Sfuma in nero in alto e in basso così le scritte si leggono."""
    v = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(v)
    for y in range(H):
        a = 0
        if y < H * alto:
            a = int(170 * (1 - y / (H * alto)))
        if y > H * (1 - basso):
            a = max(a, int(170 * (y - H * (1 - basso)) / (H * basso)))
        d.line([(0, y), (W, y)], fill=a)
    nero = Image.new("RGB", (W, H), "black")
    return Image.composite(nero, img, v)


def card(src, out, titolo, righe):
    img = velo(sfondo(src))
    d = ImageDraw.Draw(img)
    y = scritta(d, 280, titolo.upper(), 124, colore="white")
    y += 30
    for i, r in enumerate(righe):
        y = scritta(d, y, r, 66, colore="#ffd23f" if i == 0 else "white") + 18
    f = font(44)
    w = d.textlength(FIRMA, font=f)
    d.text(((W - w) / 2, H - 330), FIRMA, font=f, fill="white", stroke_width=5, stroke_fill="black")
    img.save(out, "JPEG", quality=90, optimize=True)
    print(out, os.path.getsize(out), "byte")


def clip(src, out, titolo, righe):
    tmp = tempfile.mkdtemp()
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    y = scritta(d, 270, titolo.upper(), 120)
    for r in righe:
        y = scritta(d, y + 10, r, 64, colore="#ffd23f")
    png = os.path.join(tmp, "ov.png")
    ov.save(png)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", src, "-i", png, "-t", "55",
        "-filter_complex", f"[0:v]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1[v];[v][1:v]overlay=0:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out,
    ], check=True)
    print(out, os.path.getsize(out), "byte")


if __name__ == "__main__":
    if len(sys.argv) < 5 or sys.argv[1] not in ("card", "clip"):
        sys.exit(__doc__)
    modo, src, out, titolo, *righe = sys.argv[1:]
    (card if modo == "card" else clip)(src, out, titolo, righe)
