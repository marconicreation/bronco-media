"""Spot delle tazze (Robi 19/11/2026): Reel di ~10 s, uno per tazza, separati dalle puntate.
Uso: python3 sitcom/spot.py GEREMIA|BARTOLOMEO|BRONCO [uscita.mp4]   (senza uscita: sitcom/spot/spot_NOME.mp4)

A tempo con la canzone della sitcom (musica/canzone.py, 110 bpm, 1 battuta = 2,18 s), stacchi sempre sul primo tempo:
  battuta 1    il personaggio dice la frase della sua tazza (posa intera, mai ingrandita)
  battute 2-3  la foto della tazza sul bancone + prezzo e spedizione gratis
  battuta 4    il disegno della tazza in grande + "su Etsy, link in bio"
Le immagini si riducono e basta: niente ingrandimenti, quindi niente sgranature.
"""
import sys, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE); import lounge
sys.path.insert(0, os.path.join(HERE, 'musica')); import canzone  # dal 20/11 la canzone di Robi "Torso Stufo"

W, H, FPS = 1080, 1920, 30
BG = (38, 22, 14); CREAM = (255, 246, 228); INK = (20, 12, 8); GOLD = (255, 214, 90)
# FONT (Robi 20/11): Pricedown stile GTA ovunque parlino i personaggi. Il file NON sta nel repo (licenza): sta nei file del progetto.
_F = ['/mnt/project-files/fonts/Pricedown_Bl.otf', os.path.join(ROOT, 'fonts', 'Pricedown_Bl.otf'), os.path.join(ROOT, 'Bangers-Regular.ttf')]
FONT = next(f for f in _F if os.path.exists(f))
f_big = ImageFont.truetype(FONT, 118); f_mid = ImageFont.truetype(FONT, 76); f_bub = ImageFont.truetype(FONT, 78); f_tag = ImageFont.truetype(FONT, 50)
BAR = 240 / canzone.BPM if canzone.ATTIVA else lounge.BAR; NB = int(round(BAR * FPS))

TAZZE = {
    'GEREMIA':    dict(file='geremia_caffe', posa='geremia_strilla.jpg', frase='Non parlarmi prima del caffè!'),
    'BARTOLOMEO': dict(file='bartolomeo_sciabadu', posa='bartolomeo_sciabadu.jpg', frase="Sciabadù! Ho appena avuto un'idea."),
    'BRONCO':     dict(file='bronco_tango', posa='bronco_papillon.jpg', frase='Vai col tango!'),
}

