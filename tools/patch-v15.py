#!/usr/bin/env python3
"""v0.15:
1) Any screen (secretary, writer, doctor) can add a new exam from the registration list
   («＋ فحص جديد…»): name + price; saved to the shared catalog.
2) Previous surgeries (عمليات سابقة): pick a body area, then the operation, side, biopsy
   result (حميد/خبيث/ما معروف), later treatment (يود مشع/إشعاع/كيمياوي), year and a note.
   Unusual operations can be typed and are added to the shared list
   (config/main.surgeriesCustom). Editable from ✎ تعديل.
3) Previous visit (مراجعة سابقة): لا / نعم لنفس الفحص / نعم لفحص آخر — filled
   automatically when the phone number matches an earlier visit, editable.
Shown in today's list and the doctor's now/next cards. Doctor + secretary screens;
run tools/make-writer.py afterwards."""
import pathlib, sys
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html', 'secretary-karma-test.html']

def must(s, old, new, what):
    n = s.count(old)
    if n != 1: sys.exit(f'patch-v15: expected 1 of [{what}], found {n}')
    return s.replace(old, new)

LAYER = r"""<style id="v15css">
.sg-box{display:flex;flex-direction:column;gap:6px}.sg-list{display:flex;flex-wrap:wrap;gap:6px}
.sg-chip{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line);background:var(--bg);border-radius:9px;padding:5px 9px;font-size:13px;line-height:1.5}
.sg-chip button{padding:1px 7px;font-size:12px}.sg-add{align-self:flex-start;padding:7px 12px;font-size:13px}
.hx-tag{display:inline-block;font-size:12px;font-weight:600;border-radius:7px;padding:1px 7px;margin-inline-start:6px;margin-top:3px}
.hx-pv{color:#fde9c8;background:#5a3a12}.hx-sg{color:#fbdde4;background:#5b2230;white-space:normal}
body:not(.dark) .hx-pv{color:#7a4a0c;background:#fde9c8}body:not(.dark) .hx-sg{color:#7a1f33;background:#fbdde4}
#nowCard .nc-h{display:block;margin-top:6px;font-size:14px;font-weight:700;line-height:1.6}#nowCard .nc-h .hx-tag{font-size:13px;margin:2px 0 0 6px}
.v15dlg label{display:block;margin:8px 0 3px;font-size:13px;color:var(--muted)}.v15dlg select,.v15dlg input{width:100%}.v15dlg .tx{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:4px}.v15dlg .tx label{display:inline-flex;align-items:center;gap:5px;margin:0;color:var(--ink);font-size:14px}.v15dlg .tx input{width:auto}
</style>
<script id="v15js">
(function(){
 const CFG=()=>FB.doc(cloud.db,'clinics',CLINIC_ID,'config','main');
 S.surgCustom=S.surgCustom||{};
 // ---------- 1) New exam from the registration list ----------
 const NEWX='__newexam__';
 function dlg(title){let d=$('v15dlg');if(!d){d=el('dialog');d.id='v15dlg';d.className='v15dlg';d.style.width='min(460px,94vw)';document.body.append(d)}d.replaceChildren();const h=el('h2',title);h.style.fontSize='18px';d.append(h);d.oncancel=e=>{e.preventDefault();d.close()};return d}
 function addExam(){return new Promise(res=>{const d=dlg('＋ فحص جديد');const lab=t=>{const l=el('label',t);d.append(l);return l};
  lab('اسم الفحص');const nm=el('input');nm.maxLength=100;nm.placeholder='مثال: سونار الكتف';d.append(nm);
  lab('السعر (ألف دينار) — من مضاعفات 5');const pr=el('input');pr.inputMode='numeric';pr.dir='ltr';pr.style.textAlign='right';pr.placeholder='20';d.append(pr);
  lab('سعر الأطفال أقل من ١٠ سنوات (اختياري — إذا فارغ نفس السعر)');const pc=el('input');pc.inputMode='numeric';pc.dir='ltr';pc.style.textAlign='right';d.append(pc);
  const err=el('p','');err.style.color='#ff9a9a';d.append(err);const a=el('div',undefined,'actions');
  const ok=btn('✓ إضافة',()=>{const name=nm.value.replace(/\s+/g,' ').trim(),p=Number(toAsciiDigits(pr.value).trim())*1000,c=pc.value.trim()?Number(toAsciiDigits(pc.value).trim())*1000:p;
   if(!name){err.textContent='اكتبي اسم الفحص.';return}if(examCatalog.some(x=>normText(x.name)===normText(name))){err.textContent='الفحص موجود بالقائمة.';return}
   if(![p,c].every(n=>Number.isInteger(n)&&n>=5000&&n<=2000000&&n%5000===0)){err.textContent='السعر بالألف ومن مضاعفات 5 (مثل 15، 20، 25).';return}
   examCatalog=examCatalog.concat({name,child:c,adult:p});try{localStorage.setItem(CATALOG_KEY,JSON.stringify(examCatalog))}catch{}pushCatalog();refreshExamOptions();if(typeof renderCatalog==='function')try{renderCatalog()}catch(e){}
   audit('إضافة فحص جديد — '+name+' ('+money(p)+(c!==p?'، الأطفال '+money(c):'')+')');toast('✓ انضاف «'+name+'»');d.close();res(name)});ok.type='button';ok.className='primary';
  const no=btn('تراجع',()=>{d.close();res('')});no.type='button';a.append(ok,no);d.append(a);d.onclose=()=>res('');d.showModal();nm.focus()})}
 const baseRefresh=refreshExamOptions;refreshExamOptions=function(){const r=baseRefresh.apply(this,arguments);['exam','exam2'].forEach(id=>{const s=$(id);if(!s||[...s.options].some(o=>o.value===NEWX))return;const o=el('option','＋ فحص جديد…');o.value=NEWX;s.append(o)});return r};
 ['exam','exam2'].forEach(id=>{const s=$(id);if(!s)return;let prev=s.value;s.addEventListener('focus',()=>{if(s.value!==NEWX)prev=s.value});
  s.addEventListener('change',async e=>{if(s.value!==NEWX){prev=s.value;return}e.stopImmediatePropagation();s.value=prev;const n=await addExam();if(n){s.value=n;prev=n}s.dispatchEvent(new Event('change'))},true)});
 refreshExamOptions();if($('exam2')&&!$('exam2').options.length)$('exam2').innerHTML=$('exam').innerHTML;
 // ---------- 2) Previous surgeries ----------
 const AREAS={
  'البطن':['استئصال المرارة','استئصال الزائدة','تصليح فتق','تكميم أو تحويل مسار المعدة','استئصال الطحال','عملية بالكبد','عملية بالأمعاء أو القولون','فتح بطن'],
  'الرقبة والغدة':['استئصال الغدة الدرقية الكلي','استئصال فص من الغدة الدرقية','استئصال الغدة جار الدرقية','استئصال عقد لمفاوية بالرقبة','استئصال الغدة النكفية','استئصال الغدة تحت الفك'],
  'الحوض والنسائية':['عملية قيصرية','استئصال الرحم','استئصال المبيض','استئصال كيس مبيض','استئصال ليفة رحمية','ناظور نسائي','ربط الأنابيب'],
  'الكلى والمسالك':['استئصال كلية','إخراج أو تفتيت حصى كلية','ناظور حالب','دبل جي (DJ stent)','استئصال أو كشط البروستات','عملية بالمثانة','زراعة كلية'],
  'الثدي':['استئصال الثدي','استئصال كتلة من الثدي','خزعة ثدي'],
  'الخصية':['عملية دوالي الخصية','عملية قيلة مائية','تنزيل خصية معلقة','استئصال خصية','عملية فتق إربي'],
  'أخرى':[]};
 const RESULTS=['حميد','خبيث','ما معروف'],TX=['يود مشع','علاج إشعاعي','علاج كيمياوي'],SIDES=['يمين','يسار','الجهتين'];
 function opsOf(area){return (AREAS[area]||[]).concat(((S.surgCustom||{})[area])||[]).filter((x,i,a)=>a.indexOf(x)===i)}
 async function addCustomOp(area,op){try{const snap=await FB.getDoc(CFG());const cur=(snap.exists()&&snap.data().surgeriesCustom)||{};const l=cur[area]||[];if(!l.includes(op)&&!(AREAS[area]||[]).includes(op)){cur[area]=l.concat(op);await FB.setDoc(CFG(),{surgeriesCustom:cur},{merge:true});S.surgCustom=cur;audit('إضافة عملية للقائمة — '+area+': '+op)}}catch(err){console.error(err)}}
 window.surgText=function(x){return [x.op+(x.side?' ('+x.side+')':''),x.result&&x.result!=='ما معروف'?x.result:x.result?'النتيجة ما معروفة':'',(x.tx||[]).join(' + '),x.year?'سنة '+x.year:'',x.note||''].filter(Boolean).join(' — ')};
 function surgDialog(init){return new Promise(res=>{const d=dlg('🩹 عملية سابقة');const lab=t=>{const l=el('label',t);d.append(l);return l};const opt=(s,v,t)=>{const o=el('option',t??v);o.value=v;s.append(o)};
  lab('المنطقة');const ar=el('select');Object.keys(AREAS).forEach(a=>opt(ar,a));d.append(ar);
  lab('العملية');const op=el('select');d.append(op);const other=el('input');other.placeholder='اكتبي اسم العملية';other.maxLength=80;other.style.marginTop='6px';d.append(other);
  const fillOps=v=>{op.replaceChildren();opsOf(ar.value).forEach(o=>opt(op,o));opt(op,'__other__','＋ عملية ثانية (أكتبها)…');op.value=v&&opsOf(ar.value).includes(v)?v:(opsOf(ar.value)[0]||'__other__');other.style.display=op.value==='__other__'?'':'none'};
  ar.onchange=()=>fillOps('');op.onchange=()=>{other.style.display=op.value==='__other__'?'':'none';if(op.value==='__other__')other.focus()};
  lab('الجهة (إذا تنطبق)');const sd=el('select');opt(sd,'','—');SIDES.forEach(x=>opt(sd,x));d.append(sd);
  lab('نتيجة الخزعة / الفحص النسيجي');const rs=el('select');opt(rs,'','— ما مسوية أو ما تنطبق');RESULTS.forEach(x=>opt(rs,x));d.append(rs);
  lab('علاج بعد العملية');const tx=el('div',undefined,'tx');const boxes=TX.map(t=>{const l=el('label'),c=el('input');c.type='checkbox';c.value=t;l.append(c,' '+t);tx.append(l);return c});d.append(tx);
  lab('سنة العملية (اختياري)');const yr=el('input');yr.inputMode='numeric';yr.dir='ltr';yr.style.textAlign='right';yr.placeholder='مثال: 2021';yr.maxLength=4;d.append(yr);
  lab('ملاحظة (اختياري)');const nt=el('input');nt.maxLength=120;d.append(nt);
  if(init){ar.value=init.area in AREAS?init.area:'أخرى';fillOps(init.op);if(!opsOf(ar.value).includes(init.op)){op.value='__other__';other.style.display='';other.value=init.op}sd.value=init.side||'';rs.value=init.result||'';boxes.forEach(b=>b.checked=(init.tx||[]).includes(b.value));yr.value=init.year||'';nt.value=init.note||''}else fillOps('');
  const err=el('p','');err.style.color='#ff9a9a';d.append(err);const a=el('div',undefined,'actions');
  const ok=btn('✓ حفظ',()=>{const name=op.value==='__other__'?other.value.replace(/\s+/g,' ').trim():op.value;if(!name){err.textContent='اختاري أو اكتبي العملية.';return}
   const y=toAsciiDigits(yr.value).trim();if(y&&!/^(19|20)\d\d$/.test(y)){err.textContent='السنة مثل 2021.';return}
   const x={area:ar.value,op:name,side:sd.value,result:rs.value,tx:boxes.filter(b=>b.checked).map(b=>b.value),year:y,note:nt.value.trim()};
   if(op.value==='__other__')addCustomOp(ar.value,name);d.close();res(x)});ok.type='button';ok.className='primary';
  const no=btn('تراجع',()=>{d.close();res(null)});no.type='button';a.append(ok,no);d.append(a);d.onclose=()=>res(null);d.showModal()})}
 // An editable block: chips + «＋ إضافة عملية». block.value is the list.
 window.surgBlock=function(list){const wrap=el('div',undefined,'sg-box');let L=(list||[]).map(x=>({...x}));const h=el('label','🩹 عمليات سابقة');wrap.append(h);const box=el('div',undefined,'sg-list');wrap.append(box);
  const draw=()=>{box.replaceChildren();if(!L.length)box.append(el('small','ماكو','muted'));L.forEach((x,i)=>{const c=el('span',surgText(x),'sg-chip');const e=btn('✎',async()=>{const r=await surgDialog(x);if(r){L[i]=r;draw()}});e.type='button';const k=btn('✕',()=>{L.splice(i,1);draw()});k.type='button';c.append(e,k);box.append(c)})};
  const add=btn('＋ إضافة عملية',async()=>{const r=await surgDialog(null);if(r){L.push(r);draw()}});add.type='button';add.className='sg-add';wrap.append(add);
  Object.defineProperty(wrap,'value',{get:()=>L.map(x=>({...x})),set:v=>{L=(v||[]).map(x=>({...x}));draw()}});draw();return wrap};
 // ---------- 3) Previous visit ----------
 const PV={'':'— ما معروف',no:'لا — أول مرة',same:'نعم — لنفس الفحص',other:'نعم — لفحص آخر'};
 window.pvSelect=function(v){const s=el('select');Object.entries(PV).forEach(([k,t])=>{const o=el('option',t);o.value=k;s.append(o)});s.value=v||'';return s};
 window.pvText=function(p){return p.prevVisit==='same'?'🔁 راجع قبل لنفس الفحص':p.prevVisit==='other'?'🔁 راجع قبل لفحص آخر':''};
 // ---------- Registration form ----------
 let regSg=null,regPv=null,history=[];
 (function mount(){const ref=$('referrer');const anchor=ref?ref.closest('label'):$('age')&&$('age').closest('label');if(!anchor)return;
  const l=el('label','🔁 عنده مراجعة سابقة عدنا؟');l.className='full';regPv=pvSelect('');regPv.id='prevVisit';l.append(regPv);const hint=el('small','','muted');hint.id='pvHint';l.append(hint);
  regSg=surgBlock([]);regSg.classList.add('full');anchor.after(l,regSg)})();
 function samePart(a,b){const A=String(a||'').split(' + '),B=String(b||'').split(' + ');return A.some(x=>B.includes(x))}
 function autoPv(){if(!regPv||!history.length)return;const ex=$('exam').value+($('twoExams')&&$('twoExams').checked?' + '+$('exam2').value:'');const same=history.find(h=>samePart(h.exam,ex));
  regPv.value=same?'same':'other';$('pvHint').textContent=same?'آخر مرة لنفس الفحص: '+same.day:'آخر زيارة: '+history[0].day+' ('+history[0].exam+')'}
 $('phone').addEventListener('input',()=>{history=[];if($('pvHint'))$('pvHint').textContent='';const ph=normPhone($('phone').value);if(!ph||!cloud.db||!cloud.user)return;
  setTimeout(async()=>{try{if(normPhone($('phone').value)!==ph)return;const snap=await FB.getDocs(FB.query(FB.collection(cloud.db,'clinics',CLINIC_ID,'patients'),FB.where('phone','==',ph),FB.limit(30)));if(normPhone($('phone').value)!==ph)return;
   history=snap.docs.map(d=>d.data()).filter(p=>p.status!=='ملغي'&&p.day!==day()).sort((a,b)=>String(b.day).localeCompare(String(a.day)));if(history.length)autoPv();else if(regPv&&!regPv.value){regPv.value='no';$('pvHint').textContent='ما لگينا زيارة سابقة بهذا الرقم'}}catch(e){console.error(e)}},500)});
 ['exam','exam2','twoExams'].forEach(id=>$(id)&&$(id).addEventListener('change',()=>setTimeout(autoPv,0)));
 $('patientForm').addEventListener('reset',()=>setTimeout(()=>{if(regSg)regSg.value=[];if(regPv)regPv.value='';history=[];if($('pvHint'))$('pvHint').textContent=''},0));
 window.__regExtra=function(){return{surgeries:regSg?regSg.value:[],prevVisit:regPv?regPv.value:''}};
 // ---------- Show in today's list and the now/next cards ----------
 function tags(p){const t=[];const pv=pvText(p);if(pv)t.push(['hx-tag hx-pv',pv]);if((p.surgeries||[]).length)t.push(['hx-tag hx-sg','🩹 '+p.surgeries.map(surgText).join(' • ')]);return t}
 function put(host,p,cls){let w=host.querySelector('.'+cls);const t=p?tags(p):[];const key=JSON.stringify(t);if(!t.length){if(w)w.remove();return}if(w&&w.dataset.k===key)return;if(!w){w=el('span','',cls);host.append(w)}w.dataset.k=key;w.replaceChildren(...t.map(([c,x])=>el('span',x,c)))}
 function run(){document.querySelectorAll('#rows tr[data-id]').forEach(tr=>{const p=list().find(x=>x.id===tr.dataset.id),td=tr.querySelector('td:nth-child(2)');if(td)put(td,p,'hx-row')});
  const c=$('nowCard');if(c){const inside=list().find(p=>p.status==='داخل الفحص'||(typeof OUT!=='undefined'&&p.status===OUT));let next=null;try{next=nextPatient()}catch(e){}
   [[c.querySelector('.nc-in'),inside],[c.querySelector('.nc-next'),next]].forEach(([b,p])=>{if(b)put(b,p,'nc-h')})}}
 // ---------- Live custom-operation list ----------
 let un=null;function attach(){if(!cloud.db||!cloud.user||(un&&cloud.unsubs.includes(un)))return;un=FB.onSnapshot(CFG(),s=>{const x=s.data()||{};S.surgCustom=x.surgeriesCustom||{}},()=>{});cloud.unsubs.push(un)}
 setInterval(attach,3000);attach();
 const base=render;render=function(){const r=base.apply(this,arguments);try{run()}catch(e){console.error(e)}return r};setInterval(()=>{try{run()}catch(e){}},5000);try{run()}catch(e){}
})();
</script>
</body></html>"""

