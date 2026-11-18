import { put } from "@vercel/blob";

// Conta gli eventi dell'app "Chiedi a Bronco": /api/conta?e=apri|cocktail|condividi&da=...
const BOT = /bot|crawl|spider|facebookexternalhit|facebookcatalog|meta-externalagent|preview|slurp|whatsapp|telegram|discord|skype|curl|wget|python|headless/i;
const EVENTI = new Set(["apri", "cocktail", "condividi"]);

export default async function handler(req, res) {
  const e = EVENTI.has(String(req.query.e)) ? String(req.query.e) : null;
  const da = String(req.query.da || "altro").replace(/[^a-z0-9_-]/gi, "").slice(0, 20) || "altro";
  const ua = req.headers["user-agent"] || "";
  if (e && !BOT.test(ua)) {
    const day = new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Rome" });
    try {
      await put(`clic/app_${e}/${day}/${da}.txt`, ua.slice(0, 200) || "-", {
        access: "private", addRandomSuffix: true, contentType: "text/plain",
      });
    } catch (err) { console.error("conteggio fallito", err?.message); }
  }
  res.setHeader("Cache-Control", "no-store");
  res.status(204).end();
}
