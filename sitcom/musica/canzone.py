"""Musica della sitcom dal 20/11/2026 (Robi 19/11 sera): "Torso Stufo", canzone scritta da Robi (sua, niente diritti).
110 bpm esatti (GarageBand), 1 battuta = 2,18 s. Parte dalla battuta 14 (30,55 s), dove la canzone e' gia' piena.
Le variabili d'ambiente SITCOM_MUSICA / SITCOM_BPM / SITCOM_INIZIO la sostituiscono (SITCOM_MUSICA=lounge = vecchia base sintetica)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
FILE = os.environ.get('SITCOM_MUSICA', os.path.join(HERE, 'torso_stufo.m4a'))
BPM = float(os.environ.get('SITCOM_BPM', '110'))
INIZIO = float(os.environ.get('SITCOM_INIZIO', str(round(14 * 240 / 110, 4))))
ATTIVA = FILE != 'lounge' and os.path.exists(FILE)
if __name__ == '__main__': print(f'{FILE if ATTIVA else ""}|{INIZIO}')
