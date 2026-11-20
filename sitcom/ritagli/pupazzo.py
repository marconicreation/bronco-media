"""Pupazzo di carta (Robi 20/11/2026, proposta A): personaggio ridisegnato dall'IA immagini di ElevenLabs
in pezzi separati (testa con 4 espressioni, torso, braccia), montato e animato qui sullo sfondo del bar di carta.
La bocca segue la voce ElevenLabs (volume della voce fotogramma per fotogramma).

Uso (prova Bronco): python3 sitcom/ritagli/pupazzo.py uscita.mp4
Cartella del personaggio: testa0 (bocca chiusa), testa1 (parla), testa2 (bocca spalancata), testa3 (occhi chiusi),
torso, braccio_sx, braccio_dx (PNG trasparenti).
"""
import os, sys, math, random, subprocess, tempfile, wave
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ritagli as R          # sfondo del bar di carta, fumetto Pricedown, ombre

S, W, H, FPS, IMG_Y = R.S, R.W, R.H, R.FPS, R.IMG_Y
POSE_FPS = 12

# configurazione dei pupazzi: zone di bocca/occhi (frazioni della testa) per trapiantare le espressioni
PERSONAGGI = {
    'BRONCO': dict(cartella='bronco', scala=0.95, bocca=(0.22, 0.50, 0.78, 0.90), occhi=(0.12, 0.18, 0.88, 0.50), collo=60),
    'GEREMIA': dict(cartella='geremia', scala=0.95, bocca=(0.22, 0.55, 0.78, 0.98), occhi=(0.15, 0.18, 0.85, 0.55), collo=50),
    'BARTOLOMEO': dict(cartella='bartolomeo', scala=0.85, bocca=(0.00, 0.50, 0.55, 0.95), occhi=(0.20, 0.22, 0.75, 0.58), collo=90),
}

# stessi personaggi in versione plastilina (pezzi in plastilina/<nome>/, estratti con estrai_plastilina.py)
PERSONAGGI_PLASTILINA = {
    'BRONCO': dict(cartella='plastilina/bronco', sfondo='plastilina', scala=0.92, bocca=(0.22, 0.52, 0.78, 0.92), occhi=(0.12, 0.18, 0.88, 0.50), collo=50),
    'GEREMIA': dict(cartella='plastilina/geremia', sfondo='plastilina', scala=1.10, gesti=0.6, bocca=(0.25, 0.58, 0.75, 0.97), occhi=(0.20, 0.22, 0.80, 0.52), collo=40),
    'BARTOLOMEO': dict(cartella='plastilina/bartolomeo', sfondo='plastilina', scala=1.08, bocca=(0.00, 0.52, 0.58, 0.88), occhi=(0.18, 0.24, 0.75, 0.50), collo=110),
}

