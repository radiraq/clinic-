#!/usr/bin/env python3
"""v0.21 (all six test screens + sw-test.js):
1) White first page on a weak connection: the service worker now answers from its saved copy
   when the network is slow (>2.5 s) and refreshes the copy in the background.
2) False "device clock is wrong" banner when the internet drops: version.txt is never cached
   by the service worker, and the clock check is skipped while offline.
3) Referring doctor: «✍️ اكتب» button next to the list + «اكتب اسم طبيب جديد» at the top of the
   list; a typed name is used for the patient right away, even offline.
Also: no auto-update reload while a login password is being typed."""
import pathlib, time
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html',
         'secretary-karma-test.html', 'writer-test.html', 'writer-karma-test.html']
BUILD = time.strftime('%Y%m%d%H%M%S')

REPL = [
 # (2) clock check: skip offline, ignore any answer that came from a cache
 ("function check(){const t0=Date.now();fetch('version.txt?clock='+t0,{cache:'no-store'}).then(r=>{const d=r.headers.get('date');if(!d)return;",
  "function check(){if(!navigator.onLine)return;const t0=Date.now();fetch('version.txt?clock='+t0,{cache:'no-store'}).then(r=>{const d=r.headers.get('date');if(!d||!r.ok||r.headers.get('x-sw-cache'))return;if(Date.now()-t0>15000)return;"),
 # (3a) "type a new name" option at the top of the list
 ("const o0=el('option','— بدون —');o0.value='';sel.append(o0);",
  "const o0=el('option','— بدون —');o0.value='';sel.append(o0);{const ot=el('option','✍️ اكتب اسم طبيب جديد…');ot.value=NEW;sel.append(ot)}"),
 ("const on=el('option','＋ إضافة طبيب جديد…');on.value=NEW;sel.append(on);", ""),
 # (3b) adding a name never blocks on the network
 ("try{const snap=await FB.getDoc(cfgRef());const cur=(snap.exists()&&Array.isArray(snap.data().referrers))?snap.data().referrers:[];\n   const next=cur.some(x=>same(x,name))?cur:sortAr(cur.concat(name));await FB.setDoc(cfgRef(),{referrers:next},{merge:true});S.referrers=next;\n   audit('إضافة طبيب محوِّل — '+name);fill();toast('✓ انضاف '+name);return name}\n  catch(err){console.error(err);toast('تعذر حفظ الاسم: '+(err.code||err.message));return ''}",
  "let cur=(S.referrers||[]).slice();try{if(navigator.onLine){const snap=await Promise.race([FB.getDoc(cfgRef()),new Promise((_,j)=>setTimeout(()=>j(Error('slow')),4000))]);if(snap.exists()&&Array.isArray(snap.data().referrers))cur=snap.data().referrers}}catch(e){}\n   const next=cur.some(x=>same(x,name))?cur:sortAr(cur.concat(name));S.referrers=next;FB.setDoc(cfgRef(),{referrers:next},{merge:true}).catch(err=>{console.error(err);toast('تعذر حفظ الاسم بالقائمة: '+(err.code||err.message))});\n   audit('إضافة طبيب محوِّل — '+name);fill();toast('✓ انضاف '+name);return name"),
 # (3c) «✍️ اكتب» button beside the registration list
 ("function fill(){const r=$('referrer');if(r){build(r);wire(r)}",
  "function typeBtn(r){if($('refType'))return;const row=el('span',undefined,'ref-row');r.parentNode.insertBefore(row,r);row.append(r);const b=btn('✍️ اكتب',async()=>{const n=await addReferrer();if(n)build(r,n)});b.type='button';b.id='refType';b.title='اكتب اسم طبيب مو موجود بالقائمة';b.disabled=r.disabled;row.append(b)}\n function fill(){const r=$('referrer');if(r){build(r);wire(r);typeBtn(r)}"),
 # no auto-update reload while a password is typed in a login box
 ("const busy=($('name')&&$('name').value.trim())||",
  "const busy=($('name')&&$('name').value.trim())||[...document.querySelectorAll('dialog[open] input')].some(i=>i.value)||"),
]
CSS = "<style id=\"v21css\">.ref-row{display:flex;gap:6px;align-items:stretch;width:100%}.ref-row select{flex:1;min-width:0}#refType{flex:0 0 auto;white-space:nowrap;padding:0 14px;font-weight:700}</style>\n"

for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v21css"' in s: print('already', f); continue
    for a, b in REPL:
        n = s.count(a); assert n == 1, (f, n, a[:60]); s = s.replace(a, b)
    old = s[s.index("BUILD='"):].split("'")[1]; s = s.replace("BUILD='%s'" % old, "BUILD='%s'" % BUILD)
    s = s.replace('الإصدار 0.7 التجريبي (18/11)', 'الإصدار 0.7 التجريبي (19/11)')
    s = s.rstrip(); assert s.endswith('</body></html>')
    p.write_text(s[:-len('</body></html>')] + CSS + '</body></html>\n', encoding='utf-8'); print('patched', f)

(T / 'version.txt').write_text(BUILD + '\n')
(T / 'sw-test.js').write_text(r"""const C='clinic-test-v2';
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
""")
print('BUILD', BUILD)
