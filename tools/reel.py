#!/usr/bin/env python3
"""Reel verticale di Bronco (1080x1920, ~11 s) dalla posa con fumetto. Gratis: solo PIL + numpy + ffmpeg.
Uso:
  python3 tools/reel.py POSA_PULITA.jpg POSA_CON_FUMETTO.jpg OUT.mp4 --hook "TESTO IN ALTO" [--cta regalo|segui]
- POSA_PULITA: pose/nuove/X.jpg (senza fumetto); POSA_CON_FUMETTO: l'immagine fatta con tools/caption.py
  (già controllata: muso libero). Il fumetto compare dopo ~1 s con un "pop".
- Se POSA_CON_FUMETTO è lo stesso file di POSA_PULITA: niente fumetto né pop (utile per la card citazione
  di tools/quote.py, o per una posa pulita con la battuta scritta solo in alto nel --hook).
- --hook: testo in alto, va a capo da solo (max 3 righe, ~60 caratteri). Breve tema ("BOLLETTE") oppure
  la battuta intera. Mai nomi di persone o partiti.
- --cta regalo (default fino al 24/12): chiusura 3,5 s sul regalo "Il cocktail col tuo nome", link in bio.
  --cta segui: chiusura "Segui Bronco".
- Musica: base lounge sintetizzata qui (nessun diritto d'autore) + suono pop sul fumetto.
Dopo il render GUARDA 2-3 fotogrammi (ffmpeg -ss 2 -i OUT.mp4 -frames:v 1 f.jpg) prima di pubblicare."""
import argparse, os, subprocess, tempfile, math, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FONT = os.path.join(R, "Bangers-Regular.ttf")
W, H, FPS = 1080, 1920, 30
BG = (38, 22, 14); YEL = (255, 214, 90); CREAM = (230, 200, 160)
SR = 44100


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def font(s): return ImageFont.truetype(FONT, s)


