# Far crescere la pagina (Robi, 18/11/2026): regole per OGNI didascalia e OGNI Reel

Obiettivo di Robi: oltre a vendere, far crescere visualizzazioni e follower di @marconicreation (IG) e MarconiCreation (FB),
come un vero social media manager. Niente spam, niente follower comprati, niente spesa senza il sì di Robi.

## Orari (Metricool getBestTimeToPost, Facebook, 18/11)
Picchi feriali: 10:00 e 12:00, poi 17-18. Weekend più basso, picco 10:00. Instagram: ancora troppo pochi dati.
Quindi: Reel FB battuta 10:00 (scenario 8552945), puntata sitcom 13:00 IG+FB (8555972), Reel FB regalo 18:00 (8552953).

## Didascalia (vale per sitcom m1 e per i Reel FB m1/m2)
1. PRIMA RIGA = la battuta o la domanda più forte (è l'unica che si vede senza aprire). Mai iniziare col titolo della rubrica.
   Esempio: "Geremia ha trovato il modo di non pagare il caffè 😂" poi sotto "AL BANCONE DI BRONCO 🍸 Ep. 12 ...".
2. UNA domanda vera al pubblico, facile da commentare con una parola o un'emoji (i commenti spingono la distribuzione):
   "Voi da che parte state: Geremia o Bartolomeo? 🐴🐒", "Che invenzione dovrebbe provare Bartolomeo domani? 👇",
   "Anche voi avete un amico come Geremia?". Variala ogni giorno. MAI "tagga 3 amici", "metti like se...", "condividi per..." (Meta li penalizza).
3. Parole chiave scritte per intero (Instagram e Facebook cercano anche nel testo): "cartone animato", "sitcom a puntate",
   "barista", "bar", "cocktail", "vignette divertenti".
4. Invito a seguire concreto: "Segui @marconicreation: la puntata di domani esce alle 13".
5. Riga regalo con link contaclic (fino al 24/12), come già scritto in TASK_SITCOM.md / TASK_FB.md.
6. Hashtag: 5-7, in fondo, a rotazione dalla lista sotto. Sempre #marconicreation. Mai gli stessi 7 due giorni di fila.
   Lista: #vignettedivertenti #umorismoitaliano #cartoneanimato #sitcomitaliana #barista #bartender #cocktail #barlife
   #ridere #battute #animazione #fumetti #reelsitalia #comicità #natale2026 (da dicembre) #regalidinatale (solo Reel regalo)

## Il video (il montaggio lo decide il thread del formato: qui solo promemoria)
- Primo secondo = la cosa più forte. Testo grande in alto leggibile senza audio.
- Cover/anteprima: il primo fotogramma deve far capire chi parla (primo piano), non un cartello.

## Misura (ogni domenica sera)
Metricool brand 7649060: IGEV01/FBEV17 follower, IGEV23/FBEV22 view Reel, IGEV25/FBEV34 interazioni, + /numeri dei link.
Confronta con gli obiettivi della settimana (memoria di progetto "crescita-pagina") e cambia UNA cosa alla volta.

## ATTRAZIONI (Robi 18/11 sera: "inventati qualsiasi attrazione, sentiti libero")
Regole fisse sempre valide: niente spam, niente follower comprati, niente spesa senza il sì di Robi, satira senza nomi/partiti/cifre,
niente La Spezia e provincia, niente concorsi con premi (in Italia servono autorizzazioni): si vince solo l'onore di entrare in puntata.

1. RISPOSTE AI COMMENTI, OGNI SERA (le fa la routine serale della sitcom, passo 8 di sitcom/TASK_SITCOM.md)
   - Make scenario 8663341 "Commenti IG: raccogli" (su richiesta): scrive i commenti nuovi di Instagram nel data store 264473
     (key = id commento; testo, utente, post, quando, stato="nuovo").
   - Leggi i record con stato "nuovo" (data-store-records_list 264473). Per ognuno scrivi una risposta IN PERSONAGGIO, max ~150 caratteri,
     di solito Bronco (calmo, ironico, gentile), a volte Geremia (brontolone) se il commento lo prende in giro. Ringrazia sempre chi scrive.
     Niente link, niente prezzi (se chiedono del regalo: "trovi tutto nel link in bio 🍸"). Spam, insulti, politica: stato="ignorato".
   - data-store-records_update: risposta="...", stato="da_inviare". Poi scenarios_run 8663345 "Commenti IG: rispondi": pubblica e mette stato="inviata".
2. IL GIOCO DELLA SETTIMANA (lunedì -> giovedì)
   - Didascalia della puntata del LUNEDÌ, subito dopo la prima riga: "🎲 GIOCO DELLA SETTIMANA: Bartolomeo cerca il nome per la sua prossima
     invenzione [descrivila in 5 parole]. Scrivetelo nei commenti: il più divertente entra nella puntata di giovedì!"
   - La puntata del GIOVEDÌ usa il nome scelto (fra i commenti del lunedì nel data store 264473; se nessuno ha scritto, lo inventi tu e non citi nessuno)
     e in didascalia: "Nome dell'invenzione suggerito da @utente 🏆". Se la saga in corso non lo permette, mettilo nella battuta di Bronco finale.
3. LA NOTIZIA DEL GIORNO
   - L'aggancio (prima battuta) e la prima riga della didascalia prendono il TEMA del giorno: Black Friday (27/11), primo freddo, bollette, regali,
     cenone, saldi, sciopero dei mezzi, partite della Nazionale... Sempre generico: niente nomi, partiti, cifre o fatti inventati.
4. PROVA DELLE APERTURE (A/B)
   - Nel json di ogni puntata metti "tipo_aggancio": "urlo" (Geremia esplode), "assurdo" (Bartolomeo e l'invenzione) oppure "bronco" (ironia di Bronco).
     Ruotali: mai lo stesso due giorni di fila.
   - La domenica sera (misura settimanale) confronta le view IG/FB delle puntate per tipo e scrivi il risultato in tools/aperture.md.
     Dopo 2 settimane usa di più il tipo che vince (ma almeno 1 volta a settimana gli altri).
5. IL MEGLIO DELLA SETTIMANA (domenica 18:00 su Facebook, al posto del Reel regalo)
   - Lo prepara la routine dei Reel FB il SABATO sera (tools/TASK_FB.md): bash tools/meglio.sh promo/fb/D_2.mp4 promo/fb/<ultimo>_2.mp4 EP EP EP
     con le 3 puntate della settimana con più view (Metricool; se non ci sono dati, le ultime 3). Didascalia: "Il meglio della settimana al bancone 🍸
     Quale battuta vince? 1, 2 o 3? 👇" + riga regalo + hashtag.
6. NATALE (Robi sì 18/11, dettagli in sitcom/TASK_SITCOM.md): "Il calendario dell'Avvento di Bronco" dal 1/12 al 24/12, ogni puntata è una casella ("🎄 -N a Natale")
   e la saga di Natale porta al regalo "Il cocktail col tuo nome".
