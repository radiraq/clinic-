const C='clinic-test-v2';
self.addEventListener('install',e=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
// Fast start: try the network, but if it is slow (>2.5 s) show the saved copy and refresh it quietly.
// version.txt always goes straight to the network (never cached: it carries the server clock).
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin)return;if(u.pathname.endsWith('/version.txt'))return;
const key=u.origin+u.pathname;
const net=fetch(u.href,{cache:'no-cache',credentials:'same-origin'}).then(r=>{if(r.ok){const c=r.clone();e.waitUntil(caches.open(C).then(x=>x.put(key,c)))}return r});
e.waitUntil(net.then(()=>{},()=>{}));
e.respondWith(caches.match(key).then(hit=>{if(!hit)return net;
 return Promise.race([net.then(r=>r.ok?r:hit,()=>hit),new Promise(res=>setTimeout(()=>res(hit),2500))])}))});
