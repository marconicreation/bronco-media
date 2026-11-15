# Link con contatore di clic (dal 15/11/2026)

Redirect su Vercel (team OSPITO, progetto `bronco-link`, dominio `marconicreation.vercel.app`).
Ogni clic vero (i bot di anteprima di Facebook/WhatsApp ecc. sono esclusi) viene salvato nel Blob store `bronco-clic`, poi la persona va alla pagina giusta.

| Link | Porta a |
|---|---|
| https://marconicreation.vercel.app/regalo | pagina del regalo "Il cocktail col tuo nome" |
| https://marconicreation.vercel.app/etsy | negozio Etsy marconicreation |

Aggiungi `?da=xxx` per sapere da dove arriva il clic:
- `?da=bio` → bio Instagram
- `?da=fb` → didascalia del Reel FB delle 19:00 (routine 3 post FB)
- `?da=sitcom` → didascalia della puntata delle 13:00
- `?da=metricool` → Reel IG+FB via Metricool

**Numeri**: https://marconicreation.vercel.app/numeri (totale, per giorno, per provenienza). I clic con `?da=test` non sono contati.

Deploy: i file in questa cartella (`api/`, `lib/`, `vercel.json`, `package.json`) caricati con lo strumento Vercel `create_deployment` (progetto `prj_gMpQ6EAtZNe5b7LkMXttfnFwU5Kp`, target production).
Per aggiungere un link nuovo: aggiungilo in `lib/links.js` e una riga in `vercel.json`.
