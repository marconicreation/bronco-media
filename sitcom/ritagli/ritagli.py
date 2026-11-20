"""Animazione A RITAGLI di carta (Robi 20/11/2026): il personaggio e' tagliato in pezzi
(testa, mascella, braccio, corpo) che si muovono a scatti come cartoncino ritagliato.
Stile nostro: pezzi col bordino bianco di carta e ombra, sfondo del bar fatto di carta piatta.

Uso (prova Bronco): python3 sitcom/ritagli/ritagli.py uscita.mp4
"""
import os, sys, math, random, subprocess, tempfile
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
SITCOM = os.path.dirname(HERE)
S = 1264                      # lato della posa originale: si lavora qui e si RIDUCE a 1080 (mai ingrandire)
W, H, FPS = 1080, 1920, 30
IMG_Y = 560
POSE_FPS = 12                 # i pezzi cambiano posizione 12 volte al secondo: movimento "a scatti" di carta
_F = ['/mnt/project-files/fonts/Pricedown_Bl.otf', os.path.join(SITCOM, '..', 'fonts', 'Pricedown_Bl.otf')]
FONT = next(f for f in _F if os.path.exists(f))
BG = (38, 22, 14); CREAM = (255, 246, 228); INK = (20, 12, 8); GOLD = (255, 214, 90)

# ---------------------------------------------------------------- pezzi di Bronco (coordinate sulla posa 1264)
BRONCO = {
    'posa': os.path.join(SITCOM, 'pose', 'bronco_papillon.jpg'),
    'testa': [(250, 80), (1060, 80), (1010, 560), (930, 640), (880, 690), (820, 725), (740, 748), (600, 762),
              (500, 768), (440, 752), (400, 722), (350, 690), (300, 640), (250, 560)],
    'perno_testa': (610, 760),
    'mascella': [(412, 580), (440, 562), (480, 554), (520, 557), (542, 576), (580, 587), (640, 590), (700, 580),
                 (742, 562), (772, 522), (788, 482), (802, 540), (788, 610), (748, 670), (692, 712),
                 (600, 741), (520, 739), (460, 726), (418, 702), (398, 670), (402, 630)],
    'braccio': [(398, 788), (470, 762), (542, 778), (558, 850), (532, 902), (472, 962), (412, 1032), (362, 1072),
                (288, 1064), (266, 1012), (318, 962), (328, 902), (368, 842)],
    'perno_braccio': (300, 1040),
    'occhi': [((503, 347), (54, 50)), ((716, 389), (52, 46))],
    'oggetto_x': 235,
    'pulisci': [[(270, 255), (345, 256), (395, 258), (412, 268), (428, 282), (432, 295), (420, 320), (408, 350),
                 (398, 380), (390, 400), (270, 400)]],          # a sinistra di questa x c'e' il boccale: diventa un ritaglio a parte
}

