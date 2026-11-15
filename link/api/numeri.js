import { list } from "@vercel/blob";

export default async function handler(req, res) {
  const tot = {};
  let cursor;
  do {
    const r = await list({ prefix: "clic/", limit: 1000, cursor });
    for (const b of r.blobs) {
      const [, link, day, file] = b.pathname.split("/");
      const da = file.replace(/-[^-]*\.txt$/, "").replace(/\.txt$/, "");
      if (da === "test") continue;
      const L = (tot[link] ??= { totale: 0, per_giorno: {}, per_provenienza: {} });
      L.totale++;
      L.per_giorno[day] = (L.per_giorno[day] || 0) + 1;
      L.per_provenienza[da] = (L.per_provenienza[da] || 0) + 1;
    }
    cursor = r.hasMore ? r.cursor : undefined;
  } while (cursor);
  res.setHeader("Cache-Control", "no-store");
  res.status(200).json({ aggiornato: new Date().toISOString(), clic: tot });
}
