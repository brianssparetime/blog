import { getStore } from "@netlify/blobs";

const SECRET = process.env.BFR_PAIR_SECRET || "bfr_7Xm9kP2wQ4nR8vJ5";
const TTL_MS = 24 * 60 * 60 * 1000; // 24 hours

// Salt for the network hash below. A bare SHA-256 of an IPv4 address is
// not private: the whole space is four billion values and reverses in
// minutes. Salting it means the store holds nothing anyone can turn back
// into a household's public address. Set BFR_IP_SALT in the Netlify env
// and never change it, or every registered clone drops out of the index
// until it next re-registers.
const IP_SALT = process.env.BFR_IP_SALT || "bfr_ip_salt_9Qw3Lz7Kd2Rt";

// Prefix for the second key an entry is written under: where it connects
// from, rather than the digits shown on its TV.
const NET_PREFIX = "net:";

/** Public address this request arrived from. */
function clientIp(req, context) {
  if (context && context.ip) return context.ip;
  const direct = req.headers.get("x-nf-client-connection-ip");
  if (direct) return direct;
  const forwarded = req.headers.get("x-forwarded-for");
  if (forwarded) return forwarded.split(",")[0].trim();
  return "";
}

/**
 * The part of an address a clone and a phone in the same house share.
 *
 * IPv4 behind NAT: every device presents the router's whole address, so
 * the whole address identifies the household.
 *
 * IPv6: there is no NAT, and the clone and the phone hold different global
 * addresses. What they share is the prefix their router was delegated, so
 * the first four hextets are used. A household whose clone registered over
 * one family and whose phone arrives over the other simply misses, and the
 * page falls back to asking for the code.
 */
function networkOf(ip) {
  if (!ip) return "";
  let addr = ip.trim().toLowerCase();
  const zone = addr.indexOf("%");
  if (zone >= 0) addr = addr.slice(0, zone);
  if (addr.startsWith("::ffff:") && addr.includes(".")) {
    addr = addr.slice(7); // IPv4-mapped IPv6, e.g. ::ffff:203.0.113.4
  }
  if (!addr.includes(":")) return addr; // IPv4

  let groups;
  if (addr.includes("::")) {
    const halves = addr.split("::");
    const left = halves[0] ? halves[0].split(":") : [];
    const right = halves[1] ? halves[1].split(":") : [];
    const gap = 8 - left.length - right.length;
    groups = left.concat(new Array(gap > 0 ? gap : 0).fill("0"), right);
  } else {
    groups = addr.split(":");
  }
  return groups
    .slice(0, 4)
    .map((h) => (h || "0").replace(/^0+(?=.)/, ""))
    .join(":");
}

/**
 * Salted hash of the household network, used as a blob key.
 *
 * Returns "" rather than throwing if anything goes wrong. This function
 * is shared by every clone in the field, so a failure here has to cost
 * the codeless shortcut and nothing else -- registration and the code
 * path both carry on without it.
 */
async function networkKey(ip) {
  try {
    const net = networkOf(ip);
    if (!net) return "";
    const data = new TextEncoder().encode(IP_SALT + "|" + net);
    const digest = await crypto.subtle.digest("SHA-256", data);
    const hex = Array.from(new Uint8Array(digest))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
    return NET_PREFIX + hex.slice(0, 32);
  } catch (e) {
    return "";
  }
}

/**
 * Is this an address only reachable from inside a household?
 *
 * A clone always registers the LAN address a phone on the same network
 * dials. Nothing legitimate registers a public one, and allowing it would
 * let anyone holding the shared POST secret point a phone at a host they
 * own. Loopback is refused too: an entry for 127.0.0.1 can never help a
 * phone, so a clone that could not work out its own address is better off
 * seeing the registration fail than showing a code that leads nowhere.
 */
