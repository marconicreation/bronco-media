# Storie Instagram di Bronco (approvate da Robi il 20/11/2026)

Tre storie al giorno su Instagram (@marconicreation, account Windsor `17841474213412207`),
pubblicate in automatico da tre attività programmate: 13:10, 18:20, 21:00 (Europe/Rome).
Costo zero: niente crediti Make, niente ElevenLabs. Valgono anche dall'11 al 24/12 quando Robi è via.

Regole fisse:
- Leggi prima `CLAUDE.md`. Scritte SEMPRE in Pricedown col contorno nero: usa solo `tools/storia.py`.
- Instagram non permette da programma sondaggi, domande o link cliccabili: scrivi "Rispondi a questa storia"
  o "link in bio" nel testo. Mai inventare recensioni, finte urgenze o numeri di vendita.
- Satira: niente persone, partiti, cifre precise o fatti inventati. Niente La Spezia.
- Le storie di Facebook non si possono pubblicare (né Make né Windsor): non provarci in altri modi.
- Una sola pubblicazione per storia. Se Windsor dà errore riprova UNA volta, poi fermati e avvisa Robi.

## Come si pubblica
1. Crea il file con `tools/storia.py` (card = immagine JPEG, clip = video MP4).
2. Copialo in `storie/AAAA-MM-GG_ORA.jpg` (o `.mp4`), commit e push su `main`.
3. Verifica con `curl -sI` che `https://raw.githubusercontent.com/marconicreation/bronco-media/main/storie/...` risponda 200.
4. Windsor `execute_action`: connector `instagram`, account `17841474213412207`, action `create_story`,
   parametri `{"image_url": URL}` oppure `{"video_url": URL}` (video 3-60 s, max 100 MB).

## 13:10 · Pezzo della puntata
- Puntata di oggi: il record `puntata` nel data store Make 233472 (campo `date` = oggi, `v1` = URL del video),
  oppure il file `sitcom/episodi/epNN.mp4` la cui data di uscita è oggi (vedi `sitcom/TASK_SITCOM.md`).
- `python3 tools/storia.py clip PUNTATA.mp4 OUT.mp4 "Nuova puntata!" "Guardala tutta sul profilo"`
  (il titolo può cambiare: "Puntata N!", "Parte 2 della saga!", ecc.).
- Se oggi non c'è la puntata, pubblica una card con una posa da `sitcom/pose/hd/` e "Domani alle 13 nuova puntata".

## 18:20 · Conto alla rovescia
- Titolo: "Mancano X giorni a Natale" (X = giorni dal giorno dopo fino al 25/12; il 24/12 "Domani è Natale!", il 25/12 "Buon Natale dal bancone!"). Dopo il 25/12 questa storia diventa "Dal bancone" come quella delle 21.
- Giorni pari: la tazza a rotazione (Bronco, Bartolomeo, Geremia) con foto da `gadget/tazze_v2/*_foto.jpg`,
  righe "La tazza di NOME: FRASE" e, fino al 6/12, "Ordina entro il 6/12 per Natale · link in bio" (dopo il 6/12: "Su Etsy · link in bio").
- Giorni dispari: il regalo da 5 € "Il cocktail col tuo nome", sfondo `tools/regalo_esempio.jpg`, righe tipo
  "Bronco inventa un cocktail col nome di chi vuoi" e "5 € · arriva per email · link in bio".
- Nei giorni dello spot serio (record `spot-AAAA-MM-GG` nel data store 233472): "Lo spot di NOME è uscito" + "Guardalo sul profilo".

## 21:00 · Dal bancone
- Card con una posa da `sitcom/pose/hd/` (mai la stessa due sere di fila: guarda gli ultimi file in `storie/`).
- Titolo "Dal bancone" (o una battuta breve di un personaggio), poi UNA domanda legata alla puntata di domani o alla saga in corso
  (es. "Bartolomeo deve vincere il concorso?", "Geremia ha ragione?") e la riga "Rispondi a questa storia".
- Non svelare la battuta finale della puntata di domani.

## Fine
Risposta finale breve in italiano: quale storia è uscita (o cosa è andato storto). Le risposte alle storie le legge il briefing delle 8:52.