def carica(cartella, scala, BOCCA=(0.22, 0.50, 0.78, 0.90), OCCHI=(0.12, 0.18, 0.88, 0.50)):
    if not os.path.isabs(cartella): cartella = os.path.join(HERE, cartella)
    def ld(n):
        im = Image.open(os.path.join(cartella, n + '.png')).convert('RGBA')
        return im.resize((round(im.width * scala), round(im.height * scala)), Image.LANCZOS)
    teste = [ld(f'testa{i}') for i in range(4)]
    base = teste[0]
    # le espressioni vengono "trapiantate" sulla testa base (allineate), cosi' la testa non cambia forma
    def allinea(src):
        g0 = cv2.cvtColor(np.array(base.convert('RGB')), cv2.COLOR_RGB2GRAY).astype(np.float32)
        s = src.resize(base.size, Image.LANCZOS)
        g1 = cv2.cvtColor(np.array(s.convert('RGB')), cv2.COLOR_RGB2GRAY).astype(np.float32)
        M = np.eye(2, 3, dtype=np.float32)
        try:
            cv2.findTransformECC(g0, g1, M, cv2.MOTION_AFFINE, (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-5), None, 5)
        except cv2.error:
            pass
        a = cv2.warpAffine(np.array(s), M, base.size, flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
        return Image.fromarray(a)
    def trapianta(src, box):
        w, h = base.size; x0, y0, x1, y1 = [int(v) for v in (box[0] * w, box[1] * h, box[2] * w, box[3] * h)]
        m = Image.new('L', base.size, 0); ImageDraw.Draw(m).ellipse((x0, y0, x1, y1), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(10))
        out = base.copy(); al = allinea(src)
        out.paste(al.convert('RGB'), (0, 0), m)
        out.putalpha(base.getchannel('A'))
        return out
    return {
        'chiusa': base,
        'parla': trapianta(teste[1], BOCCA),
        'aperta': trapianta(teste[2], BOCCA),
        'blink': trapianta(teste[3], OCCHI),
        'torso': ld('torso'), 'bsx': ld('braccio_sx'), 'bdx': ld('braccio_dx'),
    }

def volume_voce(mp3, n, ritardo):
    wav = tempfile.mktemp(suffix='.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp3, '-ac', '1', '-ar', '16000', wav], check=True)
    with wave.open(wav) as f: x = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768
    hop = 16000 // FPS; v = np.zeros(n)
    for k in range(n):
        i = int((k / FPS - ritardo) * 16000)
        if 0 <= i < len(x): v[k] = np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-9)
    return v / (np.percentile(v[v > 0], 95) if (v > 0).any() else 1)

def ruota(p, ang, perno_loc, dest):
    """Ruota il pezzo attorno al suo perno (coordinate nel pezzo) e lo mette con il perno su dest. Restituisce (img, xy)."""
    pad = int(math.hypot(*p.size)) + 4
    c = Image.new('RGBA', (pad * 2, pad * 2), (0, 0, 0, 0)); c.paste(p, (pad - perno_loc[0], pad - perno_loc[1]))
    c = c.rotate(ang, resample=Image.BICUBIC, center=(pad, pad))
    return c, (int(dest[0] - pad), int(dest[1] - pad))

def metti(fr, p, xy, ombra=True):
    if ombra:
        a = p.getchannel('A').filter(ImageFilter.GaussianBlur(6)).point(lambda v: v * 100 // 255)
        sh = Image.new('RGBA', p.size, (0, 0, 0, 0)); sh.putalpha(a)
        fr.alpha_composite(sh, (xy[0] + 9, xy[1] + 11)) if xy[0] + 9 >= 0 and xy[1] + 11 >= 0 else _incolla(fr, sh, (xy[0] + 9, xy[1] + 11))
    _incolla(fr, p, xy)

def _incolla(fr, p, xy):
    x, y = xy; cx0, cy0 = max(0, -x), max(0, -y)
    if cx0 or cy0: p = p.crop((cx0, cy0, p.width, p.height)); x += cx0; y += cy0
    if x < fr.width and y < fr.height: fr.alpha_composite(p, (x, y))

def finta_voce(n, finestre, seed=5):
    """Senza voce: la bocca si muove a scatti nelle finestre (inizio, fine) in secondi."""
    r = random.Random(seed); v = np.zeros(n); k = 0
    while k < n:
        t = k / FPS; dentro = any(a <= t < b for a, b in finestre)
        val = r.choice([0.0, 0.3, 0.3, 0.8, 0.5]) if dentro else 0.0
        L = r.randint(3, 5); v[k:k + L] = val; k += L
    return v

BANCONE_PLASTILINA = 1080   # riga (su S) del bordo alto del bancone nel bar di plastilina

def sfondo_plastilina():
    """Bar di plastilina (plastilina/bar_full.png, quadrato centrale) -> (sfondo, bancone davanti)."""
    im = Image.open(os.path.join(HERE, 'plastilina', 'bar_full.png')).convert('RGBA'); w, h = im.size
    bg = im.crop(((w - h) // 2, 0, (w + h) // 2, h)).resize((S, S), Image.LANCZOS)
    ban = bg.copy(); a = Image.new('L', (S, S), 0); ImageDraw.Draw(a).rectangle((0, BANCONE_PLASTILINA, S, S), fill=255)
    ban.putalpha(a)
    return bg, ban

def scena_frames(cfg, dur, testo, vol, tmp, k0, testata, tango=False, cache=None):
    """Disegna una inquadratura (un personaggio) lunga dur secondi; vol = volume voce per fotogramma (0..1)."""
    P = cache.get(id(cfg)) if cache is not None else None
    if P is None:
        P = carica(cfg['cartella'], cfg['scala'], cfg['bocca'], cfg['occhi'])
        if cache is not None: cache[id(cfg)] = P
    plast = cfg.get('sfondo') == 'plastilina'
    bg, ban = sfondo_plastilina() if plast else R.sfondo_bar(); gr = R.grana() * (0.3 if plast else 1.0)
    T = P['torso']; tw, th = T.size
    tx, ty = S // 2 - tw // 2, (BANCONE_PLASTILINA + 60 if plast else 1172) - th
    hw, hh = P['chiusa'].size
    collo = (S // 2, ty + 70)
    sp_sx, sp_dx = (tx + 70, ty + 80), (tx + tw - 70, ty + 80)
    n = int(round(dur * FPS)); stato = None; ultimo = None; bocca = 'chiusa'; tenuta = 0
    for k in range(n):
        t = k / FPS; q = int(t * POSE_FPS); v = vol[k] if k < len(vol) else 0
        nuova = 'aperta' if v > 0.62 else 'parla' if v > 0.16 else 'chiusa'
        if tenuta <= 0: bocca, tenuta = nuova, 2
        tenuta -= 1
        parla = vol[max(0, k - 6):k + 6].max() > 0.16 if len(vol) else False
        if q != (stato or (None,))[0]:
            r = random.Random(q + k0)
            ang_t = round((2.5 * math.sin(t * 2.6) + (r.uniform(-1.5, 1.5) if parla else 0)) * 2) / 2
            dy_t = int(-6 * abs(math.sin(t * 6.0))) if parla else 0
            if tango: ang_d = 150 if t > 0.15 else 80
            elif parla: ang_d = [round(a * cfg.get('gesti', 1.0)) for a in (48, 70, 58, 78)][(q // 3) % 4]
            else: ang_d = 30
            ang_s = -28 + (-14 if parla and (q // 5) % 2 else 0)
            occhi = ((t + k0 / FPS) % 2.9) < 0.17 and not parla
            stato = (q, ang_t, dy_t, ang_d, ang_s, occhi)
        _, ang_t, dy_t, ang_d, ang_s, occhi = stato
        faccia = 'blink' if occhi else bocca
        chiave = (faccia, ang_t, dy_t, ang_d, ang_s)
        if ultimo and chiave == ultimo[0]:
            ultimo[1].save(os.path.join(tmp, f'{k0 + k:05d}.jpg'), quality=92); continue
        fr = bg.copy()
        if not plast: fr.alpha_composite(ban)
        bs, xy = ruota(P['bsx'], ang_s, (P['bsx'].width // 2, 30), sp_sx); metti(fr, bs, xy)
        bd, xy = ruota(P['bdx'], ang_d, (P['bdx'].width // 2, 30), sp_dx); metti(fr, bd, xy)
        metti(fr, T, (tx, ty + dy_t // 3))
        hd, xy = ruota(P[faccia], ang_t, (hw // 2, hh - cfg['collo']), (collo[0], collo[1] + dy_t)); metti(fr, hd, xy)
        if plast: fr.alpha_composite(ban)
        else: fr.alpha_composite(ban.crop((0, 1112, S, S)), (0, 1112))
        sq = fr.convert('RGB').resize((W, W), Image.LANCZOS)
        a = np.array(sq).astype(np.float32) + gr[:, :, None]
        sq = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        c = Image.new('RGB', (W, H), R.BG); c.paste(sq, (0, IMG_Y)); d = ImageDraw.Draw(c)
        d.text((W // 2, 62), testata, font=R.f_tag, fill=R.GOLD, anchor='mm', stroke_width=3, stroke_fill='black')
        if testo: R.fumetto(c, testo)
        d.text((W // 2, 1790), '@marconicreation', font=R.f_tag, fill=(230, 200, 160), anchor='mm')
        c.save(os.path.join(tmp, f'{k0 + k:05d}.jpg'), quality=92); ultimo = (chiave, c)
    return n

def render(scene, out_mp4, testata='AL BANCONE DI BRONCO', voce=None, ritardo=0.3):
    """scene: lista di {chi, testo, battute, tango?, parla: [(da, a)] secondi dentro la scena (senza voce)}."""
    BAR = 240 / 110; tmp = tempfile.mkdtemp(); k0 = 0; cache = {}
    tot = sum(s['battute'] for s in scene) * BAR; ntot = int(round(tot * FPS))
    vol_all = volume_voce(voce, ntot, ritardo) if voce else None
    for s in scene:
        n = int(round((k0 / FPS + s['battute'] * BAR) * FPS)) - k0
        if vol_all is not None: vol = vol_all[k0:k0 + n]
        else: vol = finta_voce(n, s.get('parla', [(0.2, s['battute'] * BAR - 0.6)] if s.get('testo') else []), seed=k0)
        scena_frames(PERSONAGGI[s['chi']], n / FPS, s.get('testo'), vol, tmp, k0, testata, s.get('tango', False), cache)
        k0 += n
    sys.path.insert(0, os.path.join(R.SITCOM, 'musica')); import canzone
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(tmp, '%05d.jpg')]
    if voce and canzone.ATTIVA:
        cmd += ['-i', voce, '-ss', str(canzone.INIZIO), '-i', canzone.FILE, '-filter_complex',
                f'[1:a]aformat=channel_layouts=stereo:sample_rates=44100,adelay={int(ritardo * 1000)}|{int(ritardo * 1000)},volume=1.6,asplit[v1][v2];'
                f'[2:a]aformat=channel_layouts=stereo:sample_rates=44100,volume=0.35[m];'
                f'[m][v1]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=300[md];[md][v2]amix=inputs=2:normalize=0,'
                f'afade=t=out:st={tot - 1.2:.2f}:d=1.2[a]', '-map', '0:v', '-map', '[a]']
    elif canzone.ATTIVA:
        cmd += ['-ss', str(canzone.INIZIO), '-i', canzone.FILE, '-map', '0:v', '-map', '1:a',
                '-af', f'afade=t=out:st={tot - 1.2:.2f}:d=1.2']
    cmd += ['-t', f'{tot:.3f}', '-c:a', 'aac', '-b:a', '160k', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', out_mp4]
    subprocess.run(cmd, check=True)
    return out_mp4

PROVA_TRIO = [
    {'chi': 'GEREMIA', 'testo': 'Un cocktail che si chiama Bolletta? ORO BUTTATO!', 'battute': 2},
    {'chi': 'BARTOLOMEO', 'testo': 'Io ci metterei le bollicine... del gas!', 'battute': 2},
    {'chi': 'BRONCO', 'testo': 'Vai col tango!', 'battute': 1, 'tango': True, 'parla': [(0.15, 1.3)]},
]

if __name__ == '__main__':
    if '--plastilina' in sys.argv:
        sys.argv.remove('--plastilina'); PERSONAGGI.update(PERSONAGGI_PLASTILINA)
    print(render(PROVA_TRIO, sys.argv[1] if len(sys.argv) > 1 else 'prova_trio.mp4', testata='AL BANCONE DI BRONCO · PROVA PUPAZZI'))
