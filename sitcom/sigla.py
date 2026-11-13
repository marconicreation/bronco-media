"""Sigla di apertura di "Al bancone di Bronco" (Reel verticale 1080x1920, ~10 s).

Uso:
  python3 sigla.py                         -> crea sigla.mp4 in questa cartella
  python3 sigla.py --anteponi EP.mp4 OUT.mp4  -> mette la sigla davanti a un episodio gia' montato

Struttura (a tempo di musica, 132 bpm, 1 battuta = 1,82 s):
  battuta 1: Bronco "il barista"   | 2: Bartolomeo "l'inventore" | 3: Geremia "il brontolone"
  battute 4-6: clip animata dei tre al bancone (Higgsfield, clip_trio.mp4) + titolo
Musica: funk stile sigle TV anni '70, originale e sintetizzata qui (basso in primo piano, clavinet, archi, fiati), nessun diritto.
"""
import sys, os, subprocess, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
POSE = '/mnt/project-files/sitcom/ep01/pose'
FONT = '/home/user/bronco-media/Bangers-Regular.ttf'
CLIP = os.path.join(HERE, 'clip_trio.mp4')
OUT = os.path.join(HERE, 'sigla.mp4')
MUSICA = None  # python3 sigla.py --musica FILE.wav|mp3 usa una base esterna invece di quella sintetizzata
W, H, FPS = 1080, 1920, 30
BPM = 132; BEAT = 60 / BPM; BAR = 4 * BEAT
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

# ---------------- musica: funk anni '70 originale, basso in primo piano ----------------
SR = 44100
def lp(x, fc, q=2.0):
    """Passa-basso morbido via FFT (rolloff tipo filtro analogico)."""
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** (2 * q)), len(x))
def hp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X * (1 - 1 / np.sqrt(1 + (f / fc) ** 4)), len(x))

