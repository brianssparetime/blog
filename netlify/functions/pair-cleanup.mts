import { getStore } from "@netlify/blobs";
import type { Config } from "@netlify/functions";

const MAX_AGE_MS = 24 * 60 * 60 * 1000; // 24 hours

export default async () => {
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
      await store.delete(blob.key);
      deleted++;
    }
  }

  return new Response(JSON.stringify({ deleted, checked: blobs.length }), {
    headers: { "Content-Type": "application/json" },
  });
};

export const config: Config = {
  schedule: "@daily",
};
