#!/usr/bin/env python3
"""v0.16:
1) Previous surgeries: no biopsy result / treatment fields (operation, side, year, note only).
2) An exam added by the secretary or writer works at once but waits for the doctor to
   confirm its price: a bar on the doctor screen (config/main.pendingExams) with
   «✓ تأكيد السعر» and «✎ تعديل السعر» (opens Settings → exams and prices).
Doctor + secretary screens; run tools/make-writer.py afterwards."""
import pathlib, sys
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html', 'secretary-karma-test.html']

def must(s, old, new, what):
    n = s.count(old)
    if n != 1: sys.exit(f'patch-v16: expected 1 of [{what}], found {n}')
    return s.replace(old, new)

R = [
 # 1) Remove result / treatment from the dialog, the saved record and the text.
 ("  lab('نتيجة الخزعة / الفحص النسيجي');const rs=el('select');opt(rs,'','— ما مسوية أو ما تنطبق');RESULTS.forEach(x=>opt(rs,x));d.append(rs);\n"
  "  lab('علاج بعد العملية');const tx=el('div',undefined,'tx');const boxes=TX.map(t=>{const l=el('label'),c=el('input');c.type='checkbox';c.value=t;l.append(c,' '+t);tx.append(l);return c});d.append(tx);\n", "", 'dialog fields'),
 ("sd.value=init.side||'';rs.value=init.result||'';boxes.forEach(b=>b.checked=(init.tx||[]).includes(b.value));", "sd.value=init.side||'';", 'dialog init'),
 ("side:sd.value,result:rs.value,tx:boxes.filter(b=>b.checked).map(b=>b.value),year:y", "side:sd.value,year:y", 'dialog save'),
 ("window.surgText=function(x){return [x.op+(x.side?' ('+x.side+')':''),x.result&&x.result!=='ما معروف'?x.result:x.result?'النتيجة ما معروفة':'',(x.tx||[]).join(' + '),x.year?'سنة '+x.year:'',x.note||''].filter(Boolean).join(' — ')};",
  "window.surgText=function(x){return [x.op+(x.side?' ('+x.side+')':''),x.year?'سنة '+x.year:'',x.note||''].filter(Boolean).join(' — ')};", 'text'),
 ("{const nv=sgw.value;if(JSON.stringify(nv)!==JSON.stringify(p.surgeries||[]))",
  "{const nv=sgw.value;if(JSON.stringify(nv)!==JSON.stringify((p.surgeries||[]).map(({result,tx,...x})=>x)))", 'edit compare'),
 # 2) Pending price confirmation.
 ("audit('إضافة فحص جديد — '+name+' ('+money(p)+(c!==p?'، الأطفال '+money(c):'')+')');",
  "audit('إضافة فحص جديد — '+name+' ('+money(p)+(c!==p?'، الأطفال '+money(c):'')+')');if(roleName()!=='الطبيب')markPending({name,adult:p,child:c,by:roleName(),at:stamp()});", 'pending mark'),
 (" const baseRefresh=refreshExamOptions;",
  " async function markPending(x){try{const s=await FB.getDoc(CFG());const cur=(s.exists()&&Array.isArray(s.data().pendingExams))?s.data().pendingExams:[];await FB.setDoc(CFG(),{pendingExams:cur.filter(y=>y.name!==x.name).concat(x)},{merge:true})}catch(e){console.error(e)}}\n"
  " async function clearPending(name){try{const s=await FB.getDoc(CFG());const cur=(s.exists()&&Array.isArray(s.data().pendingExams))?s.data().pendingExams:[];await FB.setDoc(CFG(),{pendingExams:cur.filter(y=>y.name!==name)},{merge:true});S.pendingExams=(S.pendingExams||[]).filter(y=>y.name!==name);drawPending()}catch(e){toast('تعذر الحفظ: '+(e.code||e.message))}}\n"
  " function drawPending(){if(roleName()!=='الطبيب')return;let bar=$('pendBar');const L=(S.pendingExams||[]).filter(x=>examCatalog.some(e=>e.name===x.name));if(!L.length){if(bar)bar.remove();return}\n"
  "  if(!bar){bar=el('div');bar.id='pendBar';const m=document.querySelector('main');const h=m&&m.querySelector('header');(h||m).after?((h||m).after(bar)):m.prepend(bar)}bar.replaceChildren();\n"
  "  L.forEach(x=>{const cur=examCatalog.find(e=>e.name===x.name)||x,r=el('div',undefined,'pend-row');r.append(el('span','🆕 فحص جديد أضافته '+(x.by||'')+': «'+x.name+'» بسعر '+money(cur.adult)+(cur.child!==cur.adult?' (الأطفال '+money(cur.child)+')':''),'pend-t'));\n"
  "   const ok=btn('✓ تأكيد السعر',()=>{audit('تأكيد سعر فحص — '+x.name);clearPending(x.name);toast('✓ تأكد السعر')});ok.className='primary';\n"
  "   const ed=btn('✎ تعديل السعر',()=>{document.querySelector('#nav button[data-page=settings]').click();setTimeout(()=>{const t=[...document.querySelectorAll('#catalogRows input')].find(i=>i.value===x.name);if(t){t.scrollIntoView({block:'center'});t.focus()}},300)});r.append(ok,ed);bar.append(r)})}\n"
  " const baseRefresh=refreshExamOptions;", 'pending fns'),
 ("un=FB.onSnapshot(CFG(),s=>{const x=s.data()||{};S.surgCustom=x.surgeriesCustom||{}},()=>{});",
  "un=FB.onSnapshot(CFG(),s=>{const x=s.data()||{};S.surgCustom=x.surgeriesCustom||{};S.pendingExams=x.pendingExams||[];drawPending()},()=>{});", 'snapshot'),
 (".v15dlg label{", "#pendBar{display:flex;flex-direction:column;gap:6px;margin:0 0 12px}#pendBar .pend-row{display:flex;flex-wrap:wrap;align-items:center;gap:8px;background:#5a3a12;color:#fde9c8;border:1px solid #8a5a1c;border-radius:12px;padding:9px 12px;font-weight:700}#pendBar .pend-t{flex:1 1 220px}#pendBar button{padding:7px 12px;font-size:13px}body:not(.dark) #pendBar .pend-row{background:#fde9c8;color:#5a3a12}@media(max-width:760px){main>#pendBar{order:1}}\n.v15dlg label{", 'css'),
]
for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'pendingExams' in s: print('already', f); continue
    for o, n, w in R: s = must(s, o, n, w)
    p.write_text(s, encoding='utf-8'); print('patched', f)
