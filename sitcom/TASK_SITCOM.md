# Sitcom "Al bancone di Bronco": una puntata al giorno (Robi, 13/11/2026)

Ogni giorno alle 13:00 (Europe/Rome) lo scenario Make "Puntata sitcom 13:00" pubblica la puntata del giorno come REEL su
Instagram @marconicreation e sulla pagina Facebook MarconiCreation (Portovenere), leggendo la cassetta di Make
(data store 233472, key "puntata": date = AAAA-MM-GG, v1 = URL del video, m1 = didascalia). Metricool NON si usa (limite 20 post/mese).

## Routine serale (prepara la puntata di DOMANI)
1. add_repo marconicreation/bronco-media (push), git clone, cd bronco-media. D = data di DOMANI (Europe/Rome).
2. Cerca in sitcom/episodi/ un epNN.json con "data" = D. Se c'è ed esiste epNN.mp4, vai al punto 6.
3. Se non c'è: scrivi la puntata nuova (numero = ultimo + 1) seguendo le REGOLE qui sotto e lo stesso schema JSON delle puntate esistenti
   (copia la struttura di un epNN.json recente e cambia testi, titolo, data, didascalia; varia le pose e le inquadrature).
4. bash sitcom/monta.sh sitcom/episodi/epNN.json  (crea epNN.mp4). Controlla 4 fotogrammi con Read
   (ffmpeg -ss 14 / 20 / 26 / 34 -i video -frames:v 1 f.jpg): fumetti leggibili, interi, sopra l'immagine.
5. git add sitcom/episodi && commit (stesso utente git indicato in tools/TASK.md) && push su main.
   URL: https://raw.githubusercontent.com/marconicreation/bronco-media/main/sitcom/episodi/epNN.mp4 — verifica con curl -sI che risponda 200.
6. Make data-store-records_replace: dataStoreId 233472, key "puntata", data {"date": D, "v1": URL, "m1": didascalia del json}.
7. Avvisa Robi in italiano, breve: titolo e copione della puntata di domani (le battute), così se qualcosa non gli piace lo dice in tempo.

## REGOLE (scelte di Robi, da rispettare sempre)
- Personaggi: BARTOLOMEO (vecchio cavallo inventore sognatore, fan di Bronco, storpia le parole), GEREMIA (vecchio scimpanzé arrabbiato e tirchio,
  occhialini tondi, urla "ORO!"), BRONCO (bulldog barista, chiude con calma e ironia). Paese inventato: Kavod.
- Schema: i tre al bancone (trio_bancone) -> Bartolomeo presenta o storpia un'invenzione (3-4 inquadrature) -> Geremia esplode ->
  battuta finale di Bartolomeo (senza "Sciabadù") -> scena SEPARATA con solo "Sciabadù!" su bartolomeo_sciabadu.jpg, inquadratura unica fissa ->
  reazione muta di Geremia ("...") -> battuta di Bronco. "Vai col tango!" lo aggiunge da solo sitcom.py nella scena finale: MAI scriverlo nelle battute.
- Più inquadrature per battuta (campo intero, primo piano con "box", dettaglio, controcampo). Box utili: vedi le puntate esistenti.
- Fumetti: niente nomi dei personaggi, testo breve (max ~90 caratteri), statici. Niente voci. Musica = quella della sigla (automatica).
- Satira sottile su tasse, bollette, prezzi, burocrazia, caro vita: MAI nomi di persone o partiti, niente cifre precise, niente fatti inventati,
  niente riferimenti a persone o luoghi di La Spezia e provincia. Niente tratti o cognomi che richiamino stereotipi etnici o religiosi:
  Geremia è tirchio e brontolone, MAI usuraio, mai "prestiti", mai banchieri.
- Non ripetere un'invenzione già usata (guarda i titoli delle puntate esistenti).
- Pose disponibili in sitcom/pose/ (non generarne di nuove: il limite IA di Canva è finito fino all'11/12).
- Didascalia: "AL BANCONE DI BRONCO 🍸 Episodio N: Titolo" + 1-2 frasi + riga sulla puntata quotidiana + riga regalo di Natale (fino al 24/12) + hashtag.
