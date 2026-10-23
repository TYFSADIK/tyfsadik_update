/* TYFSADIK service worker.
   Strategy: network-first for HTML (fresh content wins), cache-first for
   static assets (css, js, images, fonts). Versioned cache; bump CACHE on any
   deploy that changes assets. skipWaiting + clients.claim so a new deploy
   takes over immediately and never serves stale HTML. */
const CACHE = 'tyfsadik-v1';
const OFFLINE = '/offline.html';
const PRECACHE = [
  '/',
  '/index.html',
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

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() => caches.match(req).then((r) => r || caches.match(OFFLINE)))
    );
    return;
  }

  e.respondWith(
    caches.match(req).then((cached) => cached || fetch(req).then((res) => {
      if (res.ok) {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
      }
      return res;
    }).catch(() => cached))
  );
});
