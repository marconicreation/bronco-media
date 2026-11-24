# Sitcom "Al bancone di Bronco": una puntata al giorno (Robi, 13/11/2026)

Ogni giorno alle 13:00 (Europe/Rome) lo scenario Make "Puntata sitcom 13:00" pubblica la puntata del giorno come REEL su
Instagram @marconicreation e sulla pagina Facebook MarconiCreation (Portovenere), leggendo la cassetta di Make
(data store 233472, key "puntata": date = AAAA-MM-GG, v1 = URL del video, m1 = didascalia). Metricool NON si usa (limite 20 post/mese).


> AGGIORNAMENTO 20/11/2026 (Robi: "voci ogni giorno"): se il messaggio della routine dice "montala con bash sitcom/monta.sh",
> è il testo vecchio. Vale il punto 4 qui sotto: pupazzi di plastilina + voci ElevenLabs con sitcom/ritagli/episodio_pupazzi.py.

## Routine serale (prepara la puntata di DOMANI)
1. add_repo marconicreation/bronco-media (push), git clone, cd bronco-media. D = data di DOMANI (Europe/Rome).
2. Cerca in sitcom/episodi/ un epNN.json con "data" = D. Se c'è ed esiste epNN.mp4, vai al punto 6.
3. Se non c'è: scrivi la puntata nuova (numero = ultimo + 1) seguendo le REGOLE qui sotto e lo stesso schema JSON delle puntate esistenti
   (copia la struttura di un epNN.json recente e cambia testi, titolo, data, didascalia; varia le pose e le inquadrature).
