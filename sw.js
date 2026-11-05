const C = 'clinic-app-b2f9a208';
const FILES = ['./index.html', './doc.html', './app.css', './sec.webmanifest', './doc.webmanifest', './icon-sec-192.png', './icon-sec-512.png', './icon-doc-192.png', './icon-doc-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(C).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
const u = new URL(e.request.url);
if (e.request.method !== 'GET' || u.origin !== location.origin || u.pathname.endsWith('/sw.js')) return;
let name = './' + u.pathname.split('/').pop(); if (name === './') name = './index.html';
e.respondWith(caches.open(C).then(c => c.match(name).then(hit => hit || fetch(e.request).then(r => { if (r.ok) c.put(name, r.clone()); return r; }))));
});