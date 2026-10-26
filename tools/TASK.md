# Attività pianificata Bronco (ogni 2 giorni, 08:30 Europe/Rome)
1. add_repo marconicreation/bronco-media (push), clone, leggi state.json.
2. Scegli un'immagine da pose/nuove NON in state.usate (se finite, riparti da capo). Mai quelle di pose/usate.
3. Cerca sui giornali di IERI i temi economici dominanti (bollette, caro vita, tasse, prezzi). Scrivi UNA battuta italiana breve (max ~60 caratteri), satira sagace e sottile su sistema/fisco/burocrazia/prezzi, MAI partiti o persone, MAI fatti inventati, niente cifre precise (al massimo tondi: metà, due fette).
4. python3 tools/caption.py pose/nuove/X.jpg pose/pubblicate/AAAA-MM-GG.jpg "battuta" --hl parola --pos top|bottom --shape pill --color N --tx .. --lines N --width ..
   Poi GUARDA l'immagine con Read: il muso di Bronco (occhi, naso, bocca) non va mai coperto. Se coperto: pos bottom, fumetto più stretto/verticale (--width 0.5 --lines 4), codina verso il corpo. Ripeti finché ok.
5. git add/commit/push (commit con user marconicreation / rmarconi79@gmail.com). URL: https://raw.githubusercontent.com/marconicreation/bronco-media/main/pose/pubblicate/AAAA-MM-GG.jpg
6. Metricool createScheduledPost: blogId 7649060, Instagram POST, tz Europe/Rome, pubblicazione ~10 minuti dopo; didascalia = battuta + riga vuota + "Bronco · agente IA di MarconiCreation" + hashtag (#bronco #marconicreation #bar #caro vita ...). Massimo 20 post/mese su Metricool: controlla state.pubblicazioni del mese, se >=20 fermati e avvisa.
7. Aggiorna state.json (usate, pubblicazioni con data e id), push. Notifica Robi con anteprima e battuta.