4. PUPAZZI CON LE VOCI (Robi 20/11: "voci ogni giorno"). Dal 21/11 sera le puntate si montano con i pupazzi di plastilina,
   le scritte stile TikTok e le tre voci fisse (NON più con monta.sh, che resta solo di riserva):
   VELOCE (Robi 24/11 "Vai"): dal 25/11 OGNI puntata si monta con --veloce, sia in a) sia in c): niente inquadratura dei tre
   (trio_bancone viene saltato), voci +18% più svelte senza pause interne, ogni scena dura quanto la voce + 0,3 s.
   ATTENZIONE: con --veloce i numeri dei file cambiano (il trio non conta), quindi usa SEMPRE --veloce anche in a).
   a) python3 sitcom/ritagli/episodio_pupazzi.py --battute --veloce sitcom/episodi/epNN.json
      stampa le battute da registrare: nome file, personaggio, voice_id, testo ("Sciabadù!" è già registrato; "Vai col tango!" esce nella lista finché non c'è il file della voce nuova di Bronco).
      Voce di Bronco dal 24/11 sera (Robi): "Bronco cagnolone" xHMnzwnNGu6rNUfNTXmY (voce profonda e simpatica, non leccaculo, parla con qualche parola romana).
      "Vai col tango!" con questa voce è già in sitcom/ritagli/voci_fisse/bronco_vai_col_tango_xHMnzwnNGu6rNUfNTXmY.mp3 (non si paga più).
   b) Per ogni riga: ElevenLabs creative_generate_speech con model_id "eleven_v3", quel voice_id, generations_count 1,
      prompt = "[tono in inglese] testo" (es. "[angry, shouting] ...", "[dreamy, excited] ...", "[dry, deadpan] ...").
      UNA chiamata per battuta, mai ripetere (ogni chiamata costa crediti). Aspetta con creative_get_flow_run_status
      e scarica l'mp3 dall'url del risultato: curl -sL -o /tmp/voci_epNN/NN.mp3 "URL". Le voci NON vanno nel repo.
      Costo atteso: circa 400-500 crediti a puntata. Budget ElevenLabs (Robi sì 22/11): tutti i 38.777 crediti del piano Starter al mese
      (reset il 20 del mese), cioè circa 850 al giorno per tutto. Se una puntata supererebbe 600 crediti, accorcia le battute.
   c) python3 sitcom/ritagli/episodio_pupazzi.py --veloce sitcom/episodi/epNN.json sitcom/episodi/epNN.mp4 /tmp/voci_epNN   (circa 8-11 minuti)
      (prima: pip install opencv-python-headless)
      Se manca una voce lo script lo scrive (ATTENZIONE: mancano...): quella scena esce muta, avvisa Robi.
   d) Controlla 4 fotogrammi con Read (ffmpeg -ss 1 / 10 / 20 / 30 -i video -frames:v 1 f.jpg) e il volume
      (ffmpeg -i video -af volumedetect -f null - : mean_volume intorno a -17 dB, mai -91 = muto).
   Effetti comici e risate finte (Robi 20/11) li mette lo script da solo dalla libreria sitcom/ritagli/effetti/ (gratis, niente da generare):
   swoosh sugli stacchi, boing sull'invenzione, colpo quando Geremia urla, cassa sui soldi, grilli sul "...", risate dopo Sciabadù, Bronco e Vai col tango.
   e) Se ElevenLabs non è disponibile nella sessione o le voci falliscono: monta la puntata con i pupazzi SENZA voci
      (stesso comando con --veloce, senza l'ultima cartella), pubblicala lo stesso e avvisa Robi.
   Nel json "voci": true. Le pose ("img") servono solo per capire chi parla (bronco_/geremia_/bartolomeo_...) o il campo "chi";
   trio_bancone = inquadratura dei tre; "..." = reazione muta; "saga" e "avvento" funzionano come prima (cartello finale e bollino).
4b. Reel di prova (vedi CAMPAGNA), stesse voci: python3 sitcom/ritagli/episodio_pupazzi.py --veloce --prova sitcom/episodi/epNN.json sitcom/episodi/epNN_prova.mp4 /tmp/voci_epNN
   (~25 s: apre con la battuta di Geremia, senza trio, cartelli e sigla). Controlla 1 fotogramma. (prova.sh resta solo per le puntate vecchie.)
5. git add sitcom/episodi && commit (stesso utente git indicato in tools/TASK.md) && push su main.
   URL: https://raw.githubusercontent.com/marconicreation/bronco-media/main/sitcom/episodi/epNN.mp4 — verifica con curl -sI che risponda 200.
6. Make data-store-records_replace: dataStoreId 233472, key "puntata", data {"date": D, "v1": URL, "m1": didascalia del json}.
7. Avvisa Robi in italiano, breve: titolo e copione della puntata di domani (le battute), così se qualcosa non gli piace lo dice in tempo.
8. ATTRAZIONI (tools/CRESCITA.md, sezione ATTRAZIONI): i commenti Instagram li risponde DA SOLO Bronco (Make 8704211, dal 20/11): NON lanciare 8663341/8663345. Nella puntata
   applica gioco della settimana (lunedì/giovedì), notizia del giorno e "tipo_aggancio" a rotazione.

## MODELLO EP. 8 / EP. 9 (Robi sì 22/11, dal bilancio della settimana)
Le due puntate che hanno funzionato di più: Ep. 8 "Il termosifone a pedali" (973 view su Facebook, record) e
Ep. 9 "La calcolatrice ottimista" (114 view su Instagram, record). Da ora ogni puntata segue la loro ricetta:
- Al centro c'è UN'INVENZIONE ASSURDA di Bartolomeo contro un fastidio di tutti i giorni (bollette, fisco, prezzi, burocrazia, caro vita).
- La PRIMA RIGA della didascalia e l'"aggancio" dicono l'invenzione in modo concreto e buffo, con 1-2 emoji
  (es. "Il termosifone a pedali: il caldo te lo fai da solo 🚴‍♂️🔥", "Una calcolatrice che fa lo sconto? Geremia la vuole SUBITO 🧮").
- La battuta forte arriva SUBITO (Geremia che vuole approfittarne o che esplode), poi il colpo di scena sull'invenzione che si rivolta contro.
- Nelle mini-saghe ogni parte deve avere la sua invenzione o il suo pezzo di invenzione assurda, non solo la trama.
- Regole di sempre: niente nomi di persone o partiti, niente cifre precise, niente fatti inventati.

## NUOVO FORMATO dal 18/11 (Robi: "innovare tutto"): BATTUTA SUBITO + MINI-SAGA + REGALO
Motivo: su FB ogni Reel fa ~200 view ma la gente guarda 1-3 s; su IG il 67-93% scorre via nei primi 3 s.
- Ogni epNN.json ha "aggancio": la battuta più forte (di solito Geremia che esplode), max ~45 caratteri, 2,5 s, primo piano con "box".
  Esempio: {"img": "pose/geremia_strilla.jpg", "chi": "GEREMIA", "testo": "ZERO GUSTO! Come la mia pensione!", "durata": 2.5, "inq": [{"box": [0.15,0.0,0.9,0.75]}]}
  Con "aggancio": niente cartello iniziale, titolo piccolo in alto su ogni scena, la SIGLA VA IN CODA (monta.sh lo fa da solo).
  La prima scena (trio_bancone) dura 1,0 s.
- (Fino al 19/11 la puntata chiudeva con regalo/tazza. Dal 20/11 NON PIÙ: vedi RITMO qui sotto.)
  Nei giorni dispari la riga regalo della didascalia diventa: "☕ Regala la tazza di NOME: 19,90 € con spedizione gratis, ordina entro il 6/12 per averla a Natale 👉 https://marconicreation.vercel.app/etsy?da=sitcom (link anche in bio)".
  (Invito più chiaro, Robi sì 24/11. Dal 7/12 togli la frase "ordina entro il 6/12" e nei giorni dispari usa la riga del regalo cocktail.)
- MINI-SAGA: dal 22/11 le puntate sono storie di 5 parti. Nel json: "saga": {"titolo": "...", "parte": N, "di": 5}.
  sitcom.py mette "PARTE N/5" in alto e il cartello "CONTINUA... domani alle 13" (o "FINE" all'ultima parte).
  Ogni parte deve finire con una domanda aperta (cosa succederà?), e avere comunque una battuta che fa ridere da sola.
  Didascalia: "AL BANCONE DI BRONCO 🍸 Ep. N · Titolo saga (parte X di 5)" + 1 frase che riassume la parte prima + riga regalo + hashtag.
- SAGA 1 (22-26/11) "Il grande concorso di Kavod":
  1) Al paese c'è il concorso degli inventori, premio una botte di vermut. Bartolomeo si iscrive. Geremia: "Il premio è MIO!".
  2) Geremia si offre come socio di Bartolomeo... al 90%. Bartolomeo accetta perché "non sa contare oltre il 50".
  3) Il prototipo: la macchina che prepara i cocktail da sola. Li prepara al contrario (prima il bicchiere rotto, poi il ghiaccio sciolto).
  4) Geremia prova a presentare l'invenzione da solo. La giuria gli chiede la tassa d'iscrizione: lui sviene.
  5) Il verdetto: vince... il Broncospasmo di Bronco, che non era nemmeno in gara. Il premio va diviso fra tutti al bancone. Sciabadù.
  Poi SAGA 2: proponila tu a Robi nel messaggio serale dell'ultima parte (2 idee, lui sceglie).