for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v15js"' in s: print('already', f); continue
    # Registration: save surgeries + previous visit with the patient.
    s = must(s, "regBy:roleName(),regAt:stamp(),referrer:", "regBy:roleName(),regAt:stamp(),...(window.__regExtra?__regExtra():{}),referrer:", 'push')
    # Edit dialog: previous visit + surgeries.
    s = must(s, "const rf=field('👨‍⚕️ الطبيب المحوِّل',refSelect(p0.referrer||'')),",
             "const rf=field('👨‍⚕️ الطبيب المحوِّل',refSelect(p0.referrer||'')),pv=field('🔁 مراجعة سابقة',pvSelect(p0.prevVisit||'')),sgw=(d.append(surgBlock(p0.surgeries||[])),d.lastChild),", 'edit fields')
    s = must(s, "{const rv=rf.value==='__new__'?'':rf.value;",
             "if((pv.value||'')!==(p.prevVisit||'')){ch.push('المراجعة السابقة: '+(pvText(p)||'—')+' ← '+(pvText({prevVisit:pv.value})||'—'));p.prevVisit=pv.value}"
             "{const nv=sgw.value;if(JSON.stringify(nv)!==JSON.stringify(p.surgeries||[])){ch.push('العمليات السابقة: '+(nv.map(surgText).join(' • ')||'ماكو'));p.surgeries=nv}}"
             "{const rv=rf.value==='__new__'?'':rf.value;", 'edit save')
    s = s.rstrip(); assert s.endswith('</body></html>'), f
    s = s[:-len('</body></html>')] + LAYER + '\n'
    p.write_text(s, encoding='utf-8'); print('patched', f)
