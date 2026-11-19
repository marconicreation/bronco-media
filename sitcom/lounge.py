"""Musica della sitcom dal 20/11/2026 (Robi 19/11: "troppo ritmata, cambiare musica").
Funk anni '70 morbido, stile lounge da bar: basso suonato con le dita in primo piano, chitarra pulita stoppata,
piano elettrico, batteria leggera (cerchio del rullante, shaker). Tutto sintetizzato qui, nessun diritto.

Tempo: 100 bpm, 1 battuta = 2,4 s. Il montaggio cambia inquadratura ogni 2 battute (4,8 s), vedi sitcom.py.
Uso da codice:  import lounge; lounge.music(secondi, 'out.wav')
Uso da terminale:  python3 lounge.py 30 prova.wav
"""
import sys, wave
import numpy as np

BPM = 100; BEAT = 60 / BPM; BAR = 4 * BEAT; S16 = BEAT / 4
SR = 44100

def _lp(x, fc, q=2.0):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** (2 * q)), len(x))
def _hp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X * (1 - 1 / np.sqrt(1 + (f / fc) ** 4)), len(x))
def _hz(m): return 440 * 2 ** ((m - 69) / 12)

def _corda(m, dur, rng, smorza=0.996, chiaro=0.5):
    """Corda pizzicata (Karplus-Strong) calcolata a blocchi con numpy: suono di chitarra vero, non elettronico."""
    n = int(dur * SR); L = max(2, int(round(SR / _hz(m))))
    y = np.zeros(n + L + 1)
    y[1:L + 1] = _lp(rng.uniform(-1, 1, L * 4), 2000 + 4000 * chiaro)[:L]
    for a in range(L + 1, len(y), L):
        b = min(a + L, len(y))
        y[a:b] = smorza * 0.5 * (y[a - L:b - L] + y[a - L - 1:b - L - 1])
    y = y[1:n + 1]; t = np.arange(n) / SR
    rel = int(0.01 * SR); y[-rel:] *= np.linspace(1, 0, rel)
    return y * np.minimum(1, t / 0.002)

def _rhodes(ms, dur, vel=1.0):
    """Piano elettrico (FM morbido con tremolo), accordo tenuto."""
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for m in ms:
        f = _hz(m); idx = 1.8 * np.exp(-t * 6) + 0.2
        x += np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t)) * np.exp(-t * 1.6)
    x *= (1 + 0.18 * np.sin(2 * np.pi * 4.5 * t)) * np.minimum(1, t / 0.004)
    rel = int(0.08 * SR); x[-rel:] *= np.linspace(1, 0, rel)
    return 0.06 * vel * x

def _basso(m, dur, acc=1.0):
    """Basso elettrico con le dita, caldo e rotondo (filtro piu' chiuso rispetto alla sigla)."""
    n = int(dur * SR); t = np.arange(n) / SR; f = _hz(m)
    x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.25 * np.sin(6 * np.pi * f * t) + 0.15 * (2 * ((f * t) % 1) - 1)
    x = _lp(x, 420 + 900 * acc, 1.5) + _lp(x * np.exp(-t * 70), 1800) * 0.4
    x = np.tanh(1.6 * x) * np.minimum(1, t / 0.004) * (0.6 + 0.4 * np.exp(-t * 3))
    rel = int(0.02 * SR); x[-rel:] *= np.linspace(1, 0, rel)
    return 0.55 * acc * x

