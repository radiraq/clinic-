#!/usr/bin/env python3
"""v0.20: «↕ ترتيب الفحوصات» in Settings (above the exams table) — the secretary (or anyone) moves exams
up/down or to the top; the order is saved to the clinic's shared catalog, so the list
opens in that order on every screen of the clinic. Doctor + secretary screens; run
tools/make-writer.py afterwards."""
import pathlib
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html', 'secretary-karma-test.html']
LAYER = r"""<style id="v20css">
.ord-btn{margin-top:-4px;padding:6px 12px;font-size:13px;align-self:flex-start}#patientForm .formgrid>.ord-btn{grid-column:1/-1;justify-self:start}#ordDlg .ord-list:focus{outline:none}
#ordDlg .ord-list{display:flex;flex-direction:column;gap:5px;max-height:60vh;overflow:auto;margin:10px 0}
#ordDlg .ord-row{display:flex;align-items:center;gap:6px;border:1px solid var(--line);border-radius:10px;padding:6px 8px;background:var(--bg)}
#ordDlg .ord-row.moved{border-color:#2f9e74;background:rgba(40,170,110,.10)}
#ordDlg .ord-n{min-width:22px;color:var(--muted);font-size:12px;text-align:center}#ordDlg .ord-t{flex:1;font-size:14px;font-weight:600}
#ordDlg .ord-row button{padding:5px 9px;font-size:14px;min-width:34px}
</style>
<script id="v20js">
(function(){
 // Reorder the exam list (shared by every screen of this clinic).
 function openOrder(){let d=$('ordDlg');if(!d){d=el('dialog');d.id='ordDlg';d.style.width='min(460px,94vw)';document.body.append(d)}d.replaceChildren();
  const h=el('h2','↕ ترتيب الفحوصات');h.style.fontSize='18px';d.append(h,el('small','⤒ يطلّع الفحص لأول القائمة • ↑↓ تحريك خطوة','muted'));
  let L=examCatalog.map(x=>({...x}));let last='';const box=el('div',undefined,'ord-list');d.append(box);
  const mv=(i,j)=>{if(j<0||j>=L.length)return;const [x]=L.splice(i,1);L.splice(j,0,x);last=x.name;draw()};
  function draw(){box.replaceChildren();L.forEach((x,i)=>{const r=el('div',undefined,'ord-row'+(x.name===last?' moved':''));r.append(el('span',String(i+1),'ord-n'),el('span',x.name,'ord-t'));
   const t=btn('⤒',()=>mv(i,0)),u=btn('↑',()=>mv(i,i-1)),w=btn('↓',()=>mv(i,i+1));[t,u,w].forEach(b=>b.type='button');t.title='لأول القائمة';t.disabled=u.disabled=i===0;w.disabled=i===L.length-1;r.append(t,u,w);box.append(r)});
   const m=box.querySelector('.moved');if(m)m.scrollIntoView({block:'nearest'})}
  draw();const a=el('div',undefined,'actions');
  const ok=btn('✓ حفظ الترتيب',()=>{const names=L.map(x=>x.name),cur=examCatalog.map(x=>x.name);d.close();if(names.join('|')===cur.join('|'))return;
   // keep any price change made meanwhile: reorder the live catalog by the new names
   const live=examCatalog.slice();examCatalog=names.map(n=>live.find(x=>x.name===n)).filter(Boolean).concat(live.filter(x=>!names.includes(x.name)));
   try{localStorage.setItem(CATALOG_KEY,JSON.stringify(examCatalog))}catch{}pushCatalog();refreshExamOptions();if(typeof renderCatalog==='function')try{renderCatalog()}catch(e){}
   audit('تغيير ترتيب الفحوصات');toast('✓ انحفظ الترتيب')});ok.type='button';ok.className='primary';
  const no=btn('تراجع',()=>d.close());no.type='button';a.append(ok,no);d.append(a);d.oncancel=e=>{e.preventDefault();d.close()};d.showModal()}
 // The button lives in Settings, above the exams-and-prices table.
 const rows=$('catalogRows');if(!rows)return;const wrap=rows.closest('.tablewrap')||rows.closest('table');const b=btn('↕ ترتيب الفحوصات بقائمة التسجيل',openOrder);b.type='button';b.className='ord-btn';b.style.margin='4px 0 12px';
 wrap.before(b);
})();
</script>
</body></html>"""
for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v20js"' in s: print('already', f); continue
    s = s.rstrip(); assert s.endswith('</body></html>')
    p.write_text(s[:-len('</body></html>')] + LAYER + '\n', encoding='utf-8'); print('patched', f)
