const CACHE_NAME = "jobtrail-v1";
const ASSETS = [
  "/",
  "/index.html",
  "/manifest.json",
  "/icon.svg"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  // Only cache GET requests that are not API requests
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.pathname.startsWith("/applications") || url.pathname.startsWith("/me") || url.pathname.startsWith("/login") || url.pathname.startsWith("/signup")) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      return cached || fetch(event.request).then((res) => {
        if (!res || res.status !== 200 || res.type !== "basic") {
          return res;
        }
        const resClone = res.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, resClone);
        });
        return res;
      }).catch(() => {
        if (event.request.headers.get("accept").includes("text/html")) {
          return caches.match("/");
        }
      });
    })
  );
});
