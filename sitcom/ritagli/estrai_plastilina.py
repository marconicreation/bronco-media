"""Pezzi dei pupazzi in plastilina (fogli IA su fondo grigio) -> cartella.
Uso: python3 estrai_plastilina.py pezzi|teste foglio.png cartella
Va lanciato due volte (prima pezzi, poi teste): birefnet usa ~4 GB, un foglio per processo.
Le teste del foglio facce vengono riscalate alla misura della testa del foglio pezzi."""
import sys, os, json
from PIL import Image
from rembg import new_session
from estrai_pezzi import pezzi

modo, foglio, od = sys.argv[1:4]; os.makedirs(od, exist_ok=True)
s = new_session('birefnet-general')
if modo == 'pezzi':
    P = pezzi(s, foglio); mid = Image.open(foglio).height / 2
    cy = lambda p: p[0][1] + p[1].height / 2
    alto = sorted([p for p in P if cy(p) < mid], key=lambda p: p[0][0])
    basso = sorted([p for p in P if cy(p) >= mid], key=lambda p: p[0][0])
    alto[0][1].save(os.path.join(od, 'testa_pezzi.png')); alto[-1][1].save(os.path.join(od, 'torso.png'))
    basso[0][1].save(os.path.join(od, 'braccio_sx.png')); basso[-1][1].save(os.path.join(od, 'braccio_dx.png'))
    print(len(P), 'pezzi')
else:
    rif = Image.open(os.path.join(od, 'testa_pezzi.png'))
    T = sorted(pezzi(s, foglio), key=lambda p: p[0][0])[:4]
    k = rif.width / T[0][1].width
    for i, (_, p) in enumerate(T):
        p.resize((round(p.width * k), round(p.height * k)), Image.LANCZOS).save(os.path.join(od, f'testa{i}.png'))
    print(len(T), 'teste, scala', round(k, 3))
