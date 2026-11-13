"""Monta un episodio di "Al bancone di Bronco" come Reel verticale 1080x1920.
Uso: python3 sitcom.py episodio.json uscita.mp4
episodio.json: {"titolo": "...", "numero": 1, "cta": "...",
                "scene": [{"img": "percorso", "chi": "GEREMIA", "testo": "...", "durata": 4.0}, ...]}
Il fumetto sta SEMPRE sopra l'immagine (mai su muso o occhi), con la punta verso il personaggio.
Musica: motivetto swing sintetizzato qui (nessun diritto)."""
import sys, json, subprocess, math, wave, os, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
_F = [os.path.join(HERE, '..', 'Bangers-Regular.ttf'), '/home/user/bronco-media/Bangers-Regular.ttf']
FONT = next(f for f in _F if os.path.exists(f))
W, H, FPS = 1080, 1920, 30
BG = (38, 22, 14); CREAM = (255, 246, 228); INK = (20, 12, 8); GOLD = (255, 214, 90)
IMG_Y, IMG_S = 560, 1080
FINALE_IMG = os.path.join(HERE, 'pose', 'bronco_finale_tango.jpg')

ep = json.load(open(sys.argv[1])); OUT = sys.argv[2]
if ep.get('finale', True):
    ep['scene'].append({'img': ep.get('finale_img', FINALE_IMG), 'chi': 'BRONCO', 'testo': 'Vai col tango!', 'durata': 2.6})
# voci dei personaggi (Robi 13/11): una per battuta, la scena dura almeno quanto la voce
VOCI = []
if ep.get('voci', True):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'voci'))
    import voci as _voci
    _vt = tempfile.mkdtemp()
    for i, sc in enumerate(ep['scene']):
        if sc.get('chi') and sc.get('testo'):
            w = _voci.voce(sc['chi'], sc['testo'], os.path.join(_vt, f'v{i}.wav'))
            if w:
                with wave.open(w) as f: L = f.getnframes() / f.getframerate()
                sc['durata'] = max(sc.get('durata', 3.5), L + 0.7); sc['_voce'] = w
f_big = ImageFont.truetype(FONT, 110); f_mid = ImageFont.truetype(FONT, 72)
f_bub = ImageFont.truetype(FONT, 64); f_tag = ImageFont.truetype(FONT, 50)

def ease(t): return t * t * (3 - 2 * t)
_IMC = {}
def square(path, box=None, flip=False):
    """box = [x0, y0, x1, y1] in frazioni dell'immagine (inquadratura stretta); flip = specchiata."""
    k = (path, tuple(box) if box else None, flip)
    if k in _IMC: return _IMC[k]
    im = Image.open(os.path.join(HERE, path)).convert('RGB'); w, h = im.size
    if box:
        x0, y0, x1, y1 = box[0] * w, box[1] * h, box[2] * w, box[3] * h
        s = max(x1 - x0, y1 - y0); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        x0 = min(max(0, cx - s / 2), w - s); y0 = min(max(0, cy - s / 2), h - s)
        im = im.crop((int(x0), int(y0), int(x0 + s), int(y0 + s)))
    else:
        s = min(w, h); im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    im = im.resize((IMG_S, IMG_S), Image.LANCZOS)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    _IMC[k] = im; return im

def wrap(d, text, font, maxw):
    out = []
    for para in text.split('\n'):
        line = ''
        for w in para.split():
            t = (line + ' ' + w).strip()
            if d.textlength(t, font=font) <= maxw: line = t
            else: out.append(line); line = w
        out.append(line)
    return out

