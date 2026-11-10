const C='clinic-test-v2';
self.addEventListener('install',e=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin)return;
e.respondWith(fetch(u.href,{cache:'no-cache',credentials:'same-origin'}).then(r=>{if(r.ok){const c=r.clone();caches.open(C).then(x=>x.put(u.origin+u.pathname,c))}return r}).catch(()=>caches.match(u.origin+u.pathname)))});