## RITMO E MUSICA dal 20/11 (Robi 19/11: "a tempo con la musica, ogni due battute per fotogramma", niente sgranature, musica meno ritmata)
- Musica (Robi 19/11 sera): "Torso Stufo", la canzone di Robi (sitcom/musica/torso_stufo.m4a, sua, niente diritti), 110 bpm, 1 battuta = 2,18 s,
  presa dalla battuta 14 (30,55 s) dove è già piena. Suona continua sotto puntata + sigla (monta.sh lo fa da solo). Parametri in sitcom/musica/canzone.py.
  La base sintetica sitcom/lounge.py resta solo di riserva (SITCOM_MUSICA=lounge).
- Ogni epNN.json ha "ritmo": true (automatico dalla data 2026-11-20). Le durate NON si scrivono in secondi ma in battute:
  "battute": 2 (4,4 s) per ogni inquadratura con una battuta di dialogo; "battute": 1 (2,2 s) solo per trio_bancone, "Sciabadù!" e la reazione muta "...".
  Una battuta di dialogo = UNA inquadratura (niente liste "inq" con 3-4 tagli). Aggancio = 2 battute. Totale puntata ~33 s + sigla 11 s (la canzone dura 74 s dal punto di partenza: la puntata intera deve restare sotto i 70 s).
