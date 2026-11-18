#!/usr/bin/env python3
"""v0.8: referring doctors — fix first-time list (seed checked against the server, not the
cache) and favourites (⭐) shown first in the list. The doctor stars a name from Settings;
favourites are shared by every screen (config/main.referrerFavs). Doctor + secretary
screens; run tools/make-writer.py afterwards."""
import pathlib, sys
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html', 'secretary-karma-test.html']

def must(s, old, new, what):
    n = s.count(old)
    if n != 1: sys.exit(f'patch-v08: expected 1 of [{what}], found {n}')
    return s.replace(old, new)

R = [
 # Seed: ask the server itself, once, instead of trusting a cached snapshot.
 ("if(!Array.isArray(x.referrers)&&!snap.metadata.fromCache){FB.setDoc(cfgRef(),{referrers:sortAr(SEED)},{merge:true}).catch(()=>{});return}",
  "S.refFavs=Array.isArray(x.referrerFavs)?x.referrerFavs:[];if(!Array.isArray(x.referrers)){seedOnce();return}", 'seed'),
 ("const r=Array.isArray(x.referrers)?x.referrers:[];if(stable(r)!==stable(S.referrers||[])){S.referrers=r;fill()}",
  "const r=x.referrers;if(stable(r)!==stable(S.referrers||[])||stable(S.refFavs)!==favSeen){S.referrers=r;favSeen=stable(S.refFavs);fill()}", 'snapshot'),
 (" let unsub=null,forUid='';",
  " let unsub=null,forUid='',seeding=false,favSeen='';\n function seedOnce(){if(seeding)return;seeding=true;FB.getDoc(cfgRef()).then(s=>{const d=s.exists()?s.data():{};if(Array.isArray(d.referrers)){S.referrers=d.referrers;S.refFavs=d.referrerFavs||[];fill();return}return FB.setDoc(cfgRef(),{referrers:sortAr(SEED)},{merge:true}).then(()=>{S.referrers=sortAr(SEED);fill()})}).catch(err=>{console.error('referrers seed',err);seeding=false})}", 'state'),
 # Favourites first in every list.
 ("  const names=sortAr(S.referrers||[]);if(v&&v!==NEW&&!names.some(x=>x===v))names.unshift(v);\n  names.forEach(n=>{const o=el('option',n);o.value=n;sel.append(o)});",
  "  const all=sortAr(S.referrers||[]),fav=all.filter(isFav),rest=all.filter(n=>!isFav(n));if(v&&v!==NEW&&!all.some(x=>x===v))rest.unshift(v);\n  const grp=(label,list)=>{if(!list.length)return;const g=document.createElement('optgroup');g.label=label;list.forEach(n=>{const o=el('option',(isFav(n)?'⭐ ':'')+n);o.value=n;g.append(o)});sel.append(g)};\n  if(fav.length){grp('⭐ المفضلة',fav);grp('كل الأطباء',rest)}else rest.forEach(n=>{const o=el('option',n);o.value=n;sel.append(o)});", 'build'),
 (" function wire(sel){",
  " function isFav(n){return (S.refFavs||[]).some(x=>same(x,n))}\n async function toggleFav(n){try{const snap=await FB.getDoc(cfgRef());const cur=(snap.exists()&&Array.isArray(snap.data().referrerFavs))?snap.data().referrerFavs:[];const on=cur.some(x=>same(x,n));const next=on?cur.filter(x=>!same(x,n)):cur.concat(n);await FB.setDoc(cfgRef(),{referrerFavs:next},{merge:true});S.refFavs=next;audit((on?'إزالة من المفضلة — ':'إضافة للمفضلة — ')+n);fill();toast(on?'شلته من المفضلة':'⭐ صار بالمفضلة')}catch(err){toast('تعذر الحفظ: '+(err.code||err.message))}}\n function wire(sel){", 'fav fns'),
 ("names.forEach(n=>{const s=el('span',n);s.append(btn('✕',()=>removeReferrer(n)));l.append(s)})}",
  "const fv=names.filter(isFav);names.sort((a,b)=>isFav(b)-isFav(a));names.forEach(n=>{const s=el('span',n),st=btn(isFav(n)?'⭐':'☆',()=>toggleFav(n));st.title=isFav(n)?'شيل من المفضلة':'خليه بالمفضلة (يطلع أول القائمة)';s.prepend(st);s.append(btn('✕',()=>removeReferrer(n)));l.append(s)})}", 'settings list'),
 ("el('p','القائمة مشتركة لكل شاشات العيادة (الطبيب، السكرتيرة، الكاتبة) وتنضاف الأسماء من أي شاشة وقت التسجيل.','muted')",
  "el('p','القائمة مشتركة لكل شاشات العيادة (الطبيب، السكرتيرة، الكاتبة) وتنضاف الأسماء من أي شاشة وقت التسجيل. اضغط ☆ يم الاسم حتى يصير بالمفضلة ويطلع أول القائمة.','muted')", 'settings note'),
 (" S.referrers=S.referrers||[];\n", " S.referrers=S.referrers||[];S.refFavs=S.refFavs||[];\n", 'init'),
 ("const baseSub=subscribe;subscribe=function(){const keep=S.referrers||[];const r=baseSub.apply(this,arguments);S.referrers=keep;",
  "const baseSub=subscribe;subscribe=function(){const keep=S.referrers||[],kf=S.refFavs||[];const r=baseSub.apply(this,arguments);S.referrers=keep;S.refFavs=kf;", 'subscribe'),
]

for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'referrerFavs' in s: print('already', f); continue
    for old, new, what in R: s = must(s, old, new, what)
    p.write_text(s, encoding='utf-8'); print('patched', f)
