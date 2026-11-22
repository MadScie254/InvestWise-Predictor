const ALLOW = [
  { host: "query1.finance.yahoo.com", prefix: "/v8/finance/chart/" },
  { host: "api.worldbank.org", prefix: "/v2/" },
  { host: "afx.kwayisi.org", prefix: "/nse/" },
  { host: "news.google.com", prefix: "/rss/" },
];

function allowed(url) {
  return ALLOW.some((rule) => url.hostname === rule.host && url.pathname.startsWith(rule.prefix));
}

function ttlFor(host) {
  if (host === "api.worldbank.org") return 86400;
  if (host === "news.google.com") return 900;
  if (host === "afx.kwayisi.org") return 180;
  return 300;
}

export default {
  async fetch(request) {
    const incoming = new URL(request.url);
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors() });
    }
    if (request.method !== "GET") {
      return json({ error: "Method not allowed." }, 405);
    }
    if (incoming.pathname === "/" || incoming.pathname === "/health") {
      return json({ ok: true, service: "investwise-proxy" }, 200);
    }
    if (incoming.pathname !== "/fetch") {
      return json({ error: "Unknown path." }, 404);
    }

    let target;
    try {
      target = new URL(incoming.searchParams.get("url") || "");
    } catch {
      return json({ error: "Missing url." }, 400);
    }
    if (target.protocol !== "https:" || target.username || target.password || !allowed(target)) {
      return json({ error: "That address is not on the allow list." }, 400);
    }

    const ttl = ttlFor(target.hostname);
    console.log(JSON.stringify({ message: "proxy fetch", host: target.hostname, path: target.pathname }));

    let upstream;
    try {
      upstream = await fetch(target.toString(), {
        method: "GET",
        redirect: "follow",
        headers: {
          "user-agent": "InvestWiseDesk/1.0",
          accept: "application/json, application/xml, text/html;q=0.9, */*;q=0.8",
        },
        cf: { cacheTtl: ttl, cacheEverything: true },
      });
    } catch (error) {
      console.error(JSON.stringify({
        message: "upstream failed",
        host: target.hostname,
        error: error instanceof Error ? error.message : String(error),
      }));
      return json({ error: "The data source did not answer." }, 502);
    }

    const headers = new Headers();
    const type = upstream.headers.get("content-type");
    if (type) headers.set("content-type", type);
    headers.set("cache-control", `public, max-age=${ttl}`);
    headers.set("x-investwise-proxy", "1");
    for (const [key, value] of Object.entries(cors())) headers.set(key, value);

    return new Response(upstream.body, { status: upstream.status, headers });
  },
};

function cors() {
  return {
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "GET, OPTIONS",
    "access-control-allow-headers": "content-type",
  };
}

function json(body, status) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...cors() },
  });
}
