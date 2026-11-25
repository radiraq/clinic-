import re,glob
NEW='20261125173500'
UNDO=r"""<style id="v33css">
#rows .b-undone{background:transparent;color:#f5c26b;border:1px solid #f5c26b88;font-weight:700}
</style>
<script id="v33js">
(function(){
 // «↶ تراجع»: a patient marked finished by mistake goes back to how they were (inside the exam);
 // if another patient is inside now, back to waiting at their own turn.
 const DONE='مكتمل',IN='داخل الفحص',WAIT='بانتظار الدخول';
 window.undoDone=function(id){refreshSharedState();const p=list().find(x=>x.id===id);if(!p||p.status!==DONE)return toast('المريض مو مكتمل');
  const busy=list().some(x=>x.id!==id&&(x.status===IN||x.status===OUT));
  if(!confirm(busy?'ترجيع '+p.name+' للانتظار بدوره؟\n(اكو مريض هسه داخل الفحص)':'ترجيع '+p.name+' لداخل الفحص مثل ما چان؟'))return;
  refreshSharedState();const q=list().find(x=>x.id===id);if(!q||q.status!==DONE)return;
  q.statusBy=roleName();q.statusAt=stamp();
  if(!busy){q.status=IN;audit('تراجع عن إنهاء '+q.name+' — رجع داخل الفحص')}
  else{q.status=WAIT;q.enteredAt=null;q.enteredBy=null;S.waitingOrder??={};const w=waitingQueue().map(x=>x.id).filter(x=>x!==q.id);const i=w.findIndex(x=>{const o=list().find(y=>y.id===x);return o&&o.no>q.no});w.splice(i<0?w.length:i,0,q.id);S.waitingOrder[clinic()]=w;audit('تراجع عن إنهاء '+q.name+' — رجع للانتظار بدوره')}
  render();toast('↶ رجع '+q.name+(busy?' للانتظار بدوره':' داخل الفحص'))};
 function add(){document.querySelectorAll('#rows tr[data-id]').forEach(tr=>{const p=list().find(x=>x.id===tr.dataset.id);const td=tr.querySelector('td:last-child');if(!p||!td)return;const has=td.querySelector('.b-undone');
  if(p.status!==DONE){if(has)has.remove();return}if(has)return;const b=el('button','↶ تراجع','b-undone');b.type='button';b.title='انتهى بالغلط؟ يرجع مثل ما چان';b.onclick=e=>{e.stopPropagation();undoDone(p.id)};td.prepend(b)})}
 const _r=render;render=function(){const r=_r.apply(this,arguments);try{add()}catch(e){console.error(e)}return r};
 try{add()}catch(e){}
})();
</script>
"""
FOLD=r"""<style id="v33fold">
body:not(.show-done):not(.force-done) #rows tr.done-row{display:none!important}
#rows tr.done-row{opacity:.7}
#doneToggle{width:100%;margin-top:12px;padding:12px;font-size:15px;font-weight:700}
</style>
<script id="v33foldjs">
(function(){
 // Finished patients fold away under one button, like the doctor's screen.
 function fold(){let done=0;document.querySelectorAll('#rows tr[data-id]').forEach(tr=>{const p=list().find(x=>x.id===tr.dataset.id);const d=!!p&&p.status==='مكتمل';tr.classList.toggle('done-row',d);if(d)done++});
  const f=document.getElementById('filter');document.body.classList.toggle('force-done',!!f&&f.value==='مكتمل');
  let t=document.getElementById('doneToggle');const wrap=document.querySelector('#queue .tablewrap');
  if(!t&&wrap){t=document.createElement('button');t.type='button';t.id='doneToggle';t.onclick=()=>{document.body.classList.toggle('show-done');fold()};wrap.after(t)}
  if(t){t.hidden=!done||document.body.classList.contains('force-done');t.textContent=(document.body.classList.contains('show-done')?'▴ إخفاء المكتملين':'▾ عرض المكتملين')+' ('+done+')'}}
 const _r=render;render=function(){const r=_r.apply(this,arguments);try{fold()}catch(e){console.error(e)}return r};
 try{fold()}catch(e){}
})();
</script>
"""
for f in glob.glob('test/*.html'):
    s=open(f,encoding='utf-8').read()
    if 'v33js' not in s:
        add=UNDO+(FOLD if 'secretary' in f else '')
        i=s.rfind('</body>')
        s=s[:i]+add+s[i:] if i>=0 else s+add
    s=re.sub(r"var BUILD='\d+'","var BUILD='%s'"%NEW,s)
    open(f,'w',encoding='utf-8').write(s)
open('test/version.txt','w').write(NEW+'\n')