def poly_mask(pts, size=S, dil=0):
    m = Image.new('L', (size, size), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    if dil: m = m.filter(ImageFilter.MaxFilter(dil * 2 + 1))
    return m

def silhouette(img):
    from rembg import remove, new_session
    m = remove(img, session=new_session('isnet-general-use'), only_mask=True)
    a = np.array(m); a = np.where(a > 170, 255, 0).astype(np.uint8)   # via i riflessi semitrasparenti (bottiglie dietro)
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    return Image.fromarray(a)

def carta(piece, bordo=8, forma=None, togli=None):
    """Bordino bianco di carta ritagliata attorno al pezzo.
    forma = sagoma su cui calcolare il bordo (es. testa+mascella, cosi' niente righe bianche dentro la bocca);
    togli = zona dove il bordo NON va (dove il pezzo tocca un altro pezzo)."""
    a = forma if forma is not None else piece.getchannel('A')
    big = a.filter(ImageFilter.MaxFilter(bordo * 2 + 1))
    if forma is not None: big = ImageChops.subtract(big, forma)
    if togli is not None: big = ImageChops.subtract(big, togli.filter(ImageFilter.MaxFilter(bordo * 2 + 3)))
    big = ImageChops.lighter(big, piece.getchannel('A')).filter(ImageFilter.GaussianBlur(1.2))
    out = Image.new('RGBA', piece.size, (250, 247, 238, 0)); out.putalpha(big)
    out.alpha_composite(piece); return out

def ombra(piece, off=(10, 12), forza=110):
    a = piece.getchannel('A').filter(ImageFilter.GaussianBlur(7)).point(lambda v: v * forza // 255)
    sh = Image.new('RGBA', piece.size, (0, 0, 0, 0)); sh.putalpha(a)
    out = Image.new('RGBA', piece.size, (0, 0, 0, 0)); out.alpha_composite(sh, off); return out

def tagli(cfg):
    img = Image.open(cfg['posa']).convert('RGB'); assert img.size == (S, S)
    sil = np.array(silhouette(img))
    xo = cfg['oggetto_x']
    for pts in cfg.get('pulisci', []):   # pezzi di bottiglia dietro il personaggio rimasti attaccati alla sagoma
        sil[np.array(poly_mask(pts)) > 0] = 0
    obj = sil.copy(); obj[:, xo:] = 0
    sil[:, :xo] = 0
    m_testa = np.array(poly_mask(cfg['testa'])) & sil
    m_masc = np.array(poly_mask(cfg['mascella'])) & sil
    m_bra = np.array(poly_mask(cfg['braccio'])) & sil
    m_testa = m_testa & ~m_masc
    # corpo: la sagoma senza testa; dove ci sono braccio/mascella/collo il colore viene "ricostruito" (inpaint),
    # cosi' quando i pezzi si muovono sotto si vede camicia e papillon, non un buco
    low = np.zeros_like(sil); low[680:800, :] = 255
    m_tp = np.array(poly_mask(cfg['testa']))
    rif = np.array(poly_mask(cfg['braccio'], dil=10)) | np.array(poly_mask(cfg['mascella'], dil=10)) | (m_tp & low)
    arr = np.array(img)[:, :, ::-1].copy()
    fill = cv2.inpaint(arr, ((rif & sil) > 0).astype(np.uint8) * 255, 18, cv2.INPAINT_TELEA)[:, :, ::-1]
    body_a = sil & ~m_tp
    def rgba(rgb, a):
        p = Image.fromarray(np.array(rgb)).convert('RGBA'); p.putalpha(Image.fromarray(a.astype(np.uint8))); return p
    return {
        'corpo': rgba(fill, body_a),
        'testa': rgba(img, m_testa),
        'mascella': rgba(img, m_masc),
        'braccio': rgba(img, m_bra),
        'oggetto': rgba(img, obj),
        'img': img,
    }

def occhi_chiusi(testa, occhi, quale=(0, 1)):
    t = testa.copy(); d = ImageDraw.Draw(t); src = testa.convert('RGB')
    for i in quale:
        (cx, cy), (rx, ry) = occhi[i]
        col = src.getpixel((cx, cy - ry - 14))
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=col + (255,))
        d.arc((cx - rx + 6, cy - ry * 0.6, cx + rx - 6, cy + ry * 0.9), 15, 165, fill=INK + (255,), width=9)
    return t

# ---------------------------------------------------------------- sfondo del bar in carta
def sfondo_bar(seed=3):
    rnd = random.Random(seed)
    bg = Image.new('RGBA', (S, S), (86, 48, 32, 255)); d = ImageDraw.Draw(bg)
    for x in range(0, S, 158):  # pannelli di legno della parete
        d.rectangle((x + 10, 0, x + 148, S), fill=(98, 56, 36, 255))
    lay = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    def pezzo(draw_fn):
        p = Image.new('RGBA', (S, S), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(p))
        p = carta(p, 5); lay.alpha_composite(ombra(p, (6, 8), 90)); lay.alpha_composite(p)
    colori = [(46, 120, 62), (176, 106, 34), (150, 40, 34), (60, 90, 140), (196, 160, 60), (110, 60, 120)]
    for sy in (430, 790):
        pezzo(lambda d, sy=sy: d.rectangle((0, sy, S, sy + 34), fill=(140, 82, 44)))
        x = 20
        while x < S - 60:
            w = rnd.randint(54, 86); h = rnd.randint(170, 250); c = rnd.choice(colori)
            def bott(d, x=x, w=w, h=h, c=c, sy=sy):
                d.rounded_rectangle((x, sy - h, x + w, sy), 14, fill=c)
                nw = w // 3; d.rectangle((x + w // 2 - nw // 2, sy - h - 70, x + w // 2 + nw // 2, sy - h + 4), fill=c)
                d.rectangle((x + 8, sy - h * 0.6, x + w - 8, sy - h * 0.3), fill=(236, 222, 190))
            pezzo(bott); x += w + rnd.randint(14, 40)
    pezzo(lambda d: (d.ellipse((1080, 60, 1220, 200), fill=(255, 210, 110)), d.rectangle((1145, 0, 1155, 70), fill=(60, 40, 30))))
    bg.alpha_composite(lay)
    # bancone davanti
    ban = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(ban)
    d.rectangle((0, 1112, S, S), fill=(128, 70, 34)); d.rectangle((0, 1112, S, 1140), fill=(176, 104, 52))
    for y in (1170, 1210, 1240): d.line((0, y, S, y + 6), fill=(110, 58, 28), width=4)
    ban = carta(ban, 6)
    return bg, ban

def grana(seed=7):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 7, (W, W)).astype(np.float32)
    n = cv2.GaussianBlur(n, (0, 0), 1.1)
    return n

