# Attività pianificata Bronco (ogni 2 giorni, 08:30 Europe/Rome) - REEL
1. add_repo marconicreation/bronco-media (push), clone, leggi state.json.
2. Scegli un'immagine da pose/nuove NON in state.usate (se finite, riparti da capo). Mai quelle di pose/usate.
3. Cerca sui giornali di IERI i temi economici dominanti (bollette, caro vita, tasse, prezzi). Scrivi UNA battuta italiana breve (max ~60 caratteri), satira sagace e sottile su sistema/fisco/burocrazia/prezzi, MAI partiti o persone, MAI fatti inventati, niente cifre precise (al massimo tondi: metà, due fette).
4. python3 tools/caption.py pose/nuove/X.jpg pose/pubblicate/AAAA-MM-GG.jpg "battuta" --hl parola --pos top|bottom --shape oval --color N --to X,Y [--thought] --tx .. --lines N --width ..
   Poi GUARDA l'immagine con Read: il muso di Bronco (occhi, naso, bocca) non va mai coperto. Se coperto: pos bottom, fumetto più stretto/verticale (--width 0.5 --lines 4), codina verso il corpo. Ripeti finché ok.
5. REEL (dal 13/11/2026 Robi vuole SOLO Reel, niente post immagine). Crea il video:
   python3 tools/reel.py pose/nuove/X.jpg pose/pubblicate/AAAA-MM-GG.jpg promo/video/reel_AAAA-MM-GG.mp4 --hook "TEMA IN 1-3 PAROLE" --cta regalo
   (--cta regalo fino al 24/12/2026 compreso, dopo usa --cta segui). Il hook è il tema del giorno (es. "BOLLETTE", "CARO SPESA"), mai nomi di persone o partiti.
   Controlla 3 fotogrammi con Read (ffmpeg -ss 0.5 / 3 / 8.5 -i video -frames:v 1 f.jpg): testi leggibili, muso di Bronco libero.
   git add/commit/push del jpg e del mp4 (commit con user marconicreation / rmarconi79@gmail.com).
   URL video: https://raw.githubusercontent.com/marconicreation/bronco-media/main/promo/video/reel_AAAA-MM-GG.mp4 (prima di usarlo verifica con curl -sI che risponda 200).
6. Metricool createScheduledPost: blogId 7649060, tz Europe/Rome, pubblicazione ~10 minuti dopo, media = [URL video], info.videoCoverMilliseconds 3000,
   providers [{"network":"instagram"},{"network":"facebook"}], instagramData {"type":"REEL","showReelOnFeed":true,"isAiGenerated":true}, facebookData {"type":"REEL"}.
   Didascalia = battuta + riga vuota + "Bronco · agente IA di MarconiCreation" + riga "Regalo di Natale: il cocktail col tuo nome, link in bio" (fino al 24/12) + hashtag (#bronco #marconicreation #bar #carovita #reels ...).
   Massimo 20 post/mese su Metricool: controlla state.pubblicazioni del mese, se >=20 fermati e avvisa.
7. Aggiorna state.json (usate, pubblicazioni con data e id), push. Notifica Robi con la battuta e il link al video.

Nota: con fumetto ovale usa --tx verso il lato SENZA testa (0.15-0.25 o 0.8) così la codina non tocca il viso; entrambi gli occhi devono vedersi aperti e interi.

Scelta della posizione del fumetto (guarda prima la posa):
1. Se sopra la testa di Bronco c'è spazio libero (orecchie/sfondo) -> --pos top (come i fumetti classici), --tx verso il lato senza testa.
2. Se la testa tocca il bordo alto o gli occhi sono troppo in alto -> --pos bottom (sul petto/bancone, evitando oggetti importanti) oppure --pos left/right --y 0.1-0.5 --lines 4 (fumetto laterale verticale su sfondo libero, senza coprire mani/oggetti chiave).
3. Controlla SEMPRE il risultato: occhi, naso, bocca liberi, testo leggibile. Altrimenti prova un'altra posizione.

Direzione del fumetto: la codina deve SEMPRE indicare Bronco: usa --to X,Y (frazioni) puntando al bordo della testa/guancia/mento vicino alla bocca, senza toccare il muso. Fumetto in basso -> codina verso l'alto; laterale -> verso Bronco; in alto -> verso il basso.
Ogni tanto (circa 1 post su 4, o quando la battuta è una riflessione) usa --thought: fumetto pensiero con pallini che salgono verso la testa di Bronco.

Facebook: il Reel esce anche sulla pagina MarconiCreation Portovenere (id 691340067386511) tramite facebookData REEL. Se Metricool rifiuta facebookData, crea un secondo post solo Facebook REEL.