- Niente zoom: sitcom.py ritaglia la posa originale senza mai ingrandirla (lato minimo 1080 px veri su 1264): un "box" stretto viene allargato da solo.
  Meglio usare le pose intere. Le pose MORBIDE (geremia_dito, bronco_shaker, bartolomeo_quaderno) evitale proprio finché non sono rifatte con Canva (dall'11/12).
- Niente tazza né regalo in fondo al video: la puntata chiude con "Vai col tango!", poi "CONTINUA..." (saga) o "DOMANI ALLE 13", poi la sigla.
  La didascalia può tenere la riga con il link (regalo o tazza come prima).
- Esempi da copiare: sitcom/episodi/ep08.json e ep09.json.

## DOMANDA SECCA DI BRONCO IN CHIUSURA (Robi sì 24/11, dal bilancio della settimana)
Su Instagram zero condivisioni, salvati e commenti: da ora OGNI puntata chiude con Bronco che fa UNA domanda secca al pubblico, a voce.
- È l'ULTIMA battuta di Bronco (quella prima di "Vai col tango!"): la domanda PRENDE IL POSTO della sua battuta finale, non si aggiunge.
  Così le battute restano le stesse di numero e i crediti ElevenLabs non salgono.
- Corta (max ~6 secondi di parlato), in romanesco leggero, guardando il pubblico, e legata all'invenzione della puntata.
  Deve avere una risposta facile da scrivere in una parola o una riga. Esempi:
  "E tu, er termosifone a pedali lo compreresti? Scrivilo sotto!" · "Che ce mettevi te ner bicchiere? Dimmelo nei commenti!" ·
  "Chi c'ha ragione, Geremia o Bartolomeo? Scrivi er nome!" · "A te te serve? Sì o no, scrivilo!"
  Varia la formula ogni giorno (mai la stessa due giorni di fila). Mai "tagga" o "metti like se" (tools/CRESCITA.md), mai chiedere follow nella domanda.
- La STESSA domanda va nella didascalia come "domanda vera al pubblico" (vedi DIDASCALIA PER CRESCERE), così chi legge e chi ascolta risponde alla stessa cosa.
- Nel copione da mandare a Robi (punto 7) scrivi la domanda finale in evidenza.
- Bronco risponde ai commenti da solo (Make 8704211): niente da cambiare lì.

## SPOT DELLE TAZZE (Robi 19/11): Reel separati di 10 s, non dentro le puntate
- python3 sitcom/spot.py GEREMIA|BARTOLOMEO|BRONCO -> sitcom/spot/spot_NOME.mp4 (frase del personaggio, foto della tazza, prezzo, "su Etsy, link in bio").
- Pubblicazione: vedi la memoria del progetto (calendario e orario da confermare con Robi prima di attivarli).

## CALENDARIO DELL'AVVENTO DI BRONCO (Robi sì 18/11): dal 1/12 al 24/12
- Ogni puntata di dicembre è una casella: nel json "avvento": N (N = giorno di dicembre) e il titolo comincia con "🎄 -K a Natale" (K = 25 - N).
  sitcom.py disegna da solo il bollino rosso "-K A NATALE" (il 24/12 "VIGILIA!") in alto a destra sull'immagine: basta il campo "avvento".
  Didascalia, prima riga: "🎄 Casella N del calendario dell'Avvento di Bronco: -K a Natale!" poi la battuta.
  Invito a tornare in ogni puntata: "Domani alle 13 si apre la casella N+1".
- Saghe di dicembre (5 parti ciascuna): 2-6/12, 7-11/12, 12-16/12, 17-21/12; poi 22-24/12 il FINALE DI NATALE in 3 parti
  ("Il Natale al bancone"): tutti al bancone, Geremia non vuole fare regali, Bronco gli inventa "il cocktail col suo nome" e Geremia si commuove
  (una sola volta, poi torna brontolone). Il 24/12 la puntata chiude: "Hai ancora tempo: il cocktail col tuo nome arriva per email in poche ore".
- Una saga a dicembre è sui regali sbagliati (Bartolomeo inventa il regalo perfetto per chi ha tutto), una sul cenone (prezzi, parenti, avanzi).
- Le saghe di dicembre le proponi a Robi 2 alla volta nel messaggio serale dell'ultima parte, come per la saga 2.

## CAMPAGNA "NATALE AL BANCONE" (Robi sì 20/11, solo mosse gratuite: niente pubblicità)
Piano: https://claude.ai/artifact/8myW2xrNwV9LwKERX8T81E
1. REEL DI PROVA (Instagram "Trial Reel", lo vede solo chi NON ci segue): ogni giorno alle 17:41 lo pubblica lo scheduled task
   "Bronco: Reel di prova 18:00" con il connettore Windsor (non serve nulla dalla routine serale). Versione corta della puntata del giorno:
   episodio_pupazzi.py --prova (punto 4b) -> epNN_prova.mp4 (~25 s, apre con un'altra battuta, senza trio, senza saga, senza sigla).
   La routine serale, dopo aver montato la puntata, monta ANCHE epNN_prova.mp4 e lo mette nel commit (così alle 17:41 è già pronto).
2. REEL DA MANDARE A UN AMICO: almeno 2 puntate a settimana su situazioni che tutti conoscono (l'amico brontolone, quello con le idee assurde,
   il caffè al bar, le bollette, i regali di Natale, il cenone, i parenti). Nella didascalia, 2-3 volte a settimana, una domanda che fa venire
   in mente qualcuno: "Anche tu hai un amico come Geremia? 😂". Mai "tagga", "manda a 3 amici", "metti like se" (Instagram li penalizza).
3. ARCO DI NATALE nelle didascalie: fino al 6/12 la riga del link è la TAZZA ("ultimi giorni per riceverla a Natale" dal 28/11);
   dal 7/12 al 24/12 è il REGALO "il cocktail col tuo nome: arriva per email, va bene anche all'ultimo minuto".
   27/11 puntata speciale "Black Friday al bancone" (Geremia vuole lo sconto sul caffè; satira generica, niente marchi né cifre).
4. VOCI: dal 22/11 tutte le puntate hanno le voci fisse (punto 4 della routine serale).

## REGOLE (scelte di Robi, da rispettare sempre)
- Personaggi: BARTOLOMEO (vecchio cavallo inventore sognatore, fan di Bronco, storpia le parole), GEREMIA (vecchio scimpanzé arrabbiato e tirchio,
  occhialini tondi, urla "ORO!"), BRONCO (bulldog barista, chiude con calma e ironia). Paese inventato: Kavod.
- Schema: AGGANCIO (battuta forte, 2,5 s) -> i tre al bancone (trio_bancone, 1 s) -> Bartolomeo presenta o storpia un'invenzione (3-4 inquadrature) -> Geremia esplode ->
  battuta finale di Bartolomeo (senza "Sciabadù") -> scena SEPARATA con solo "Sciabadù!" su bartolomeo_sciabadu.jpg, inquadratura unica fissa ->
  reazione muta di Geremia ("...") -> battuta di Bronco = DOMANDA SECCA al pubblico (dal 24/11, vedi sopra). "Vai col tango!" lo aggiunge da solo sitcom.py nella scena finale: MAI scriverlo nelle battute.
- Dal 20/11 una inquadratura per battuta di dialogo, lunga 2 battute di musica (vedi RITMO). Varia le pose da una battuta all'altra.
- Scritte: niente nomi dei personaggi, testo breve (max ~90 caratteri). Dal 21/11 voci fisse ElevenLabs (vedi punto 4) e scritte stile TikTok. Musica = Torso Stufo (automatica).
- Battute dette ad alta voce: scrivile come si parlano (niente sigle o simboli strani; i numeri in lettere se brevi), max ~8 secondi di parlato a battuta.
- Satira sottile su tasse, bollette, prezzi, burocrazia, caro vita: MAI nomi di persone o partiti, niente cifre precise, niente fatti inventati,
  niente riferimenti a persone o luoghi di La Spezia e provincia. Niente tratti o cognomi che richiamino stereotipi etnici o religiosi:
  Geremia è tirchio e brontolone, MAI usuraio, mai "prestiti", mai banchieri.
- Non ripetere un'invenzione già usata (guarda i titoli delle puntate esistenti).
- QUALITÀ (Robi 18/11): ogni posa ha la copia 2x in sitcom/pose/hd/ (sitcom.py la usa da sola). Se aggiungi una posa nuova: python3 tools/hd.py sitcom/pose/NOME.jpg.
  Le pose nate sfocate (MORBIDE in sitcom.py: geremia_dito, bronco_shaker, bronco_finale_tango, bartolomeo_quaderno) non vanno in primo piano stretto.
- Pose disponibili in sitcom/pose/ (non generarne di nuove: il limite IA di Canva è finito fino all'11/12).
- Didascalia: "AL BANCONE DI BRONCO 🍸 Episodio N: Titolo" + 1-2 frasi + riga sulla puntata quotidiana + riga regalo di Natale (fino al 24/12), SEMPRE con il link contaclic:
  "🎁 Regala un cocktail inventato col nome di chi vuoi: 5 €, arriva per email in 24 ore 👉 https://marconicreation.vercel.app/regalo?da=sitcom (link anche in bio)" + hashtag.
  (Invito più chiaro, Robi sì 24/11: cosa ricevi, prezzo e tempi nella stessa riga.)
  Mai il link claude.ai/artifact diretto (vedi link/README.md).
- DIDASCALIA PER CRESCERE (Robi 18/11): segui tools/CRESCITA.md. Prima riga = la battuta dell'aggancio (non il titolo),
  poi la riga "AL BANCONE DI BRONCO", una domanda vera al pubblico, "Segui @marconicreation: la puntata di domani esce alle 13", regalo, 5-7 hashtag a rotazione.
