import { put } from "@vercel/blob";
import { LINKS } from "../lib/links.js";

const BOT = /bot|crawl|spider|facebookexternalhit|facebookcatalog|meta-externalagent|preview|slurp|whatsapp|telegram|discord|skype|curl|wget|python|headless/i;

export default async function handler(req, res) {
  const d = LINKS[req.query.d] ? String(req.query.d) : "regalo";
  const target = LINKS[d];
  const da = String(req.query.da || "altro").replace(/[^a-z0-9_-]/gi, "").slice(0, 20) || "altro";
  const ua = req.headers["user-agent"] || "";
  if (!BOT.test(ua) && req.method === "GET") {
    const day = new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Rome" });
    try {
      await put(`clic/${d}/${day}/${da}.txt`, ua.slice(0, 200) || "-", {
        access: "private", addRandomSuffix: true, contentType: "text/plain",
      });
    } catch (e) { console.error("conteggio fallito", e?.message); }
  }
  res.setHeader("Cache-Control", "no-store");
  res.redirect(302, target);
}
