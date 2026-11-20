"""Estrae i pezzi del pupazzo dai fogli generati con l'IA (fondo bianco) usando rembg birefnet-general.
Uso: python3 estrai_pezzi.py foglio_pezzi.png foglio_teste.png cartella_uscita
foglio_pezzi: testa (in alto a sinistra), torso (in alto a destra), braccio sx e dx (in basso).
foglio_teste: 4 teste in fila (chiusa, parla, aperta, occhi chiusi).
Nota: birefnet usa ~4 GB di memoria, un foglio alla volta."""
import sys, os
import numpy as np, cv2
from PIL import Image
from rembg import remove, new_session

def pezzi(sess, path, minarea=20000):
    im = Image.open(path).convert('RGB')
    m = np.array(remove(im, session=sess, only_mask=True))
    a = (m > 128).astype(np.uint8)
    n, l, st, _ = cv2.connectedComponentsWithStats(a)
    out = []
    for i in range(1, n):
        if st[i, 4] < minarea: continue
        x, y, w, h = st[i, :4]
        mk = np.where(l == i, m, 0).astype(np.uint8)
        out.append(((x, y), Image.fromarray(np.dstack([np.array(im), mk])[y:y + h, x:x + w])))
    return out

if __name__ == '__main__':
    fp, ft, od = sys.argv[1:4]; os.makedirs(od, exist_ok=True)
    s = new_session('birefnet-general')
    P = pezzi(s, fp); mid = Image.open(fp).height / 2
    alto = sorted([p for p in P if p[0][1] < mid], key=lambda p: p[0][0])
    basso = sorted([p for p in P if p[0][1] >= mid], key=lambda p: p[0][0])
    alto[-1][1].save(os.path.join(od, 'torso.png'))
    basso[0][1].save(os.path.join(od, 'braccio_sx.png')); basso[-1][1].save(os.path.join(od, 'braccio_dx.png'))
    T = sorted(pezzi(s, ft), key=lambda p: p[0][0])
    for i, (_, p) in enumerate(T[:4]): p.save(os.path.join(od, f'testa{i}.png'))
    print(len(P), 'pezzi,', len(T), 'teste')