def music(sec, path):
    N = int(sec * SR); y = np.zeros(N + 2 * SR); s16 = BEAT / 4
    bus = {k: np.zeros_like(y) for k in ('dr', 'bass', 'clav', 'str', 'br')}
    def add(k, sig, at):
        i = int(at * SR)
        if i < len(y): bus[k][i:i + len(sig)] += sig[:len(y) - i]
    rng = np.random.RandomState(7)
    note = lambda m: 440 * 2 ** ((m - 69) / 12)
    def kick():
        n = int(0.3 * SR); t = np.arange(n) / SR; f = 45 + 70 * np.exp(-t * 25)
        return 0.8 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8)
    def snare():  # rullante secco anni '70, poco riverbero
        n = int(0.18 * SR); t = np.arange(n) / SR
        return lp(0.4 * rng.randn(n) * np.exp(-t * 28), 6000) + 0.25 * np.sin(2 * np.pi * 180 * t) * np.exp(-t * 30)
    def hat(o=False):
        n = int((0.15 if o else 0.035) * SR); x = hp(rng.randn(n), 7000)
        return 0.18 * x * np.exp(-np.arange(n) / SR * (14 if o else 90))
    def tamb():
        n = int(0.12 * SR); x = hp(rng.randn(n), 5000); t = np.arange(n) / SR
        return 0.13 * x * (np.exp(-t * 30) + 0.5 * np.exp(-((t - 0.03) ** 2) / 1e-4))
    def bass(m, dur, acc=1.0):
        """Basso elettrico suonato con le dita: attacco 'thump', corpo caldo, un filo di saturazione."""
        n = int(dur * SR); t = np.arange(n) / SR; f = note(m)
        x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.25 * (2 * ((f * t) % 1) - 1)
        x = lp(x, 350 + 1400 * acc, 1.5) + lp(x * np.exp(-t * 60), 2500) * 0.6  # filtro che si chiude + click
        x = np.tanh(2.2 * x) * np.minimum(1, t / 0.003) * (0.55 + 0.45 * np.exp(-t * 5))
        x[-int(0.008 * SR):] *= np.linspace(1, 0, int(0.008 * SR))
        return 0.5 * acc * x
    def clav(ms, dur):  # clavinet con wah
        n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
        for m in ms:
            f = note(m); x += np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + (2 * ((f * t) % 1) - 1) * 0.5
        x = hp(x, 500); x = lp(x, 1800, 3) * np.exp(-t * 18)
        return 0.05 * x
    def strings(ms, dur):
        n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
        for m in ms:
            for dt in (-0.12, 0, 0.13):
                f = note(m) * 2 ** (dt / 12); x += 2 * ((f * t + rng.rand()) % 1) - 1
        x = lp(x, 3000) * np.minimum(1, t / 0.25); x[-int(0.2 * SR):] *= np.linspace(1, 0, int(0.2 * SR))
        return 0.012 * x
    def brass(ms, dur, lvl=1.0):
        n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
        for m in ms:
            ph = np.cumsum(note(m) * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * t))) / SR
            for h in range(1, 8): x += np.sin(2 * np.pi * h * ph) / h ** 1.1
        e = np.minimum(1, t / 0.015) * np.exp(-t * 2.2); e[-300:] *= np.linspace(1, 0, 300)
        return 0.05 * lvl * x * e
    E = 40  # Mi basso
    # giro di basso anni '70 (sedicesimo, semitoni su Mi, durata in sedicesimi, accento): ottave, ghost note e salita cromatica
    riffA = [(0, 0, 3, 1), (3, 0, .8, .5), (4, 12, 1, .9), (5, 0, .8, .5), (6, 10, 1, .8), (7, 12, 1, .9), (8, 0, 2, 1), (10, 7, 1, .8), (11, 0, .8, .5), (12, 3, 1, .9), (13, 4, 1, .9), (14, 5, 1, .9), (15, 6, 1, .9)]
    riffB = [(0, 5, 3, 1), (3, 5, .8, .5), (4, 17, 1, .9), (5, 5, .8, .5), (6, 15, 1, .8), (7, 17, 1, .9), (8, 7, 2, 1), (10, 14, 1, .8), (11, 7, .8, .5), (12, 10, 1, .9), (13, 9, 1, .9), (14, 8, 1, .9), (15, -1, 1, .9)]
    Em9 = [64, 67, 71, 74, 78]; A13 = [61, 66, 69, 67, 71]
    bars = int(np.ceil(sec / BAR))
    for b in range(bars):
        t0 = b * BAR; last = b == bars - 1
        if not last:
            for s in range(16):
                if s in (0, 8) or (s == 10 and b % 2) or s == 14: add('dr', kick(), t0 + s * s16)
                if s in (4, 12): add('dr', snare(), t0 + s * s16)
                if s in (7, 15): add('dr', 0.3 * snare(), t0 + s * s16)  # ghost
                add('dr', hat(o=(s % 4 == 2)), t0 + s * s16 + (0.01 if s % 2 else 0))
                if s in (4, 12): add('dr', tamb(), t0 + s * s16)
            riff = riffB if b % 2 else riffA
            for s, semi, ln, acc in riff: add('bass', bass(E + semi, ln * s16 * 0.92, acc), t0 + s * s16)
            ch = A13 if b % 2 else Em9
            for s in (2, 3, 6, 10, 11, 14): add('clav', clav(ch[:3], s16 * 0.6), t0 + s * s16)
            add('str', strings(ch, BAR), t0)
            add('br', brass([c + 0 for c in ch[:4]], 1.5 * s16), t0 + 6 * s16)
            add('br', brass([c + 0 for c in ch[:4]], 2.5 * s16), t0 + 14 * s16)
        else:  # finale "ta-daaa" col basso che scende e poi tiene
            add('bass', bass(E, BAR * 0.95, 1), t0); add('dr', kick(), t0); add('dr', snare(), t0); add('dr', hat(True), t0)
            add('br', brass([64, 68, 71, 74, 76], BAR * 0.9, 1.6), t0)
            add('str', strings([64, 68, 71, 76, 80], BAR * 0.9), t0)
    mix = 0.75 * bus['dr'] + 1.35 * bus['bass'] + 2.2 * bus['clav'] + 1.3 * bus['str'] + 1.7 * bus['br']
    y = mix[:N]; y = np.tanh(1.3 * y) / np.tanh(1.3)
    y *= np.clip((sec - np.arange(N) / SR) / 0.3, 0, 1); y *= 0.9 / max(1e-6, np.abs(y).max())
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())

def build(out=OUT):
    tmp = tempfile.mkdtemp(); vid = os.path.join(tmp, 'v.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '19', vid], stdin=subprocess.PIPE)
    n = 0
    for args in PERSONAGGI:
        for f in intro(*args): p.stdin.write(f.tobytes()); n += 1
    for f in clip_frames(min(3 * BAR, 5.0)): p.stdin.write(f.tobytes()); n += 1
    p.stdin.close(); p.wait()
    if MUSICA:  # base approvata da Robi (es. /mnt/project-files/sitcom/musica/...): presa dall'inizio, sfumata in coda
        d = n / FPS; subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', MUSICA, '-t', str(d), '-af', f'afade=t=out:st={d - 0.4}:d=0.4',
                                     '-ar', '44100', '-ac', '1', os.path.join(tmp, 'm.wav')], check=True)
    else: music(n / FPS, os.path.join(tmp, 'm.wav'))
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
    if len(sys.argv) == 3 and sys.argv[1] == '--musica': MUSICA = sys.argv[2]; build()
    elif len(sys.argv) == 4 and sys.argv[1] == '--anteponi': anteponi(sys.argv[2], sys.argv[3])
    else: build()