# ---------------------------------------------------------------- fumetto Pricedown (bianco, contorno nero spesso)
def wrap(d, text, font, maxw):
    out, line = [], ''
    for w in text.split():
        t = (line + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw: line = t
        else: out.append(line); line = w
    out.append(line); return out

f_bub = ImageFont.truetype(FONT, 74); f_tag = ImageFont.truetype(FONT, 50)
def fumetto(c, testo):
    d = ImageDraw.Draw(c); lines = wrap(d, testo, f_bub, 840)
    lh = 84; bh = len(lines) * lh + 80; bw = 960; cx = W // 2; y0 = 130 + (400 - bh) // 2
    d.rounded_rectangle((cx - bw // 2, y0, cx + bw // 2, y0 + bh), 50, fill=CREAM, outline=INK, width=8)
    d.polygon([(cx - 40, y0 + bh - 4), (cx + 40, y0 + bh - 4), (cx + 10, y0 + bh + 70)], fill=CREAM)
    d.line([(cx - 40, y0 + bh), (cx + 10, y0 + bh + 70), (cx + 40, y0 + bh)], fill=INK, width=8)
    for i, ln in enumerate(lines):
        d.text((cx, y0 + 40 + i * lh + lh // 2), ln, font=f_bub, fill='white', anchor='mm', stroke_width=7, stroke_fill=INK)

# ---------------------------------------------------------------- movimento
def trasforma(p, ang, perno, dx=0, dy=0):
    if not ang and not dx and not dy: return p
    return p.rotate(ang, resample=Image.BICUBIC, center=perno, translate=(dx, dy))

def render(cfg, copione, out_mp4, testata='AL BANCONE DI BRONCO · PROVA A RITAGLI'):
    P = tagli(cfg)
    bg, ban = sfondo_bar()
    corpo = carta(P['corpo']); ogg = carta(P['oggetto'])
    tm = ImageChops.lighter(P['testa'].getchannel('A'), P['mascella'].getchannel('A'))
    mA = P['mascella'].getchannel('A'); tA = P['testa'].getchannel('A')
    ct = lambda p: carta(p, forma=tm, togli=ImageChops.subtract(mA, tA.filter(ImageFilter.MaxFilter(25))))
    testa_ap = ct(P['testa']); testa_ch = ct(occhi_chiusi(P['testa'], cfg['occhi']))
    testa_occhiolino = ct(occhi_chiusi(P['testa'], cfg['occhi'], (1,)))
    masc = carta(P['mascella'], togli=tA); bra = carta(P['braccio'])
    # prolunga del mento: copie della mascella spostate in giu', disegnate DIETRO il corpo,
    # cosi' quando la bocca si chiude (mascella su) sotto il mento non resta un buco
    pro = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    for dy in (40, 26, 13): pro.alpha_composite(masc, (0, dy))
    sh = {k: ombra(v) for k, v in dict(corpo=corpo, testa=testa_ap, masc=masc, bra=bra, ogg=ogg).items()}
    gr = grana()
    BAR = 240 / 110
    tot = sum(s['battute'] for s in copione) * BAR
    nfr = int(round(tot * FPS))
    tmp = tempfile.mkdtemp()
    rnd = random.Random(11)
    # posizioni dei pezzi calcolate 12 volte al secondo (a scatti)
    cache = {}; ultimo = [None, None]
    t0s = []; acc = 0
    for s in copione: t0s.append(acc); acc += s['battute'] * BAR
    for k in range(nfr):
        t = k / FPS
        si = max(i for i, a in enumerate(t0s) if a <= t + 1e-9); s = copione[si]; ts = t - t0s[si]
        q = int(t * POSE_FPS)
        if q not in cache:
            r = random.Random(q * 7 + 3)
            parla = s.get('testo') and ts < s['battute'] * BAR - 0.5 and ts > 0.15
            masc_dy = -r.choice([0, 18, 34, 34]) if parla else -34    # bocca: chiusa = mascella su
            if parla and q % 2 == 0: masc_dy = 0
            ang_t = 2.6 * math.sin(t * 2.9) + (r.uniform(-0.8, 0.8) if parla else 0)
            dy_t = int(5 * math.sin(t * 5.8)) if parla else 0
            ang_b = 0
            if s.get('azione') == 'papillon':
                ang_b = [0, -7, -7, 0, -7, -7, 0, 0][int(ts * 4) % 8]
                ang_t = -4 if ts > 0.4 else ang_t
            ang_t = round(ang_t * 2) / 2
            occhi = 'ap'
            if (t % 2.7) < 0.17: occhi = 'ch'
            if s.get('azione') == 'papillon' and 1.0 < ts < 1.9: occhi = 'occhiolino'
            cache = {q: (masc_dy, ang_t, dy_t, ang_b, occhi)}
        masc_dy, ang_t, dy_t, ang_b, occhi = cache[q]
        if (q, si) == ultimo[0]:
            ultimo[1].save(os.path.join(tmp, f'{k:05d}.jpg'), quality=92); continue
        fr = bg.copy()
        tv = dict(ap=testa_ap, ch=testa_ch, occhiolino=testa_occhiolino)[occhi]
        pt = cfg['perno_testa']; pb = cfg['perno_braccio']
        fr.alpha_composite(ban)
        L = [
            (sh['ogg'], ogg, 0, (0, 0), 0, 0),
            (None, pro, ang_t, pt, 0, dy_t + masc_dy),
            (sh['corpo'], corpo, 0, (0, 0), 0, 0),
            (sh['masc'], masc, ang_t, pt, 0, dy_t + masc_dy),
            (sh['testa'], tv, ang_t, pt, 0, dy_t),
            (sh['bra'], bra, ang_b, pb, 0, 0),
        ]
        for shadow, piece, a, pv, dx, dy in L:
            if shadow is not None: fr.alpha_composite(trasforma(shadow, a, pv, dx, dy))
            fr.alpha_composite(trasforma(piece, a, pv, dx, dy))
        # bancone davanti al corpo solo in basso (le zampe restano sopra: il corpo e' gia' tagliato al bancone)
        sq = fr.convert('RGB').resize((W, W), Image.LANCZOS)
        a = np.array(sq).astype(np.float32) + gr[:, :, None]
        sq = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        c = Image.new('RGB', (W, H), BG); c.paste(sq, (0, IMG_Y))
        d = ImageDraw.Draw(c)
        d.text((W // 2, 62), testata, font=f_tag, fill=GOLD, anchor='mm', stroke_width=3, stroke_fill='black')
        if s.get('testo'): fumetto(c, s['testo'])
        d.text((W // 2, 1790), '@marconicreation', font=f_tag, fill=(230, 200, 160), anchor='mm')
        c.save(os.path.join(tmp, f'{k:05d}.jpg'), quality=92); ultimo[:] = [(q, si), c]
    sys.path.insert(0, os.path.join(SITCOM, 'musica')); import canzone
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(tmp, '%05d.jpg')]
    if canzone.ATTIVA:
        cmd += ['-ss', str(canzone.INIZIO), '-i', canzone.FILE, '-map', '0:v', '-map', '1:a', '-t', f'{tot:.3f}',
                '-af', f'afade=t=out:st={tot - 1.2:.2f}:d=1.2', '-c:a', 'aac', '-b:a', '160k']
    cmd += ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', out_mp4]
    subprocess.run(cmd, check=True)
    return out_mp4

PROVA = [
    {'testo': 'Cocktail nuovo: si chiama Bolletta.', 'battute': 2},
    {'testo': 'Ti lascia senza parole. E senza portafoglio.', 'battute': 2},
    {'azione': 'papillon', 'battute': 1},
    {'testo': 'Vai col tango!', 'battute': 1},
]

if __name__ == '__main__':
    print(render(BRONCO, PROVA, sys.argv[1] if len(sys.argv) > 1 else 'prova_ritagli_bronco.mp4'))
