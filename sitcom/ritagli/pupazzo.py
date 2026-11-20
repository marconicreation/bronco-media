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

def carica(cartella, scala):
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
        a = cv2.warpAffine(np.array(s), M, base.size, flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        return Image.fromarray(a)
    def trapianta(src, box):
        w, h = base.size; x0, y0, x1, y1 = [int(v) for v in (box[0] * w, box[1] * h, box[2] * w, box[3] * h)]
        m = Image.new('L', base.size, 0); ImageDraw.Draw(m).ellipse((x0, y0, x1, y1), fill=255)
        m = m.filter(ImageFilter.GaussianBlur(10))
        out = base.copy(); al = allinea(src)
        out.paste(al.convert('RGB'), (0, 0), m)
        out.putalpha(base.getchannel('A'))
        return out
    BOCCA = (0.22, 0.50, 0.78, 0.90); OCCHI = (0.12, 0.18, 0.88, 0.50)
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

def render(cartella, voce, battute, out_mp4, testata='AL BANCONE DI BRONCO · PROVA PUPAZZO', scala=0.95, ritardo=0.3):
    P = carica(cartella, scala)
    bg, ban = R.sfondo_bar()
    gr = R.grana()
    BAR = 240 / 110
    tot = 5 * BAR; n = int(round(tot * FPS))
    vol = volume_voce(voce, n, ritardo)
    T = P['torso']; tw, th = T.size
    tx, ty = S // 2 - tw // 2, 1172 - th
    hw, hh = P['chiusa'].size
    collo = (S // 2, ty + 70)                      # dove la testa si appoggia sul torso
    sp_sx, sp_dx = (tx + 70, ty + 80), (tx + tw - 70, ty + 80)
    tmp = tempfile.mkdtemp(); stato = None; ultimo = None; bocca = 'chiusa'; tenuta = 0
    for k in range(n):
        t = k / FPS; q = int(t * POSE_FPS)
        # bocca dal volume della voce, con forme tenute almeno 2 fotogrammi (scatto da carta)
        v = vol[k]
        nuova = 'aperta' if v > 0.62 else 'parla' if v > 0.16 else 'chiusa'
        if tenuta <= 0 or nuova == 'chiusa' and bocca == 'chiusa': bocca, tenuta = nuova, 2
        tenuta -= 1
        parla = vol[max(0, k - 6):k + 6].max() > 0.16
        if q != (stato or (None,))[0]:
            r = random.Random(q)
            ang_t = round((2.5 * math.sin(t * 2.6) + (r.uniform(-1.5, 1.5) if parla else 0)) * 2) / 2
            dy_t = int(-6 * abs(math.sin(t * 6.0))) if parla else 0
            # braccio destro: gesticola quando parla, si alza per "Vai col tango!"
            if t >= battute[-1][0]: ang_d = 150 if t > battute[-1][0] + 0.15 else 80
            elif parla: ang_d = [48, 70, 58, 78][(q // 3) % 4]
            else: ang_d = 30
            ang_s = -28 + (-14 if parla and (q // 5) % 2 else 0)
            occhi = (t % 2.9) < 0.17 and not parla
            stato = (q, ang_t, dy_t, ang_d, ang_s, occhi)
        _, ang_t, dy_t, ang_d, ang_s, occhi = stato
        faccia = 'blink' if occhi else bocca
        if t >= battute[-1][0] + 0.15 and bocca == 'chiusa' and t > battute[-1][1]: faccia = 'parla' if False else 'chiusa'
        chiave = (faccia, ang_t, dy_t, ang_d, ang_s, next(i for i, b in reversed(list(enumerate(battute))) if b[0] <= t + 1e-9 or i == 0))
        if chiave == ultimo[0] if ultimo else False:
            ultimo[1].save(os.path.join(tmp, f'{k:05d}.jpg'), quality=92); continue
        fr = bg.copy(); fr.alpha_composite(ban)
        bs, xy = ruota(P['bsx'], ang_s, (P['bsx'].width // 2, 30), sp_sx); metti(fr, bs, xy)
        bd, xy = ruota(P['bdx'], ang_d, (P['bdx'].width // 2, 30), sp_dx); metti(fr, bd, xy)
        metti(fr, T, (tx, ty + dy_t // 3))
        hd, xy = ruota(P[faccia], ang_t, (hw // 2, hh - 60), (collo[0], collo[1] + dy_t)); metti(fr, hd, xy)
        # bancone davanti (copre la vita e le braccia sotto)
        fr.alpha_composite(ban.crop((0, 1112, S, S)), (0, 1112))
        sq = fr.convert('RGB').resize((W, W), Image.LANCZOS)
        a = np.array(sq).astype(np.float32) + gr[:, :, None]
        sq = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        c = Image.new('RGB', (W, H), R.BG); c.paste(sq, (0, IMG_Y)); d = ImageDraw.Draw(c)
        d.text((W // 2, 62), testata, font=R.f_tag, fill=R.GOLD, anchor='mm', stroke_width=3, stroke_fill='black')
        bi = chiave[-1]
        if battute[bi][0] <= t: R.fumetto(c, battute[bi][2])
        d.text((W // 2, 1790), '@marconicreation', font=R.f_tag, fill=(230, 200, 160), anchor='mm')
        c.save(os.path.join(tmp, f'{k:05d}.jpg'), quality=92); ultimo = (chiave, c)
    sys.path.insert(0, os.path.join(R.SITCOM, 'musica')); import canzone
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(tmp, '%05d.jpg'), '-i', voce]
    if canzone.ATTIVA:
        cmd += ['-ss', str(canzone.INIZIO), '-i', canzone.FILE, '-filter_complex',
                f'[1:a]aformat=channel_layouts=stereo:sample_rates=44100,adelay={int(ritardo * 1000)}|{int(ritardo * 1000)},volume=1.6,asplit[v1][v2];'
                f'[2:a]aformat=channel_layouts=stereo:sample_rates=44100,volume=0.35[m];'
                f'[m][v1]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=300[md];[md][v2]amix=inputs=2:normalize=0,'
                f'afade=t=out:st={tot - 1.2:.2f}:d=1.2[a]', '-map', '0:v', '-map', '[a]']
    else:
        cmd += ['-filter_complex', f'[1:a]adelay={int(ritardo * 1000)}[a]', '-map', '0:v', '-map', '[a]']
    cmd += ['-t', f'{tot:.3f}', '-c:a', 'aac', '-b:a', '160k', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', out_mp4]
    subprocess.run(cmd, check=True)
    return out_mp4

# (inizio, fine, testo) in secondi sul video; la voce parte a 0,3 s
PROVA = [(0.0, 3.4, 'Cocktail nuovo: si chiama Bolletta.'),
         (3.4, 7.6, 'Ti lascia senza parole... e senza portafoglio.'),
         (7.6, 10.9, 'Vai col tango!')]

if __name__ == '__main__':
    print(render(os.path.join(HERE, 'bronco'), os.path.join(HERE, 'bronco', 'prova_voce.mp3'), PROVA,
                 sys.argv[1] if len(sys.argv) > 1 else 'prova_pupazzo_bronco.mp4'))
