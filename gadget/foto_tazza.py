# Foto "da negozio" della tazza: tazza 3D su bancone di legno con luci del bar sfocate. Uso: python3 foto_tazza.py stampa.png out.jpg [lato]
import sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
S = 2000
def sfondo():
    y = np.linspace(0, 1, S)[:, None]
    top = np.array([48, 28, 18]); bot = np.array([96, 58, 32])
    g = (top + (bot - top) * y[..., None] ** 1.3) * np.ones((S, S, 1))
    im = Image.fromarray(g.astype('uint8'))
    # luci del bar sfocate (bokeh)
    b = Image.new('RGB', (S, S), (0, 0, 0)); d = ImageDraw.Draw(b); random.seed(7)
    for _ in range(38):
        x, yy, r = random.randint(0, S), random.randint(0, int(S * 0.55)), random.randint(25, 90)
        c = random.choice([(255, 190, 90), (255, 160, 70), (255, 220, 150), (200, 120, 60)])
        d.ellipse((x - r, yy - r, x + r, yy + r), fill=tuple(int(v * random.uniform(0.35, 0.8)) for v in c))
    im = Image.fromarray(np.clip(np.asarray(im, float) + np.asarray(b.filter(ImageFilter.GaussianBlur(18)), float), 0, 255).astype('uint8'))
    # bancone di legno: venature orizzontali morbide (rumore a piu' scale) e luce che sfuma verso il basso
    tw = int(S * 0.62); hh = S - tw; rng = np.random.default_rng(3)
    def noise(sx, sy):
        n = Image.fromarray((rng.random((sy, sx)) * 255).astype('uint8')).resize((S, hh), Image.BICUBIC)
        return np.asarray(n, float) / 255
    n = noise(6, 40) * 0.5 + noise(3, 160) * 0.35 + noise(40, 400) * 0.15
    grain = 0.5 + 0.5 * np.sin(n * 18)
    base = np.array([132, 76, 38]); dark = np.array([86, 44, 20])
    wood = dark + (base - dark) * grain[..., None]
    ys = np.arange(hh)[:, None]
    wood *= (1.05 - 0.35 * (ys / hh))[..., None]
    a = np.asarray(im, float).copy(); a[tw:] = wood
    a[tw:tw + 6] = [150, 95, 50]  # filo del bancone
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8')), tw
def tazza(stampa, lato=0.5):
    """Corpo cilindrico con la stampa avvolta (lato = punto del file rivolto alla camera), luce da sinistra."""
    src = Image.open(stampa).convert('RGBA')
    mw = 860; R = mw / 2
    # proporzioni vere: l'altezza della stampa sul corpo segue la circonferenza (niente ovali schiacciati)
    mh = int(mw * 1.16)  # 11 oz: alta 9,5 cm, larga 8,2 cm
    band_ = int(mh * 0.9); k = (src.size[1] / band_) * (math.pi * mw / src.size[0])  # disegni rotondi, non ovali
    bg = Image.new('RGBA', src.size, (255, 255, 255, 255)); bg.alpha_composite(src); src = np.asarray(bg.convert('RGB'), float)
    sh, sw = src.shape[:2]; band = int(mh * 0.9); top = int(mh * 0.05)
    # mappa cilindrica
    x = (np.arange(mw) - R + 0.5) / R; th = np.arcsin(np.clip(x, -0.9999, 0.9999))
    u = ((lato + k * th / (2 * math.pi)) % 1.0) * sw
    rows = np.clip(((np.arange(band)) / band * sh).astype(int), 0, sh - 1)
    tex = src[rows[:, None], np.clip(u.astype(int), 0, sw - 1)[None, :]]
    body = np.ones((mh, mw, 3)) * 246.0; body[top:top + band] = tex
    # luce: lambert + speculare
    nx = np.sin(th); L = np.array([-0.55, 0.0, 0.83]); nz = np.cos(th)
    lam = np.clip(nx * L[0] + nz * L[2], 0, 1)
    shade = 0.42 + 0.62 * lam
    spec = np.exp(-((th + 0.42) / 0.07) ** 2) * 0.55 + np.exp(-((th - 0.75) / 0.05) ** 2) * 0.15
    body = body * shade[None, :, None] + 255 * spec[None, :, None]
    body *= (1 - 0.06 * (np.arange(mh) / mh))[:, None, None]
    return Image.fromarray(np.clip(body, 0, 255).astype('uint8')), mw, mh
def foto(stampa, out, lato=0.5):
    im, tw = sfondo(); body, mw, mh = tazza(stampa, lato)
    cx = S // 2 - 40; x0 = cx - mw // 2; ybot = tw + 380; y0 = ybot - mh; ry = 70
    # ombra sul bancone
    sh = Image.new('L', (S, S), 0); ImageDraw.Draw(sh).ellipse((x0 - 40, ybot - 50, x0 + mw + 260, ybot + 90), fill=170)
    im.paste((25, 12, 5), (0, 0), sh.filter(ImageFilter.GaussianBlur(40)))
    # manico a destra (dietro/fianco), toroide schiacciato con sfumatura
    hd = Image.new('RGBA', (S, S), (0, 0, 0, 0)); h = ImageDraw.Draw(hd)
    hx0, hy0, hx1, hy1 = x0 + mw - 110, y0 + int(mh * 0.2), x0 + mw + 230, y0 + int(mh * 0.72)
    for i in range(70):
        v = int(150 + 95 * (1 - abs(i - 25) / 45))
        h.ellipse((hx0 + i, hy0 + i, hx1 - i, hy1 - i), outline=(v, v, v - 4, 255), width=2)
    im.paste(hd, (0, 0), hd)
    # corpo con bordo inferiore arrotondato (ellisse)
    m = Image.new('L', (mw, mh + ry), 0); md = ImageDraw.Draw(m)
    md.rectangle((0, ry, mw, mh), fill=255); md.ellipse((0, mh - ry, mw, mh + ry), fill=255)
    b2 = Image.new('RGB', (mw, mh + ry)); b2.paste(body, (0, ry))
    b2.paste(body.crop((0, mh - 1, mw, mh)).resize((mw, ry)), (0, mh))
    im.paste(b2, (x0, y0 - ry), m)
    # bocca della tazza: ellisse con interno scuro e caffè
    d = ImageDraw.Draw(im)
    d.ellipse((x0, y0 - 2 * ry, x0 + mw, y0), fill=(238, 236, 232))
    d.ellipse((x0 + 22, y0 - 2 * ry + 14, x0 + mw - 22, y0 - 14), fill=(196, 192, 186))
    d.ellipse((x0 + 40, y0 - 2 * ry + 34, x0 + mw - 40, y0 - 10), fill=(62, 36, 20))
    d.ellipse((x0 + 120, y0 - 2 * ry + 44, x0 + 420, y0 - 2 * ry + 70), fill=(110, 70, 40))
    im = im.filter(ImageFilter.UnsharpMask(2, 60, 2))
    im.save(out, quality=94); return out
if __name__ == '__main__':
    foto(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.5)
