"""Voci dei personaggi (Robi 20/11/2026): voci ElevenLabs fisse, una per personaggio, scelte da Robi.
Le voci si generano PRIMA del montaggio (con il connettore ElevenLabs, vedi TASK_SITCOM.md sezione VOCI) e si salvano in
sitcom/voci/cache/<codice>.mp3; qui le si legge soltanto. Battute senza file in cache = nessuna voce (solo fumetto).
  python3 sitcom/voci/voci.py sitcom/episodi/epNN.json   -> elenco delle battute da generare (voice_id, testo, file)"""
import os, sys, json, hashlib, subprocess, re
DIR = os.path.dirname(os.path.abspath(__file__)); CACHE = os.path.join(DIR, 'cache')
MODELLO = 'eleven_v3'
VOCI = {  # voice_id ElevenLabs (account di Robi), scelte il 20/11/2026
    'BRONCO': 'BEWlTVSPWoG721VSAnWv',      # bulldog barista: profondo, calmo, ironico
    'GEREMIA': 'DQrAbk5JYQkfbsD7QZ8f',     # vecchio scimpanzé brontolone che urla
    'BARTOLOMEO': 'Gq5e8oJrkKsAeJRonm7y',  # vecchio cavallo inventore svampito
}
def testo_parlato(t):
    t = t.replace('…', '...').strip()
    return '' if re.fullmatch(r'[.\s!?]*', t) else t
def codice(chi, testo):
    return hashlib.sha1(f"{chi.upper()}|{testo_parlato(testo)}|{VOCI.get(chi.upper())}".encode()).hexdigest()[:16]
def file_mp3(chi, testo): return os.path.join(CACHE, codice(chi, testo) + '.mp3')
def voce(chi, testo, out):
    if chi.upper() not in VOCI or not testo_parlato(testo): return None
    mp3 = file_mp3(chi, testo)
    if not os.path.exists(mp3): return None
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp3, '-af', 'highpass=f=80,loudnorm=I=-16:TP=-2',
                    '-ar', '44100', '-ac', '1', out], check=True)
    return out
def battute(ep):
    sc = ([ep['aggancio']] if ep.get('aggancio') else []) + ep['scene']
    if ep.get('finale', True): sc = sc + [{'chi': 'BRONCO', 'testo': 'Vai col tango!'}]
    return [s for s in sc if s.get('chi', '').upper() in VOCI and testo_parlato(s.get('testo', ''))]
if __name__ == '__main__':
    ep = json.load(open(sys.argv[1])); visti = set()
    for s in battute(ep):
        f = file_mp3(s['chi'], s['testo'])
        if f in visti: continue
        visti.add(f)
        stato = 'GIA FATTA' if os.path.exists(f) else 'DA FARE'
        print(json.dumps({'stato': stato, 'voice_id': VOCI[s['chi'].upper()], 'model_id': MODELLO,
                          'testo': testo_parlato(s['testo']), 'file': os.path.relpath(f)}, ensure_ascii=False))
