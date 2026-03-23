import { getStore } from "@netlify/blobs";

const SECRET = process.env.BFR_PAIR_SECRET || "bfr_7Xm9kP2wQ4nR8vJ5";
const TTL_MS = 60 * 60 * 1000; // 1 hour -- generous for local renewals

export default async (req, context) => {
  const store = getStore("bfr-pairing");

  if (req.method === "POST") {
    const auth = req.headers.get("authorization") || "";
    if (auth !== "Bearer " + SECRET) {
      return new Response(JSON.stringify({ error: "unauthorized" }), {
        status: 403,
        headers: { "Content-Type": "application/json" },
      });
    }

    let body;
    try {
      body = await req.json();
    } catch (e) {
      return new Response(JSON.stringify({ error: "bad request" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    const { code, ip, port, token } = body;
    if (!code || !ip || !port || !token) {
      return new Response(
        JSON.stringify({ error: "missing fields" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    await store.setJSON(code, { ip, port, token, timestamp: Date.now() });

    return new Response(JSON.stringify({ ok: true }), {
      headers: { "Content-Type": "application/json" },
    });
  }

  if (req.method === "GET") {
    const url = new URL(req.url);
    const code = url.searchParams.get("code");
    if (!code) {
      return new Response(
        JSON.stringify({ error: "missing code parameter" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    let entry;
    try {
      entry = await store.get(code, { type: "json" });
    } catch (e) {
      entry = null;
    }

    if (!entry) {
      return new Response(
        JSON.stringify({ error: "Invalid or expired code" }),
        { status: 404, headers: { "Content-Type": "application/json" } }
      );
    }

    if (Date.now() - entry.timestamp > TTL_MS) {
      await store.delete(code);
      return new Response(
        JSON.stringify({ error: "Invalid or expired code" }),
        { status: 404, headers: { "Content-Type": "application/json" } }
      );
    }

    // One-time use: delete after successful lookup
    await store.delete(code);

    return new Response(
      JSON.stringify({ ip: entry.ip, port: entry.port, token: entry.token }),
      { headers: { "Content-Type": "application/json" } }
    );
  }

  return new Response("Method not allowed", { status: 405 });
};
