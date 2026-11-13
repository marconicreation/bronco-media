"""Sigla di apertura di "Al bancone di Bronco" (Reel verticale 1080x1920, ~10 s).

Uso:
  python3 sigla.py                         -> crea sigla.mp4 in questa cartella
  python3 sigla.py --anteponi EP.mp4 OUT.mp4  -> mette la sigla davanti a un episodio gia' montato

Struttura (a tempo di musica, 144 bpm, 1 battuta = 1,667 s):
  battuta 1: Bronco "il barista"   | 2: Bartolomeo "l'inventore" | 3: Geremia "il brontolone"
  battute 4-6: clip animata dei tre al bancone (Higgsfield, clip_trio.mp4) + titolo
Musica: funk originale sintetizzata qui (batteria, giro di basso, fiati), nessun diritto.
"""
import sys, os, subprocess, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
POSE = '/mnt/project-files/sitcom/ep01/pose'
FONT = '/home/user/bronco-media/Bangers-Regular.ttf'
CLIP = os.path.join(HERE, 'clip_trio.mp4')
OUT = os.path.join(HERE, 'sigla.mp4')
W, H, FPS = 1080, 1920, 30
BPM = 144; BEAT = 60 / BPM; BAR = 4 * BEAT
INK = (20, 12, 8); GOLD = (255, 214, 90); CREAM = (255, 246, 228)

PERSONAGGI = [  # (posa, nome, ruolo, colore sfondo, entra da)
    ('bronco_papillon.png', 'BRONCO', 'il barista', (194, 50, 31), -1),
    ('bartolomeo_annuncia.png', 'BARTOLOMEO', "l'inventore", (46, 110, 64), 1),
    ('geremia_strilla.png', 'GEREMIA', 'il brontolone', (52, 70, 140), -1),
]

f_name = ImageFont.truetype(FONT, 150); f_role = ImageFont.truetype(FONT, 80)
f_title = ImageFont.truetype(FONT, 165); f_tag = ImageFont.truetype(FONT, 50)

def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def back(t):  # entrata con piccolo rimbalzo
    t = max(0.0, min(1.0, t)); c = 1.7; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2

def rays(color, t):
    """Sfondo a raggi che ruotano (stile sigla anni '80)."""
    c = Image.new('RGB', (W, H), color); d = ImageDraw.Draw(c)
    light = tuple(min(255, int(v * 1.25 + 25)) for v in color)
    cx, cy, R = W / 2, 900, 2400; a0 = t * 0.6
    for i in range(16):
        a = a0 + i * np.pi / 8
        d.polygon([(cx, cy), (cx + R * np.cos(a), cy + R * np.sin(a)), (cx + R * np.cos(a + np.pi / 16), cy + R * np.sin(a + np.pi / 16))], fill=light)
    return c

def framed(path, size):
    im = Image.open(path).convert('RGB').resize((size, size), Image.LANCZOS)
    m = Image.new('L', (size, size), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size - 1, size - 1), 60, fill=255)
    out = Image.new('RGB', (size + 28, size + 28), CREAM); out.paste(im, (14, 14), m)
    return out

