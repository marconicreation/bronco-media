# 3 Reel Facebook al giorno (preparati alle 20:07 per DOMANI, Europe/Rome)
Dal 13/11/2026 Robi vuole SOLO Reel: i 3 post Facebook del giorno sono 3 video Reel.
Make li pubblica da solo: scenario "Reel FB 10:00" (v1/m1), "Reel FB 13:00" (v3/m3), "Reel FB 18:00" (v2/m2),
leggendo la cassetta (data store 233472, key "next"). Se un video manca, lo scenario delle 22:30 pubblica il testo come post normale (riserva).

DIDASCALIE m1/m2: segui SEMPRE tools/CRESCITA.md (prima riga forte, una domanda al pubblico, 5-7 hashtag a rotazione).
(Nota 18/11: lo scenario delle 13:00 è spento, il Reel 3 non esce.)
SABATO SERA (cioè D = domenica): il Reel 2 delle 18:00 è "IL MEGLIO DELLA SETTIMANA" fatto con tools/meglio.sh (vedi tools/CRESCITA.md, ATTRAZIONI punto 5) invece del Reel regalo.

Passi (dopo aver scritto m1, m2, m3 e la citazione come da istruzioni della routine):
1. Repo: add_repo marconicreation/bronco-media (push), git clone, cd bronco-media. D = data di DOMANI (AAAA-MM-GG).
2. Reel 1 (mattina, battuta): scegli una posa da pose/nuove o pose/usate diversa da quelle degli ultimi giorni (guarda promo/fb/).
   b1 = la battuta del mattino in versione corta (max ~70 caratteri), MAI partiti o persone, niente cifre precise, niente fatti inventati.
   python3 tools/reel.py pose/.../P.jpg pose/.../P.jpg promo/fb/D_1.mp4 --hook "b1" --cta regalo
   (Robi 18/11: fino al 24/12 OGNI Reel chiude sul regalo; in m1 aggiungi in fondo la riga
   "🎁 Il cocktail col tuo nome: regalo di Natale a 5 € 👉 https://marconicreation.vercel.app/regalo?da=fb". Dal 25/12 torna --cta segui.)
   (stesso file due volte = niente fumetto: la battuta sta in alto, mai sopra il muso di Bronco.)
3. Reel 3 (13:00, citazione): dopo tools/quote.py citazioni/D.jpg ...:
   python3 tools/reel.py citazioni/D.jpg citazioni/D.jpg promo/fb/D_3.mp4 --hook "frase corta che lega la citazione all'attualità (max ~50 caratteri)" --tag "LA FRASE DEL GIORNO" --cta segui
4. Reel 2 (18:00, regalo di Natale fino al 24/12): posa a tema (shaker, natale, festa, bicchiere, negroni, spritz, tramonto_vino).
   python3 tools/reel.py pose/.../P.jpg pose/.../P.jpg promo/fb/D_2.mp4 --hook "aggancio della sera, max ~70 caratteri (es. IL PAPÀ CHE NON BEVE? BRONCO GLI INVENTA UN COCKTAIL COL SUO NOME)" --tag "REGALO DI NATALE · 5 €" --cta regalo
   Dopo il 24/12: un Reel con consiglio/battuta dal bancone e --cta segui.
   PROVA 23-29/11 (misura del 22/11: i Reel solo-vendita della sera fanno ~120 view, le battute ~220-970): il Reel delle 18:00 apre con una
   BATTUTA su caro vita/bollette/prezzi (non con l'offerta) nel --hook, il regalo resta solo nella chiusura (--cta regalo) e nell'ultima riga della didascalia.
   Didascalia: prima riga = la battuta, poi una domanda al pubblico, poi la riga regalo. La domenica 29/11 si confrontano le view.
5. Guarda con Read un fotogramma a 3 s di ogni video (ffmpeg -ss 3 -i X.mp4 -frames:v 1 X.jpg): testo leggibile e dentro lo schermo.
6. git add promo/fb citazioni && commit (user marconicreation / rmarconi79@gmail.com) && push su main.
   URL: https://raw.githubusercontent.com/marconicreation/bronco-media/main/promo/fb/D_1.mp4 (e _2, _3). Verifica con curl -sI che rispondano 200.
7. Nella cassetta (data-store-records_replace, dataStoreId 233472, key "next") aggiungi ai campi soliti: "v1", "v2", "v3" = gli URL dei video.
   Se un video non è riuscito, NON mettere il suo campo: il testo uscirà come post normale.
