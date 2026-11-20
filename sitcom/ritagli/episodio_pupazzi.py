"""Monta una puntata (sitcom/episodi/epNN.json) con i pupazzi in plastilina e le scritte stile TikTok.
Uso: python3 episodio_pupazzi.py sitcom/episodi/epNN.json uscita.mp4 [cartella_voci]
cartella_voci (facoltativa): un mp3 per scena, chiamati 00.mp3, 01.mp3... nell'ordine delle scene montate
(aggancio, scene, "Vai col tango!"); senza voci la bocca si muove da sola mentre c'e' la scritta.
In coda: sigla (sitcom/sigla/sigla.py --accoda) e la canzone continua sotto tutto, abbassata dove parlano.

Elenco delle battute da registrare (numero file, voce, testo):  python3 episodio_pupazzi.py --battute epNN.json
"Sciabadù!" e "Vai col tango!" non si registrano: le copia da sole da voci_fisse/.
Le voci vengono ripulite dai silenzi all'inizio e alla fine; se una battuta dura troppo viene accelerata un poco
e l'inquadratura si allunga a battute intere di musica."""
import sys, os, json, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); SITCOM = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pupazzo as P

P.PERSONAGGI.update(P.PERSONAGGI_PLASTILINA); P.STILE_TESTO = 'tiktok'
BAR = 240 / 110
# voci fisse scelte da Robi (20/11/2026), da usare con eleven_v3
VOCI_ID = {'BRONCO': 'R4gEgJEocQc2CqX4LOsT', 'GEREMIA': 'DQrAbk5JYQkfbsD7QZ8f', 'BARTOLOMEO': 'Gq5e8oJrkKsAeJRonm7y'}
FISSE = os.path.join(HERE, 'voci_fisse')

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
    out.append({'chi': 'BRONCO', 'testo': 'Vai col tango!', 'battute': 1, 'tango': True, 'fissa': 'bronco_vai_col_tango.mp3'})
    for s in out:
        if s['testo'].lower().startswith('sciabad'): s['fissa'] = 'bartolomeo_sciabadu.mp3'
    sg = ep.get('saga')   # mini-saga: cartello "continua" / "fine"; altrimenti l'invito per domani
    if sg and sg['parte'] < sg['di']:
        out.append({'chi': 'CARTELLO', 'righe': ['CONTINUA...'], 'sotto': f"{sg['titolo']}\nParte {sg['parte'] + 1} di {sg['di']}\ndomani alle 13", 'battute': 1})
    elif sg:
        out.append({'chi': 'CARTELLO', 'righe': ['FINE'], 'sotto': f"{sg['titolo']}\nla saga completa", 'battute': 1})
    else:
        out.append({'chi': 'CARTELLO', 'righe': ['DOMANI', 'ALLE 13'], 'sotto': 'nuova puntata\nsegui @marconicreation', 'battute': 1})
    return out

def da_registrare(scene):
    """[(numero file, chi, voice_id, testo)] delle battute che servono (niente mute, trio, cartelli e voci fisse)."""
    return [(i, s['chi'], VOCI_ID[s['chi']], s['testo']) for i, s in enumerate(scene)
            if s['chi'] in VOCI_ID and s['testo'] and not s.get('fissa') and s.get('parla', 1) != []]

def prepara_voci(scene, cartella, out):
    """Copia le voci in out/: fisse da voci_fisse/, le altre ripulite dai silenzi (e accelerate se oltre 8 s)."""
    os.makedirs(out, exist_ok=True); manca = []; servono = {r[0] for r in da_registrare(scene)}
    pulisci = 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse'
    for i, s in enumerate(scene):
        dst = os.path.join(out, f'{i:02d}.mp3')
        if s.get('fissa'): subprocess.run(['cp', os.path.join(FISSE, s['fissa']), dst], check=True); continue
        src = os.path.join(cartella, f'{i:02d}.mp3')
        if not os.path.exists(src):
            if i in servono: manca.append(i)
            continue
        tmp = dst + '.wav'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-af', pulisci, tmp], check=True)
        d = durata(tmp); vel = min(1.25, d / 8.0) if d > 8.0 else 1.0
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-af', f'atempo={vel:.3f}', '-b:a', '128k', dst], check=True)
        os.remove(tmp)
    if manca: print('ATTENZIONE: mancano le voci delle scene', manca, file=sys.stderr)
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

def bollino(ep):
    """Calendario dell'Avvento (dal 1/12): bollino rosso "-K A NATALE" in alto a destra sulla scena."""
    if not ep.get('avvento'): return None
    k = 25 - int(ep['avvento']); txt = 'VIGILIA!' if k == 1 else f'-{k} A NATALE'
    import ritagli as R
    def dis(d, y):
        tw = d.textlength(txt, font=R.f_tag) + 50
        d.rounded_rectangle((P.W - 24 - tw, y + 20, P.W - 24, y + 96), 38, fill=(194, 30, 36), outline=R.CREAM, width=5)
        d.text((P.W - 24 - tw / 2, y + 58), txt, font=R.f_tag, fill='white', anchor='mm', stroke_width=3, stroke_fill='black')
    return dis

if __name__ == '__main__':
    if sys.argv[1] == '--battute':
        for i, chi, vid, testo in da_registrare(scene_da_json(json.load(open(sys.argv[2])))):
            print(f'{i:02d}.mp3\t{chi}\t{vid}\t{testo}')
        sys.exit()
    J, OUT = sys.argv[1], sys.argv[2]; VOCI = sys.argv[3] if len(sys.argv) > 3 else None
    ep = json.load(open(J)); scene = scene_da_json(ep)
    T = tempfile.mkdtemp(); P.DECORA = bollino(ep)
    if VOCI: VOCI = prepara_voci(scene, VOCI, os.path.join(T, 'voci')); adatta_battute(scene, VOCI)
    voce = voce_unica(scene, VOCI, os.path.join(T, 'voci.mp3')) if VOCI else None
    testata = f"AL BANCONE DI BRONCO · EP. {ep['numero']}"
    if ep.get('saga'): testata += f" · PARTE {ep['saga']['parte']}/{ep['saga']['di']}"
    P.render(scene, os.path.join(T, 'ep.mp4'), testata=testata, voce=voce, ritardo=0)
    subprocess.run(['python3', os.path.join(SITCOM, 'sigla', 'sigla.py'), '--accoda', os.path.join(T, 'ep.mp4'), os.path.join(T, 'full.mp4')], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(T, 'full.mp4'), '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', OUT], check=True)
    print(OUT)
