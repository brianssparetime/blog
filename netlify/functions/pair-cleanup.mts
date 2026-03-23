import { getStore } from "@netlify/blobs";
import type { Config } from "@netlify/functions";

const MAX_AGE_MS = 24 * 60 * 60 * 1000; // 24 hours

export default async () => {
  try {
    const store = getStore("bfr-pairing");
    const { blobs } = await store.list();

    let deleted = 0;
    for (const blob of blobs) {
      let entry;
      try {
        entry = await store.get(blob.key, { type: "json" });
      } catch (e) {
        continue;
      }
      if (entry && entry.timestamp && Date.now() - entry.timestamp > MAX_AGE_MS) {
        try { await store.delete(blob.key); } catch (e) { continue; }
        deleted++;
      }
    }

    return new Response(JSON.stringify({ deleted, checked: blobs.length }), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: "cleanup failed: " + e.message }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    });
  }
};

export const config: Config = {
  schedule: "@daily",
};