def intro(path, name, role, color, side):
    n = int(round(BAR * FPS)); pic = framed(os.path.join(POSE, path), 860)
    for k in range(n):
        t = k / FPS; c = rays(color, t); d = ImageDraw.Draw(c)
        x = int((W - pic.width) / 2 + side * (1 - back(t / 0.35)) * 1100)
        bob = int(8 * np.sin(2 * np.pi * t / BEAT))  # oscilla a tempo
        c.paste(pic, (x, 300 + bob))
        s = ease((t - 0.25) / 0.25)
        if s > 0:
            ny = 1330 + int((1 - s) * 200)
            d.text((W // 2, ny), name, font=f_name, fill=GOLD, anchor='mm', stroke_width=10, stroke_fill=INK)
            d.text((W // 2, ny + 135), role, font=f_role, fill=CREAM, anchor='mm', stroke_width=6, stroke_fill=INK)
        d.text((W // 2, 1840), '@marconicreation', font=f_tag, fill=CREAM, anchor='mm')
        yield c

def clip_frames(dur):
    tmp = tempfile.mkdtemp(); raw = os.path.join(tmp, 'c.rgb')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', CLIP, '-t', str(dur), '-vf',
                    f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}',
                    '-f', 'rawvideo', '-pix_fmt', 'rgb24', raw], check=True)
    data = np.fromfile(raw, np.uint8).reshape(-1, H, W, 3)
    n = int(round(dur * FPS)); t_title = BAR * 1.0  # titolo dopo una battuta di clip
    for k in range(n):
        t = k / FPS; c = Image.fromarray(data[min(k, len(data) - 1)]); d = ImageDraw.Draw(c)
        if k < 6:  # lampo bianco di stacco
            c = Image.blend(c, Image.new('RGB', (W, H), 'white'), 1 - k / 6); d = ImageDraw.Draw(c)
        s = back((t - t_title) / 0.4)
        if t >= t_title:
            sz = max(0.05, s)
            for i, line in enumerate(['AL BANCONE', 'DI BRONCO']):
                f = ImageFont.truetype(FONT, max(10, int(165 * sz)))
                d.text((W // 2, 1450 + i * 175), line, font=f, fill=GOLD, anchor='mm', stroke_width=max(1, int(12 * sz)), stroke_fill=INK)
        d.text((W // 2, 1840), '@marconicreation', font=f_tag, fill=CREAM, anchor='mm', stroke_width=3, stroke_fill=INK)
        yield c

# ---------------- musica: funk originale ----------------
SR = 44100
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)

def music(sec, path):
    N = int(sec * SR); y = np.zeros(N + SR); s16 = BEAT / 4
    def add(sig, at):
        i = int(at * SR); y[i:i + len(sig)] += sig[:len(y) - i]
    rng = np.random.RandomState(7)
    def kick():
        n = int(0.25 * SR); t = np.arange(n) / SR; f = 50 + 90 * np.exp(-t * 30)
        return 0.9 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    def snare():
        n = int(0.2 * SR); t = np.arange(n) / SR
        return (0.45 * rng.randn(n) * np.exp(-t * 22) + 0.3 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25))
    def hat(open_=False):
        n = int((0.12 if open_ else 0.04) * SR); x = rng.randn(n); x = np.diff(np.concatenate([[0], x]))
        return 0.12 * x * np.exp(-np.arange(n) / SR * (18 if open_ else 80))
    def bass(freq, dur):
        n = int(dur * SR); t = np.arange(n) / SR
        saw = 2 * ((freq * t) % 1) - 1; sq = np.sign(np.sin(2 * np.pi * freq * t))
        x = 0.6 * np.sin(2 * np.pi * freq * t) + 0.25 * saw + 0.15 * sq
        k = int(SR / (freq * 6)) or 1; x = np.convolve(x, np.ones(k) / k, 'same')  # filtro morbido
        e = env(n, 0.004, 0.22); e[-200:] *= np.linspace(1, 0, 200)
        return 0.55 * x * e
    def brass(freqs, dur):
        n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
        for f in freqs:
            vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t)
            ph = np.cumsum(f * vib) / SR
            for h in range(1, 7): x += np.sin(2 * np.pi * h * ph) / h ** 1.2
        e = np.minimum(1, t / 0.02) * np.exp(-t * 2.5); e[-300:] *= np.linspace(1, 0, 300)
        return 0.07 * x * e
    note = lambda m: 440 * 2 ** ((m - 69) / 12)
    E1 = 28 + 12  # Mi basso (E2)
    # giro di basso funk in Mi (16 sedicesimi per battuta): (sedicesimo, semitoni sopra Mi, durata in sedicesimi)
    riff_a = [(0, 0, 2), (3, 0, 1), (4, 12, 1), (6, 10, 1), (7, 0, 2), (10, 3, 1), (11, 5, 1), (12, 7, 2), (14, 10, 1), (15, 12, 1)]
    riff_b = [(0, 5, 2), (3, 5, 1), (4, 17, 1), (6, 15, 1), (7, 5, 2), (10, 7, 1), (11, 8, 1), (12, 10, 1), (13, 11, 1), (14, 12, 2)]
    bars = int(np.ceil(sec / BAR))
    for b in range(bars):
        t0 = b * BAR; last = b == bars - 1
        riff = riff_b if b % 4 == 2 else riff_a
        for s in range(16):
            if s in (0, 7, 10) or (s == 14 and b % 2): add(kick(), t0 + s * s16)
            if s in (4, 12): add(snare(), t0 + s * s16)
            if s in (15,) and b % 2: add(0.5 * snare(), t0 + s * s16)
            add(hat(open_=(s % 4 == 2)), t0 + s * s16 + (0.012 if s % 2 else 0))
        if not last:
            for s, semi, ln in riff: add(bass(note(E1 + semi), ln * s16 * 0.95), t0 + s * s16)
            # stacchetti di fiati sul levare, a ogni presentazione
            ch = [note(64), note(67), note(71), note(74)] if b % 2 == 0 else [note(62), note(66), note(69), note(72)]
            add(brass(ch, 1.5 * s16), t0 + 6 * s16); add(brass(ch, 3 * s16), t0 + 14 * s16)
        else:  # finale: "ta-daaa" sul titolo
            add(bass(note(E1), 3 * s16), t0); add(bass(note(E1), 1.5 * BAR), t0 + 3 * s16 * 1.0 + 0.0)
            add(brass([note(64), note(68), note(71), note(76)], 1.5 * s16), t0)
            add(1.4 * brass([note(64), note(68), note(71), note(74), note(76)], BAR * 0.95), t0 + 2 * s16)
            add(kick(), t0); add(snare(), t0); add(kick(), t0 + 2 * s16); add(snare(), t0 + 2 * s16)
    y = y[:N]; y = np.tanh(1.4 * y) / np.tanh(1.4)  # un po' di calore
    y *= np.clip((sec - np.arange(N) / SR) / 0.3, 0, 1); y *= 0.85 / max(1e-6, np.abs(y).max())
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())

def build(out=OUT):
    tmp = tempfile.mkdtemp(); vid = os.path.join(tmp, 'v.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '19', vid], stdin=subprocess.PIPE)
    n = 0
    for args in PERSONAGGI:
        for f in intro(*args): p.stdin.write(f.tobytes()); n += 1
    for f in clip_frames(3 * BAR): p.stdin.write(f.tobytes()); n += 1
    p.stdin.close(); p.wait()
    music(n / FPS, os.path.join(tmp, 'm.wav'))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vid, '-i', os.path.join(tmp, 'm.wav'), '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
                    '-ar', '44100', '-ac', '1', '-shortest', '-movflags', '+faststart', out], check=True)
    print(out, round(n / FPS, 2), 's')

def anteponi(ep, out):
    if not os.path.exists(OUT): build()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', OUT, '-i', ep, '-filter_complex',
                    f'[0:v]fps={FPS},scale={W}:{H},setsar=1[a];[1:v]fps={FPS},scale={W}:{H},setsar=1[b];'
                    '[0:a]aresample=44100,aformat=channel_layouts=mono[x];[1:a]aresample=44100,aformat=channel_layouts=mono[y];'
                    '[a][x][b][y]concat=n=2:v=1:a=1[v][au]', '-map', '[v]', '-map', '[au]',
                    '-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out], check=True)
    print(out)

if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--anteponi': anteponi(sys.argv[2], sys.argv[3])
    else: build()