def bubble(c, d, chi, text, shown, pop):
    lines = wrap(d, text, f_bub, 860)
    lh = 72; bh = len(lines) * lh + 70; bw = 960
    x0 = (W - bw) // 2; y0 = 120 + (420 - bh) // 2
    sc = 0.85 + 0.15 * ease(min(1, pop))
    cx, cy = W // 2, y0 + bh // 2
    bx0, by0 = cx - bw * sc / 2, cy - bh * sc / 2
    d.rounded_rectangle((bx0, by0, bx0 + bw * sc, by0 + bh * sc), 50, fill=CREAM, outline=INK, width=8)
    d.polygon([(cx - 40, by0 + bh * sc - 4), (cx + 40, by0 + bh * sc - 4), (cx + 10, by0 + bh * sc + 70)], fill=CREAM)
    d.line([(cx - 40, by0 + bh * sc), (cx + 10, by0 + bh * sc + 70), (cx + 40, by0 + bh * sc)], fill=INK, width=8)
    if pop >= 1:
        left = shown
        for i, ln in enumerate(lines):
            part = ln[:max(0, left)]; left -= len(ln) + 1
            d.text((cx, y0 + 35 + i * lh + lh // 2), part, font=f_bub, fill=INK, anchor='mm')
    if chi and ep.get('nomi', False):  # Robi 13/11: niente nomi nei fumetti
        tw = d.textlength(chi, font=f_tag) + 40
        d.rounded_rectangle((x0 + 30, y0 - 34, x0 + 30 + tw, y0 + 30), 16, fill=(194, 50, 31), outline=INK, width=5)
        d.text((x0 + 30 + tw / 2, y0 - 2), chi, font=f_tag, fill='white', anchor='mm')

def base(img, t, dur):
    z = 1.0 + 0.06 * ease(min(1, t / dur)); s = int(IMG_S * z)
    big = img.resize((s, s), Image.LANCZOS); o = (s - IMG_S) // 2
    c = Image.new('RGB', (W, H), BG); c.paste(big.crop((o, o, o + IMG_S, o + IMG_S)), (0, IMG_Y))
    d = ImageDraw.Draw(c)
    d.text((W // 2, 1790), '@marconicreation', font=f_tag, fill=(230, 200, 160), anchor='mm')
    return c, d

frames_written = 0
def card(lines, dur, sub=None):
    n = int(dur * FPS)
    for k in range(n):
        t = k / FPS; c = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(c)
        dy = int((1 - ease(min(1, t / 0.4))) * -250)
        d.multiline_text((W // 2, 820 + dy), '\n'.join(lines), font=f_big, fill=GOLD, anchor='mm', align='center', stroke_width=8, stroke_fill='black', spacing=14)
        if sub: d.multiline_text((W // 2, 1250), sub, font=f_mid, fill=CREAM, anchor='mm', align='center', spacing=12)
        d.text((W // 2, 1790), '@marconicreation', font=f_tag, fill=(230, 200, 160), anchor='mm')
        yield c

def scene(s):
    # "inq": piu' inquadrature nella stessa scena (Robi 13/11: scenette con piu' fotogrammi).
    # ogni inquadratura: {"img": opz., "box": [x0,y0,x1,y1] opz., "flip": opz., "peso": opz.}
    dur = s.get('durata', 3.5); n = int(dur * FPS)
    inq = s.get('inq') or [{}]
    pesi = [q.get('peso', 1) for q in inq]; tot = sum(pesi)
    tagli = []; acc = 0
    for q, pw in zip(inq, pesi):
        a = int(n * acc / tot); acc += pw; tagli.append((a, int(n * acc / tot), q))
    chars = len(s.get('testo', ''))
    for k in range(n):
        for a, b, q in tagli:
            if a <= k < b or (k >= b and (a, b, q) == tagli[-1]): break
        img = square(q.get('img', s['img']), q.get('box'), q.get('flip', False))
        t = k / FPS; c, d = base(img, (k - a) / FPS, max(0.5, (b - a) / FPS))
        if s.get('testo'):
            pop = t / 0.25; shown = int(max(0, t - 0.25) * 32)
            if not ep.get('scrittura', False): pop, shown = 1, chars  # Robi 13/11: fumetto statico, testo intero subito
            bubble(c, d, s.get('chi', ''), s['testo'], min(shown, chars), pop)
        yield c

def all_frames():
    yield from card(['AL BANCONE', 'DI BRONCO'], 2.2, f"Episodio {ep['numero']}\n{ep['titolo']}")
    t = 2.2
    for s in ep['scene']:
        if s.get('_voce'): VOCI.append((t + 0.3, s['_voce']))
        yield from scene(s); t += int(s.get('durata', 3.5) * FPS) / FPS
    # (la chiusura fissa con "Vai col tango!" di Bronco in primo piano e' aggiunta alle scene all'avvio)
    yield from card(ep.get('cta_titolo', ['IL COCKTAIL', 'COL TUO NOME']), 3.0, ep.get('cta', 'Regalo di Natale a 5 €\nlink in bio'))

# --- musica: la stessa della sigla (funk anni '70, approvata da Robi il 13/11), da sigla/sigla.py ---
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sigla'))
import sigla as _sigla
def music(sec, path): _sigla.music(sec, path)

tmp = tempfile.mkdtemp(); vid = os.path.join(tmp, 'v.mp4')
p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', vid], stdin=subprocess.PIPE)
n = 0
for f in all_frames(): p.stdin.write(f.tobytes()); n += 1
p.stdin.close(); p.wait()
music(n / FPS, os.path.join(tmp, 'm.wav'))
if VOCI:
    with wave.open(os.path.join(tmp, 'm.wav')) as f:
        sr = f.getframerate(); ch = f.getnchannels(); m = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(float) / 32768
    m = m.reshape(-1, ch).mean(1); v = np.zeros_like(m)
    for st, w in VOCI:
        with wave.open(w) as f: x = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(float) / 32768
        i = int(st * sr); k = min(len(x), len(v) - i)
        if k > 0: v[i:i + k] += x[:k]
    env = np.convolve(np.abs(v) > 0.01, np.ones(int(0.25 * sr)) / int(0.25 * sr), 'same')
    duck = 1 - 0.65 * np.clip(env * 3, 0, 1)
    y = np.tanh(m * duck * 0.9 + v * 1.0)
    with wave.open(os.path.join(tmp, 'm.wav'), 'w') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr); f.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vid, '-i', os.path.join(tmp, 'm.wav'), '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
                '-shortest', '-movflags', '+faststart', OUT], check=True)
print(OUT, round(n / FPS, 1), 's')