def ease(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def quadro(im, lato, t, dur, spinta=0.05):
    """Riduce un'immagine quadrata a `lato` px con un avvicinamento leggero, solo se ci sono pixel veri in piu'."""
    s0 = im.width; s1 = max(lato, s0 * (1 - spinta)); s = s0 - (s0 - s1) * ease(t / dur); o = (s0 - s) / 2
    return im.resize((lato, lato), Image.LANCZOS, box=(o, o, o + s, o + s))
def testo(d, xy, s, font, fill=GOLD, stroke=7):
    d.text(xy, s, font=font, fill=fill, anchor='mm', stroke_width=stroke, stroke_fill='black')
def fumetto(d, text, y_punta):
    lines = []; line = ''
    for w in text.split():
        t = (line + ' ' + w).strip()
        if d.textlength(t, font=f_bub) <= 880: line = t
        else: lines.append(line); line = w
    lines.append(line)
    lh = 86; bh = len(lines) * lh + 70; bw = 980; x0 = (W - bw) // 2; y0 = y_punta - 70 - bh
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), 50, fill=CREAM, outline=INK, width=8)
    d.polygon([(W // 2 - 40, y0 + bh - 4), (W // 2 + 40, y0 + bh - 4), (W // 2 + 10, y0 + bh + 66)], fill=CREAM)
    d.line([(W // 2 - 40, y0 + bh), (W // 2 + 10, y0 + bh + 66), (W // 2 + 40, y0 + bh)], fill=INK, width=8)
    for i, ln in enumerate(lines):  # stile GTA: lettere bianche, contorno nero spesso
        d.text((W // 2, y0 + 35 + i * lh + lh // 2), ln, font=f_bub, fill=(255, 255, 255), anchor='mm', stroke_width=7, stroke_fill='black')

def frames(chi):
    z = TAZZE[chi]; nome = chi
    posa = Image.open(os.path.join(HERE, 'pose', z['posa'])).convert('RGB')                     # 1264 px
    # tazze v2 (20/11): foto 3D Blender 1600 px e disegno singolo trasparente
    foto = Image.open(os.path.join(ROOT, 'gadget', 'tazze_v2', z['file'] + '_foto.jpg')).convert('RGB')
    fw = foto.width; foto = foto.crop((int(fw * .09), int(fw * .10), int(fw * .94), int(fw * .95)))     # la tazza intera, 1360 px veri
    dis = Image.open(os.path.join(ROOT, 'gadget', 'tazze_v2', z['file'] + '_disegno.png')).convert('RGBA')
    # 1) il personaggio dice la sua frase
    for k in range(NB):
        t = k / FPS; c = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(c)
        c.paste(quadro(posa, 1080, t, BAR, 0.04), (0, 640))
        fumetto(d, z['frase'].upper(), 600)
        testo(d, (W // 2, 90), f'LA TAZZA DI {nome}', f_mid, stroke=6)
        yield c
    # 2-3) la foto della tazza vera
    for k in range(2 * NB):
        t = k / FPS; c = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(c)
        c.paste(quadro(foto, 1080, t, 2 * BAR, 0.06), (0, 330))
        testo(d, (W // 2, 170), f'LA TAZZA DI {nome}', f_big, stroke=8)
        if t > 0.3: testo(d, (W // 2, 1545), '19,90 €', f_big, CREAM, 8)
        if t > 0.9: testo(d, (W // 2, 1690), 'SPEDIZIONE GRATIS', f_mid, GOLD, 6)
        d.text((W // 2, 1840), '@marconicreation', font=f_tag, fill=(230, 200, 160), anchor='mm')
        yield c
    # 4) il disegno in grande + dove si compra
    lato = 860; sc = lato / dis.height; dz = dis.resize((int(dis.width * sc), lato), Image.LANCZOS)
    for k in range(NB):
        t = k / FPS; c = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(c)
        d.rounded_rectangle((60, 300, W - 60, 300 + lato + 80), 60, fill=(255, 255, 255), outline=GOLD, width=10)
        c.paste(dz, ((W - dz.width) // 2, 340), dz)
        testo(d, (W // 2, 170), 'SU ETSY', f_big, stroke=8)
        testo(d, (W // 2, 1400), 'LINK IN BIO', f_big, CREAM, 8)
        d.text((W // 2, 1530), 'marconicreation.vercel.app/etsy', font=f_tag, fill=CREAM, anchor='mm')
        d.text((W // 2, 1840), '@marconicreation', font=f_tag, fill=(230, 200, 160), anchor='mm')
        yield c

def build(chi, out):
    tmp = tempfile.mkdtemp(); vid = os.path.join(tmp, 'v.mp4'); wav = os.path.join(tmp, 'm.wav')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', vid], stdin=subprocess.PIPE)
    n = 0
    for f in frames(chi): p.stdin.write(f.tobytes()); n += 1
    p.stdin.close(); p.wait()
    sec = n / FPS
    if canzone.ATTIVA: subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(canzone.INIZIO), '-i', canzone.FILE, '-t', str(sec),
                                       '-af', f'afade=t=out:st={sec - 1}:d=1', '-ac', '2', '-ar', '44100', wav], check=True)
    else: lounge.music(sec, wav)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vid, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
                    '-shortest', '-movflags', '+faststart', out], check=True)
    print(out, round(n / FPS, 1), 's')

if __name__ == '__main__':
    chi = sys.argv[1].upper() if len(sys.argv) > 1 else 'GEREMIA'
    build(chi, sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'spot', f'spot_{chi.lower()}.mp4'))
