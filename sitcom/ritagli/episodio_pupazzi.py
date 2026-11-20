"""Monta una puntata (sitcom/episodi/epNN.json) con i pupazzi in plastilina e le scritte stile TikTok.
Uso: python3 episodio_pupazzi.py sitcom/episodi/epNN.json uscita.mp4 [cartella_voci]
cartella_voci (facoltativa): un mp3 per scena, chiamati 00.mp3, 01.mp3... nell'ordine delle scene montate
(aggancio, scene, "Vai col tango!"); senza voci la bocca si muove da sola mentre c'e' la scritta.
In coda: sigla (sitcom/sigla/sigla.py --accoda) e la canzone continua sotto tutto, abbassata dove parlano."""
import sys, os, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); SITCOM = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pupazzo as P

P.PERSONAGGI.update(P.PERSONAGGI_PLASTILINA); P.STILE_TESTO = 'tiktok'
BAR = 240 / 110

def chi_di(sc):
    if sc.get('chi'): return sc['chi'].upper()
    nome = os.path.basename(sc.get('img', ''))
    for c in ('bronco', 'geremia', 'bartolomeo'):
        if nome.startswith(c): return c.upper()
    return 'TRIO'

def scene_da_json(ep):
    out = []
    for sc in ([ep['aggancio']] if ep.get('aggancio') else []) + ep['scene']:
        chi = chi_di(sc); testo = (sc.get('testo') or '').strip()
        s = {'chi': chi, 'testo': testo, 'battute': sc.get('battute', 2)}
        if chi == 'TRIO': s['testo'] = ''
        if testo in ('...', '…'): s['parla'] = []                     # reazione muta
        if testo.lower().startswith('sciabad'): s['tango'] = True        # braccio al cielo
        out.append(s)
    out.append({'chi': 'BRONCO', 'testo': 'Vai col tango!', 'battute': 1, 'tango': True})
    return out

def durata(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)

def adatta_battute(scene, cartella):
    """Allunga l'inquadratura (a battute intere di musica) se la voce non ci sta."""
    import math
    for i, s in enumerate(scene):
        f = os.path.join(cartella, f'{i:02d}.mp3')
        if os.path.exists(f): s['battute'] = max(s['battute'], math.ceil((durata(f) + 0.6) / BAR))

def voce_unica(scene, cartella, out):
    """Mette in fila le voci (una per scena, 0,3 s dopo l'inizio della sua inquadratura)."""
    ins, filt, t, j = [], [], 0.0, 0
    for i, s in enumerate(scene):
        f = os.path.join(cartella, f'{i:02d}.mp3')
        if os.path.exists(f):
            ins += ['-i', f]; ms = int((t + 0.3) * 1000)
            filt.append(f'[{j}:a]aformat=channel_layouts=mono:sample_rates=44100,adelay={ms}[a{j}]'); j += 1
        t += s['battute'] * BAR
    if not j: return None
    mix = ''.join(f'[a{k}]' for k in range(j))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(filt) + f';{mix}amix=inputs={j}:normalize=0[o]', '-map', '[o]', out], check=True)
    return out

if __name__ == '__main__':
    J, OUT = sys.argv[1], sys.argv[2]; VOCI = sys.argv[3] if len(sys.argv) > 3 else None
    ep = json.load(open(J)); scene = scene_da_json(ep)
    T = tempfile.mkdtemp()
    if VOCI: adatta_battute(scene, VOCI)
    voce = voce_unica(scene, VOCI, os.path.join(T, 'voci.mp3')) if VOCI else None
    testata = f"AL BANCONE DI BRONCO · EP. {ep['numero']}"
    P.render(scene, os.path.join(T, 'ep.mp4'), testata=testata, voce=voce, ritardo=0)
    subprocess.run(['python3', os.path.join(SITCOM, 'sigla', 'sigla.py'), '--accoda', os.path.join(T, 'ep.mp4'), os.path.join(T, 'full.mp4')], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(T, 'full.mp4'), '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', OUT], check=True)
    print(OUT)
