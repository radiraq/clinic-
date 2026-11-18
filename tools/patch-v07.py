#!/usr/bin/env python3
"""v0.7: cancelled patients leave the today list (still visible with the «ملغي» filter);
referring-doctor list (الطبيب المحوِّل) in registration and patient edit, shared by every
screen of the clinic (stored in clinics/<id>/config/main.referrers); anyone can add a name,
the doctor can remove names from Settings. Doctor + secretary screens; run
tools/make-writer.py afterwards."""
import pathlib, sys
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html', 'secretary-karma-test.html']

REF_FIELD = ('<label class="full">👨‍⚕️ الطبيب المحوِّل <small class="muted">(اختياري)</small>'
             '<select id="referrer" aria-label="الطبيب المحول"><option value="">— بدون —</option></select></label>')

LAYER = r"""<style id="v07ref">
.ref-tag{display:inline-block;font-size:12px;font-weight:600;color:#9fd3ff;background:#1d3f5f;border-radius:7px;padding:1px 7px;margin-inline-start:6px;white-space:nowrap}
body:not(.dark) .ref-tag{color:#1d4f7a;background:#dbeafe}
#refList{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}#refList span{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line);border-radius:9px;padding:5px 10px;background:var(--bg)}#refList button{padding:2px 8px;font-size:13px}
</style>
<script id="v07js">
(function(){
 // Referring doctors: one shared list per clinic, kept in config/main.referrers.
 const NEW='__new__';
 // First list = the referring doctors from the report template (male.docx); added once if the clinic has none yet.
 const SEED=["د. عبد الحكيم خلف الجميلي", "د. مروه باسم يار مراد", "د. باسم عطا الله", "د. احمد ابرهيم", "د. ضياء مجول", "د. ضياء الجميلي", "د. ايناس شاكر", "د. حسن فتحي", "د. احمد حازم", "د. وليد خالد", "د. ثائر بشير", "د. مازن عبدالجبار", "د. هديل الهلالي", "د. اكرم نواف", "د. عادل عويد", "د. عمر عصام", "د. سلام العلي", "د. علي النايل", "د. كمال رجا الحداد", "د. محمد اسماعيل داوود", "د. غادة وائل تحسين", "د. علي رافع الجنابي", "د. علي حياد", "د. مصطفى واثق مديح", "د. سعد عبدالقادر الدراجي", "د. إسحاق فارس حمادي", "د. عدنان جيجان عبيد", "د. أسماء صالح", "د. احمد عبدالجبار", "د. مصطفى لؤي بدر الدين", "د. رباب حامد فرحان", "د. لؤي احمد العاني", "د. أسامة إسماعيل", "د. عبدالعزيز احمد مرشد", "د. مهند حسين علوان", "د. حنان خميس", "د. محمد فالح", "د. إبراهيم مصطفى", "د. انمار حامد", "د. طه محمد فليح", "د. فواز مهدي", "د. مصطفى عباس", "د. زياد حماد", "د. رغد احمد", "د. ستار عبد حمود", "د. اميل فاروق", "د. عمار حميد هويدي", "د. وليد السعد", "د. حارث عبدالرحمن الكبيسي", "د. محمد فوزي"];
 S.referrers=S.referrers||[];
 const key=t=>normText(String(t).replace(/^د\.\s*/,'')).replace(/[ةه]$/,'ه').replace(/ى/g,'ي');
 const sortAr=a=>a.slice().sort((x,y)=>key(x).localeCompare(key(y),'ar'));
 const same=(a,b)=>normText(a)===normText(b);
 function cfgRef(){return FB.doc(cloud.db,'clinics',CLINIC_ID,'config','main')}
 async function addReferrer(){
  if(!cloud.db||!cloud.user){toast('سجّل الدخول أولًا');return ''}
  const raw=await askDialog('👨‍⚕️ إضافة طبيب محوِّل',{input:true,placeholder:'مثال: د. أحمد العاني',ok:'إضافة'});
  const name=String(raw||'').replace(/\s+/g,' ').trim().slice(0,60);if(!name)return '';
  const have=(S.referrers||[]).find(x=>same(x,name));if(have){toast('الاسم موجود');return have}
  try{const snap=await FB.getDoc(cfgRef());const cur=(snap.exists()&&Array.isArray(snap.data().referrers))?snap.data().referrers:[];
   const next=cur.some(x=>same(x,name))?cur:sortAr(cur.concat(name));await FB.setDoc(cfgRef(),{referrers:next},{merge:true});S.referrers=next;
   audit('إضافة طبيب محوِّل — '+name);fill();toast('✓ انضاف '+name);return name}
  catch(err){console.error(err);toast('تعذر حفظ الاسم: '+(err.code||err.message));return ''}
 }
 async function removeReferrer(name){
  if(!(await askDialog('حذف «'+name+'» من قائمة الأطباء المحولين؟ (المرضى المسجلين سابقًا يبقى اسمه عندهم)',{ok:'حذف'})))return;
  try{const snap=await FB.getDoc(cfgRef());const cur=(snap.exists()&&Array.isArray(snap.data().referrers))?snap.data().referrers:[];
   const next=cur.filter(x=>!same(x,name));await FB.setDoc(cfgRef(),{referrers:next},{merge:true});S.referrers=next;audit('حذف طبيب محوِّل — '+name);fill();toast('انحذف '+name)}
  catch(err){toast('تعذر الحذف: '+(err.code||err.message))}
 }
 // A <select> of referrers: «بدون», the names, then «＋ إضافة طبيب جديد».
 function build(sel,val){const v=val??sel.value;sel.replaceChildren();const o0=el('option','— بدون —');o0.value='';sel.append(o0);
  const names=sortAr(S.referrers||[]);if(v&&v!==NEW&&!names.some(x=>x===v))names.unshift(v);
  names.forEach(n=>{const o=el('option',n);o.value=n;sel.append(o)});const on=el('option','＋ إضافة طبيب جديد…');on.value=NEW;sel.append(on);
  sel.value=v&&v!==NEW?v:''}
 function wire(sel){if(sel.dataset.refWired)return;sel.dataset.refWired='1';sel.addEventListener('change',async()=>{if(sel.value!==NEW)return;sel.value='';const n=await addReferrer();build(sel,n||'')})}
 window.refSelect=function(val){const s=el('select');build(s,val||'');wire(s);return s};
 function fill(){const r=$('referrer');if(r){build(r);wire(r)}renderRefSettings();try{tagRows()}catch(e){}}
 // Doctor settings: list with delete.
 function renderRefSettings(){const st=$('settings');if(!st||role()!=='doctor')return;let c=$('refCard');
  if(!c){c=el('div',undefined,'card');c.id='refCard';c.style.marginBottom='20px';c.append(el('h2','👨‍⚕️ الأطباء المحولين'),el('p','القائمة مشتركة لكل شاشات العيادة (الطبيب، السكرتيرة، الكاتبة) وتنضاف الأسماء من أي شاشة وقت التسجيل.','muted'));
   const a=el('div',undefined,'actions');a.append(btn('＋ إضافة طبيب',()=>addReferrer()));c.append(a);const l=el('div');l.id='refList';c.append(l);st.prepend(c)}
  const l=$('refList');l.replaceChildren();const names=sortAr(S.referrers||[]);if(!names.length)l.append(el('small','ماكو أسماء بعد','muted'));
  names.forEach(n=>{const s=el('span',n);s.append(btn('✕',()=>removeReferrer(n)));l.append(s)})}
 // Show the referrer next to the patient's name in today's list.
 function tagRows(){document.querySelectorAll('#rows tr[data-id]').forEach(tr=>{const p=list().find(x=>x.id===tr.dataset.id),td=tr.querySelector('td:nth-child(2)');if(!td)return;
  let t=td.querySelector('.ref-tag');if(p&&p.referrer){if(!t){t=el('span','','ref-tag');td.append(t)}t.textContent='↩ '+p.referrer}else if(t)t.remove()})}
 // Live list from the server.
 let unsub=null,forUid='';
 function attach(){if(!cloud.db||!cloud.user)return;if(unsub&&forUid===cloud.user.uid&&cloud.unsubs.includes(unsub))return;forUid=cloud.user.uid;
  unsub=FB.onSnapshot(cfgRef(),snap=>{const x=snap.data()||{};if(!Array.isArray(x.referrers)&&!snap.metadata.fromCache){FB.setDoc(cfgRef(),{referrers:sortAr(SEED)},{merge:true}).catch(()=>{});return}const r=Array.isArray(x.referrers)?x.referrers:[];if(stable(r)!==stable(S.referrers||[])){S.referrers=r;fill()}},()=>{});cloud.unsubs.push(unsub)}
 const baseSub=subscribe;subscribe=function(){const keep=S.referrers||[];const r=baseSub.apply(this,arguments);S.referrers=keep;unsub=null;attach();return r};
 setInterval(()=>{S.referrers=S.referrers||[];attach()},3000);
 const baseRender=render;render=function(){const r=baseRender.apply(this,arguments);try{tagRows();renderRefSettings()}catch(e){console.error(e)}return r};
 fill();attach();
})();
</script>
</body></html>"""