def title(img, txt, t, y, f, fill=YEL, drop=160):
    d = ImageDraw.Draw(img)
    p = ease(t / 0.35); dy = int((1 - p) * -drop)
    d.multiline_text((W // 2, y + dy), txt, font=f, fill=fill, anchor='mm', align='center',
                     stroke_width=8, stroke_fill=(0, 0, 0), spacing=8)


def fit_hook(txt, maxw, start=150, minsize=58, maxlines=3):
    """Ritorna (font, testo a capo) che sta in maxw su massimo 3 righe."""
    d = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    s = start
    while True:
        f = font(s); lines = []
        for par in txt.split("\n"):
            cur = ""
            for w in par.split():
                c = (cur + " " + w).strip()
                if d.textlength(c, font=f) <= maxw or not cur: cur = c
                else: lines.append(cur); cur = w
            lines.append(cur)
        if (len(lines) <= maxlines and max(d.textlength(l, font=f) for l in lines) <= maxw) or s <= minsize:
            return f, "\n".join(lines)
        s -= 6


# ---------- scena principale: posa + fumetto ----------
def scene_main(clean, capt, hook, dur, pop=True, tag="BRONCO DICE LA SUA"):
    hf, hook = fit_hook(hook, W - 120)
    sm = font(64)
    n = int(dur * FPS)
    POP = 1.0  # secondo in cui compare il fumetto
    for k in range(n):
        t = k / FPS
        z = 1.0 + 0.10 * ease(t / dur)                       # zoom lento
        z += 0.012 * abs(math.sin(2 * math.pi * t * 0.83))    # "respiro" a tempo di musica
        if pop and t >= POP:                                          # piccolo colpo quando arriva il fumetto
            z += 0.035 * max(0.0, 1 - (t - POP) / 0.25)
        a = ease((t - POP) / 0.18) if pop else 1
        src = clean if a <= 0 else (capt if a >= 1 else Image.blend(clean, capt, a))
        s = int(1080 * z); big = src.resize((s, s), Image.BILINEAR)
        off = (s - 1080) // 2
        bob = int(6 * math.sin(2 * math.pi * t * 0.83))
        crop = big.crop((off, off, off + 1080, off + 1080))
        c = Image.new('RGB', (W, H), BG)
        c.paste(crop, (0, 430 + bob))
        title(c, hook, t, 250, hf)
        ImageDraw.Draw(c).text((W // 2, 1640), tag, font=sm, fill='white',
                               anchor='mm', stroke_width=6, stroke_fill='black')
        ImageDraw.Draw(c).text((W // 2, 1810), "@marconicreation", font=sm, fill=CREAM, anchor='mm')
        yield c


# ---------- chiusura ----------
def scene_end(kind, dur):
    logo = Image.open(os.path.join(R, 'tools/bronco_logo.png')).convert('RGBA').resize((360, 360))
    big, mid, sm = font(112), font(84), font(64)
    for k in range(int(dur * FPS)):
        t = k / FPS
        c = Image.new('RGB', (W, H), BG)
        c.paste(logo, ((W - 360) // 2, 330), logo)
        if kind == 'regalo':
            title(c, "IL COCKTAIL\nCOL TUO NOME", t, 880, big)
            if t > 0.4: title(c, "REGALO DI NATALE · 5 €", t - 0.4, 1130, mid, 'white')
            if t > 0.8: title(c, "BRONCO LO INVENTA PER CHI VUOI TU", t - 0.8, 1260, sm, CREAM)
            if t > 1.2: title(c, "ORDINA DAL LINK IN BIO", t - 1.2, 1500, mid)
        else:
            title(c, "TI È PIACIUTA?", t, 900, big)
            if t > 0.5: title(c, "SEGUI BRONCO", t - 0.5, 1130, mid, 'white')
            if t > 1.0: title(c, "BATTUTE DAL BANCONE\nOGNI GIORNO", t - 1.0, 1330, sm, CREAM)
        ImageDraw.Draw(c).text((W // 2, 1800), "@marconicreation", font=sm, fill=CREAM, anchor='mm')
        yield c


# ---------- musica ----------
def music(dur, pop_at=None):
    n = int(dur * SR); out = np.zeros(n)
    bpm = 100; beat = 60 / bpm; bar = 4 * beat
    def note(m): return 440 * 2 ** ((m - 69) / 12)
    # ii-V-I-VI in Do: Dm9, G13, Cmaj9, A7(b9)
    chords = [[50, 53, 57, 60, 64], [43, 53, 57, 59, 64], [48, 52, 55, 59, 62], [45, 55, 58, 61, 64]]
    bass = [38, 31, 36, 33]
    def add(f, start, length, vol, decay, harm=(1, .5, .25)):
        i0 = int(start * SR); m = min(int(length * SR), n - i0)
        if m <= 0: return
        tt = np.arange(m) / SR
        env = np.exp(-tt * decay) * np.minimum(1, tt / 0.008)
        sig = sum(h * np.sin(2 * np.pi * f * (j + 1) * tt) for j, h in enumerate(harm))
        out[i0:i0 + m] += vol * env * sig
    rng = np.random.default_rng(7)
    t = 0.0; ci = 0
    while t < dur:
        ch = chords[ci % 4]
        for hit in (0, 1.5 * beat, 2.5 * beat):            # comping morbido
            for m in ch[1:]: add(note(m + 12), t + hit, 1.4, 0.035, 2.2, (1, .35, .12))
        for b in range(4):                                  # basso che cammina
            add(note(bass[ci % 4] + (0, 7, 12, 7)[b]), t + b * beat, beat * 0.95, 0.16, 3.0, (1, .3))
        for e in range(8):                                  # shaker (il rumore del bancone)
            i0 = int((t + e * beat / 2) * SR); m = min(int(0.07 * SR), n - i0)
            if m > 0:
                tt = np.arange(m) / SR
                nz = rng.standard_normal(m); nz = np.diff(np.concatenate([[0], nz]))
                out[i0:i0 + m] += (0.05 if e % 2 else 0.03) * nz * np.exp(-tt * 45)
        t += bar; ci += 1
    # pop del fumetto
    if pop_at is not None:
        i0 = int(pop_at * SR); m = int(0.12 * SR); tt = np.arange(m) / SR
        f = 900 * np.exp(-tt * 18) + 250
        out[i0:i0 + m] += 0.35 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 30)
    fo = int(1.2 * SR); out[-fo:] *= np.linspace(1, 0, fo)
    out /= max(1e-6, np.abs(out).max()) / 0.8
    return (out * 32767).astype(np.int16)


def main():
    a = argparse.ArgumentParser()
    a.add_argument('clean'); a.add_argument('capt'); a.add_argument('out')
    a.add_argument('--hook', default="DAL BANCONE"); a.add_argument('--cta', default='regalo'); a.add_argument('--tag', default='BRONCO DICE LA SUA')
    a.add_argument('--main', type=float, default=7.0); a.add_argument('--end', type=float, default=3.5)
    o = a.parse_args()
    clean = Image.open(o.clean).convert('RGB').resize((1080, 1080))
    pop = os.path.abspath(o.capt) != os.path.abspath(o.clean)
    capt = Image.open(o.capt).convert('RGB').resize((1080, 1080))
    hook = o.hook.upper().replace("\\N", "\n")
    tmp = tempfile.mkdtemp()
    v, wa = os.path.join(tmp, 'v.mp4'), os.path.join(tmp, 'a.wav')
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '24', v],
                           stdin=subprocess.PIPE)
    FADE = int(0.35 * FPS); last = []
    for f in scene_main(clean, capt, hook, o.main, pop, o.tag.upper()):
        last.append(f)
        if len(last) > FADE: enc.stdin.write(last.pop(0).tobytes())
    end = scene_end(o.cta, o.end)
    for i, f in enumerate(end):
        if last:
            f = Image.blend(last.pop(0), f, (i + 1) / (FADE + 1))
        enc.stdin.write(f.tobytes())
    enc.stdin.close(); enc.wait()
    dur = o.main + o.end
    with wave.open(wa, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(music(dur, 1.0 if pop else None).tobytes())
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', v, '-i', wa, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
                    '-shortest', '-movflags', '+faststart', o.out], check=True)
    print(o.out)


if __name__ == '__main__':
    main()