function isPrivateAddress(ip) {
  if (!ip || typeof ip !== "string") return false;
  let addr = ip.trim().toLowerCase();
  const zone = addr.indexOf("%");
  if (zone >= 0) addr = addr.slice(0, zone);
  if (addr.startsWith("::ffff:") && addr.includes(".")) addr = addr.slice(7);

  if (!addr.includes(":")) {
    const parts = addr.split(".");
    if (parts.length !== 4) return false;
    const o = parts.map((p) => (/^\d{1,3}$/.test(p) ? Number(p) : -1));
    if (o.some((n) => n < 0 || n > 255)) return false;
    if (o[0] === 10) return true;                          // 10/8
    if (o[0] === 172 && o[1] >= 16 && o[1] <= 31) return true; // 172.16/12
    if (o[0] === 192 && o[1] === 168) return true;         // 192.168/16
    if (o[0] === 100 && o[1] >= 64 && o[1] <= 127) return true; // 100.64/10
    if (o[0] === 169 && o[1] === 254) return true;         // 169.254/16
    return false;
  }

  // IPv6. Today's clones always register IPv4, so this is here so that a
  // future one registering a unique-local or link-local address is not
  // turned away.
  const head = addr.split(":")[0];
  if (!/^[0-9a-f]{1,4}$/.test(head)) return false;
  const h = parseInt(head, 16);
  if ((h & 0xfe00) === 0xfc00) return true; // fc00::/7
  if ((h & 0xffc0) === 0xfe80) return true; // fe80::/10
  return false;
}

async function drop(store, key) {
  if (!key) return;
  try {
    await store.delete(key);
  } catch (e) {
    /* a stale key is harmless */
  }
}

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

    // token is optional: clones running the older code send one and are
    // served exactly as they always were, newer ones do not.
    const { code, ip, port, token } = body;
    if (!code || !ip || !port) {
      return new Response(
        JSON.stringify({ error: "missing fields" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    if (!isPrivateAddress(ip)) {
      return new Response(
        JSON.stringify({ error: "ip must be a private address" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const net = await networkKey(clientIp(req, context));
    const entry = { ip, port, timestamp: Date.now(), code };
    if (token) entry.token = token;
    if (net) entry.net = net;

    try {
      await store.setJSON(code, entry);
      // Second key, so a phone on the same network can be redirected
      // without anyone typing the digits. Where two clones share one
      // public address this overwrites, which is last refresh winning.
      if (net) await store.setJSON(net, entry);
    } catch (e) {
      return new Response(JSON.stringify({ error: "blob store error" }), {
        status: 502,
        headers: { "Content-Type": "application/json" },
      });
    }

    return new Response(JSON.stringify({ ok: true }), {
      headers: { "Content-Type": "application/json" },
    });
  }

  if (req.method === "GET") {
    const url = new URL(req.url);
    const code = url.searchParams.get("code");

    // With a code, look the entry up by it. Without one, look it up by
    // the network the phone is asking from.
    const key = code || (await networkKey(clientIp(req, context)));
    if (!key) {
      return new Response(
        JSON.stringify({ error: "Invalid or expired code" }),
        { status: 404, headers: { "Content-Type": "application/json" } }
      );
    }

    let entry;
    try {
      entry = await store.get(key, { type: "json" });
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
      await drop(store, key);
      return new Response(
        JSON.stringify({ error: "Invalid or expired code" }),
        { status: 404, headers: { "Content-Type": "application/json" } }
      );
    }

    if (entry.token) {
      // A clone running the older code. Its token is a credential that
      // server accepts exactly once, so the entry is consumed on read as
      // it always has been. Both keys go, or the other one would hand
      // the same spent token to the next phone.
      await drop(store, entry.code || key);
      await drop(store, entry.net);
      return new Response(
        JSON.stringify({ ip: entry.ip, port: entry.port, token: entry.token }),
        { headers: { "Content-Type": "application/json" } }
      );
    }

    // A clone that no longer issues tokens. The entry says where the
    // server is and nothing more, so it can be read as often as anyone
    // in the household needs it, until it goes stale.
    return new Response(
      JSON.stringify({ ip: entry.ip, port: entry.port }),
      { headers: { "Content-Type": "application/json" } }
    );
  }

  return new Response("Method not allowed", { status: 405 });
};