def music(sec, path, finale=True):
    rng = np.random.RandomState(11)
    N = int(sec * SR); tot = N + 3 * SR
    bus = {k: np.zeros(tot) for k in ('dr', 'bass', 'gtr', 'ep')}
    def add(k, sig, at):
        i = int(at * SR)
        if 0 <= i < tot: bus[k][i:i + len(sig)] += sig[:tot - i]
    def kick():
        n = int(0.25 * SR); t = np.arange(n) / SR; f = 48 + 40 * np.exp(-t * 30)
        return 0.5 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
    def cerchio():  # colpo sul cerchio del rullante (cross-stick), secco e morbido
        n = int(0.06 * SR); t = np.arange(n) / SR
        return 0.22 * (np.sin(2 * np.pi * 1700 * t) + 0.6 * np.sin(2 * np.pi * 820 * t)) * np.exp(-t * 90) + 0.05 * _hp(rng.randn(n), 3000) * np.exp(-t * 120)
    def shaker(acc):
        n = int(0.07 * SR); t = np.arange(n) / SR
        return (0.035 + 0.035 * acc) * _hp(rng.randn(n), 6000) * np.minimum(1, t / 0.012) * np.exp(-t * 45)
    # giro: Rem9 | Sol13 (dorico, il classico groove da lounge), 2 battute ciascuno
    D = 38; G = 43
    ACC = {D: [[62, 65, 69, 72, 76], [53, 57, 60, 64]], G: [[59, 64, 65, 69], [53, 59, 64]]}
    # basso: (sedicesimo, semitoni dalla tonica, durata in sedicesimi, accento) - poche note, larghe, con una salita a fine giro
    riff1 = [(0, 0, 5, 1), (6, 12, 1.6, .7), (8, 7, 3, .9), (11, 10, 1, .6), (12, 12, 2, .8), (14, 10, 1.5, .7)]
    riff2 = [(0, 0, 5, 1), (6, 12, 1.6, .7), (8, 7, 4, .9), (13, 3, 1, .7), (14, 4, 1, .8), (15, 5, 1, .8)]
    bars = max(1, int(np.ceil(sec / BAR)))
    for b in range(bars):
        t0 = b * BAR; root = D if (b // 2) % 2 == 0 else G; last = finale and b == bars - 1
        if last:  # chiusura: accordo tenuto, basso e chitarra che sfumano
            add('bass', _basso(D, BAR * 0.95, 1), t0); add('dr', kick(), t0)
            add('ep', _rhodes(ACC[D][0], BAR * 0.95, 1.2), t0)
            for i, m in enumerate([50, 57, 60, 64, 69]): add('gtr', 0.25 * _corda(m, BAR * 0.9, rng, 0.9995, 0.4), t0 + i * 0.025)
            continue
        for s in range(16):
            if s == 0 or s == 10 or (s == 7 and b % 2): add('dr', kick(), t0 + s * S16)
            if s in (4, 12): add('dr', cerchio(), t0 + s * S16)
            add('dr', shaker(1 if s % 4 == 2 else 0), t0 + s * S16 + (0.012 if s % 2 else 0))  # leggero swing
        for s, semi, ln, acc in (riff2 if b % 2 else riff1):
            add('bass', _basso(root + semi, ln * S16 * 0.95, acc), t0 + s * S16)
        alto, basso_acc = ACC[root]
        if b % 2 == 0: add('ep', _rhodes(alto, BAR * 1.9, 1.0), t0)          # accordo lungo
        else: add('ep', _rhodes(alto, BEAT * 1.5, 0.7), t0 + 6 * S16)          # anticipo morbido
        for s in (2, 6, 10, 14):  # chitarra stoppata sui controtempi, accordo strappato verso il basso
            v = 0.12 if s in (6, 14) else 0.08
            for i, m in enumerate(basso_acc): add('gtr', v * _corda(m + 12, S16 * 0.9, rng, 0.985, 0.35), t0 + s * S16 + i * 0.006)
        if b % 4 == 3:  # piccola frase di chitarra a fine giro
            for i, (s, m) in enumerate([(8, 74), (10, 72), (11, 69), (12, 67), (14, 69)]):
                add('gtr', 0.28 * _corda(m, S16 * 2.2, rng, 0.997, 0.6), t0 + s * S16)
    gtr = bus['gtr'] + 0.35 * np.roll(bus['gtr'], int(0.11 * SR)) * 0.6  # un'eco corta di ambiente
    mix = 0.6 * bus['dr'] + 1.2 * bus['bass'] + 3.2 * gtr + 3.6 * bus['ep']
    rev = np.zeros_like(mix)  # riverbero leggero da locale
    for d, g in ((0.031, .22), (0.047, .18), (0.071, .14), (0.103, .1), (0.149, .07)): rev += g * np.roll(mix, int(d * SR))
    y = (mix + 0.5 * _lp(rev, 3500))[:N]
    y = np.tanh(1.1 * y) / np.tanh(1.1)
    y *= np.clip((sec - np.arange(N) / SR) / 0.4, 0, 1); y *= 0.85 / max(1e-6, np.abs(y).max())
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())

if __name__ == '__main__':
    music(float(sys.argv[1]) if len(sys.argv) > 1 else 20, sys.argv[2] if len(sys.argv) > 2 else 'lounge_prova.wav')
