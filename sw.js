/* TYFSADIK service worker.
   Strategy:
   - HTML, CSS, JS: network-first. A deploy is visible on the next load; the
     cache is only an offline fallback.
   - Images and fonts: stale-while-revalidate. Served from cache instantly,
     refreshed in the background so a replaced file shows up on the next visit.
   - Only successful same-origin responses are cached; the runtime cache is
     capped so it cannot grow without limit.
   CACHE is stamped with a content hash at deploy time by
   .tools/stamp_assets.py, so every deploy clears the previous caches. */
const CACHE = 'tyfsadik-dev';
const OFFLINE = '/offline.html';
const MAX_RUNTIME_ENTRIES = 80;
const PRECACHE = [
  '/',
  '/css/style.css',
  '/js/main.js',
  '/offline.html',
  '/images/banner-mine.jpg',
  '/fonts/DepartureMono-Regular.woff',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Drop the oldest entries once the cache passes the cap (precache entries
// are re-added on the next install, so trimming them is harmless).
const trim = (cache) => cache.keys().then((keys) => {
  const extra = keys.length - MAX_RUNTIME_ENTRIES;
  return extra > 0 ? Promise.all(keys.slice(0, extra).map((k) => cache.delete(k))) : null;
});

const store = (req, res) => {
  if (!res || !res.ok || res.type !== 'basic') return;
  const copy = res.clone();
  caches.open(CACHE).then((c) => c.put(req, copy).then(() => trim(c)));
};

const networkFirst = (req, fallback) =>
  fetch(req)
    .then((res) => { store(req, res); return res; })
    .catch(() => caches.match(req, { ignoreSearch: true })
      .then((r) => r || (fallback ? caches.match(fallback) : Response.error())));

const staleWhileRevalidate = (req) =>
  caches.match(req).then((cached) => {
    const fresh = fetch(req).then((res) => { store(req, res); return res; }).catch(() => cached);
    return cached || fresh;
  });

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  if (req.mode === 'navigate') {
    e.respondWith(networkFirst(req, OFFLINE));
    return;
  }
  if (/\.(css|js|json)$/.test(url.pathname)) {
    e.respondWith(networkFirst(req));
    return;
  }
  e.respondWith(staleWhileRevalidate(req));
});