def must(s, old, new, what):
    n = s.count(old)
    if n != 1: sys.exit(f'patch-v07: expected 1 of [{what}], found {n}')
    return s.replace(old, new)

for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v07js"' in s: print('already', f); continue
    # 1) Cancelled patients disappear from the default list.
    s = must(s, "($('filter').value==='all'||p.status===$('filter').value)",
             "($('filter').value==='all'?p.status!=='ملغي':p.status===$('filter').value)", 'filter')
    # 2) Referrer in registration.
    s = must(s, '<label>العمر <small', REF_FIELD + '<label>العمر <small', 'age label')
    s = must(s, "regBy:roleName()});autoCollect", "regBy:roleName(),referrer:$('referrer')&&$('referrer').value!=='__new__'?$('referrer').value:''});autoCollect", 'push')
    # 3) Referrer in patient edit (v0.6 dialog).
    s = must(s, "const price=field('💵 السعر (ألف)'", "const rf=field('👨‍⚕️ الطبيب المحوِّل',refSelect(p0.referrer||'')),price=field('💵 السعر (ألف)'", 'edit price')
    s = must(s, "if(base!==p.base){", "{const rv=rf.value==='__new__'?'':rf.value;if(rv!==(p.referrer||'')){ch.push('المحوِّل: '+(p.referrer||'—')+' ← '+(rv||'—'));p.referrer=rv}}if(base!==p.base){", 'edit save')
    s = s.rstrip(); assert s.endswith('</body></html>'), f
    s = s[:-len('</body></html>')] + LAYER + '\n'
    p.write_text(s, encoding='utf-8'); print('patched', f)
