#!/usr/bin/env python3
"""v0.6: full patient edit (name, phone, age, exam, price, discount) with automatic
cash adjustment; back-to-waiting keeps the patient's own turn. Doctor + secretary
screens; run tools/make-writer.py afterwards."""
import pathlib, sys
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html', 'secretary-karma-test.html']
LAYER = r"""<script id="v06js">
(function(){
 // Price of one exam for a given age (children under 10 use the child price).
 function priceOf(name,age){const x=examCatalog.find(x=>x.name===name);if(!x)return 0;return age!==null&&age!==undefined&&age<10?x.child:x.adult}
 const K=n=>Number.isFinite(n)?String(n/1000):'';
 window.editPatient=function(p0){const id=p0.id;let d=$('editDlg');if(!d){d=el('dialog');d.id='editDlg';d.style.width='min(480px,94vw)';document.body.append(d)}d.replaceChildren();
  const h=el('h2','✎ تعديل المريض — الدور '+p0.no);h.style.fontSize='18px';d.append(h);
  const field=(label,node)=>{const l=el('label',label);node.style.width='100%';l.append(node);d.append(l);return node};
  const inp=(val,ph,num)=>{const i=el('input');i.value=val??'';i.placeholder=ph||'';if(num){i.inputMode='numeric';i.dir='ltr';i.style.textAlign='right'}return i};
  const nm=field('👤 الاسم',inp(p0.name)),ph=field('📞 الهاتف (اختياري)',inp(p0.phone,'07XXXXXXXXX',true));
  d.append(el('small','🎂 العمر الحالي: '+(ageShow(p0)||'—')+' — اتركي الخانات فارغة إذا صحيح','muted'));
  const row=el('span',undefined,'age-row'),ay=inp('','سنة',1),am=inp('','شهر',1),ad=inp('','يوم',1);row.append(ay,am,ad);d.append(row);
  const parts=String(p0.exam||'').split(' + ');
  const sel=(val,none)=>{const s=el('select');if(none){const o=el('option','— بدون فحص ثاني');o.value='';s.append(o)}const names=examCatalog.map(x=>x.name);if(val&&!names.includes(val))names.unshift(val);names.forEach(n=>{const o=el('option',n);o.value=n;s.append(o)});s.value=val||'';return s};
  const ex1=field('🩺 الفحص',sel(parts[0])),ex2=field('＋ فحص ثاني (اختياري)',sel(parts[1]||'',true));
  const price=field('💵 السعر (ألف)',inp(K(p0.base),'',1)),disc=field('➖ الخصم (ألف)',inp(K(p0.discount||0),'0',1)),why=field('سبب الخصم',inp(p0.reason||''));
  const info=el('p','','muted');info.style.fontSize='13px';d.append(info);
  const ageNow=()=>{const v=[ay,am,ad].map(i=>{const t=toAsciiDigits(i.value).trim();return t===''?null:Number(t)});if(v.every(x=>x===null))return p0.age;return (v[0]||0)+(v[1]||0)/12+(v[2]||0)/365};
  const autoPrice=()=>{const a=ageNow();price.value=K(priceOf(ex1.value,a)+(ex2.value&&ex2.value!==ex1.value?priceOf(ex2.value,a):0));showInfo()};
  const showInfo=()=>{const b=Number(toAsciiDigits(price.value))*1000,dd=Number(toAsciiDigits(disc.value||'0'))*1000,net=Math.max(0,b-dd-(p0.refunded||0)),diff=net-(p0.paid||0);
   info.textContent=p0.status==='ملغي'?'':'المدفوع حاليًا '+money(p0.paid||0)+(diff>0?' • يستلم فرق +'+money(diff):diff<0?' • يرجع للمريض '+money(-diff):' • بدون فرق')};
  ex1.onchange=autoPrice;ex2.onchange=autoPrice;[price,disc].forEach(i=>i.oninput=showInfo);showInfo();
  const err=el('p','');err.style.color='#ff9a9a';d.append(err);const a=el('div',undefined,'actions');
  const ok=btn('✓ حفظ',()=>{const name=nm.value.trim();if(!name){err.textContent='اكتبي الاسم.';return}
   const phRaw=toAsciiDigits(ph.value).trim(),phone=phRaw?normPhone(phRaw):'';if(phRaw&&!phone){err.textContent='رقم الهاتف غير صحيح؛ مثل 07701234567.';return}
   const nums=[ay,am,ad].map(i=>{const v=toAsciiDigits(i.value).trim();if(v==='')return null;const n=Number(v);return Number.isFinite(n)&&n>=0?n:NaN});if(nums.some(Number.isNaN)){err.textContent='العمر أرقام فقط.';return}
   const base=Math.round(Number(toAsciiDigits(price.value).trim())*1000),dsc=Math.round(Number(toAsciiDigits(disc.value||'0').trim()||0)*1000),rsn=why.value.trim();
   if(!validPrice(base)){err.textContent='السعر بالألف ومن مضاعفات 5 (مثل 15، 20، 25) أو 0 للمجاني.';return}
   if(!Number.isInteger(dsc)||dsc<0||dsc%5000!==0||dsc>base){err.textContent='الخصم بالألف ومن مضاعفات 5 وما يزيد على السعر.';return}
   if(dsc&&!rsn){err.textContent='اكتبي سبب الخصم.';return}
   refreshSharedState();const p=list().find(x=>x.id===id);if(!p){d.close();return toast('المريض غير موجود')}const ch=[];
   if(name!==p.name){ch.push('الاسم: '+p.name+' ← '+name);p.name=name}
   if((phone||'')!==(p.phone||'')){ch.push('الهاتف: '+(p.phone||'—')+' ← '+(phone||'—'));p.phone=phone}
   if(nums.some(n=>n!==null)){const [y,m,dd]=nums;const yrs=(y||0)+(m||0)/12+(dd||0)/365;if(yrs>120){err.textContent='العمر غير صحيح.';return}const pr=[];if(y)pr.push(arCount(y,'سنة','سنوات'));if(m)pr.push(arCount(m,'شهر','أشهر'));if(dd)pr.push(arCount(dd,'يوم','أيام'));const lab=pr.length?pr.join(' و'):'حديث الولادة';if(lab!==p.ageLabel){ch.push('العمر: '+(ageShow(p)||'—')+' ← '+lab);p.age=Math.round(yrs*1000)/1000;p.ageLabel=lab}}
   const exam=ex1.value+(ex2.value&&ex2.value!==ex1.value?' + '+ex2.value:'');if(exam&&exam!==p.exam){ch.push('الفحص: '+p.exam+' ← '+exam);p.exam=exam}
   if(base!==p.base){ch.push('السعر: '+money(p.base)+' ← '+money(base));p.base=base;p.priceEdited=true}
   if(dsc!==(p.discount||0)||(dsc&&rsn!==(p.reason||''))){ch.push('الخصم: '+money(p.discount||0)+' ← '+money(dsc)+(rsn?' ('+rsn+')':''));p.discount=dsc;p.reason=rsn}
   if(p.status!=='ملغي'){const net=Math.max(0,p.base-p.discount-(p.refunded||0)),diff=net-(p.paid||0);
    if(diff){const at=stamp();S.ledger.push({id:uid(),at,clinic:clinic(),patientId:p.id,amount:diff,label:diff>0?'قبض فرق':'استرداد',reason:p.name+' — تعديل الفحص/السعر',by:roleName()});p.paid=net;ch.push(diff>0?'استلام فرق '+money(diff):'إرجاع '+money(-diff)+' للمريض')}}
   d.close();if(!ch.length)return toast('ما تغيّر شي');p.editedBy=roleName();p.editedAt=stamp();audit('تعديل '+p.name+' — '+ch.join(' • '));render();toast('✓ تم الحفظ')});
  ok.type='button';ok.className='primary';const no=btn('تراجع',()=>d.close());no.type='button';a.append(ok,no);d.append(a);d.oncancel=e=>{e.preventDefault();d.close()};d.showModal();nm.focus()};
 // Back to waiting: return to the patient's own place by turn number.
 window.backToWaiting=function(id){refreshSharedState();const p=list().find(x=>x.id===id);if(!p||p.status!=='داخل الفحص')return toast('المريض مو داخل الفحص');
  p.status='بانتظار الدخول';p.enteredAt=null;p.enteredBy=null;p.statusBy=roleName();p.statusAt=stamp();
  S.waitingOrder??={};const q=waitingQueue().map(x=>x.id).filter(x=>x!==p.id);const i=q.findIndex(x=>{const o=list().find(y=>y.id===x);return o&&o.no>p.no});q.splice(i<0?q.length:i,0,p.id);S.waitingOrder[clinic()]=q;
  S.nextPatient??={};delete S.nextPatient[clinic()];audit('إرجاع '+p.name+' للانتظار (بدوره رقم '+p.no+')');render();toast('↩ رجع '+p.name+' للانتظار بدوره ('+p.no+')')};
})();
</script>
</body></html>"""
for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v06js"' in s: print('already', f); continue
    s = s.rstrip(); assert s.endswith('</body></html>'), f
    s = s[:-len('</body></html>')] + LAYER + '\n'
    s = s.replace("u.title='دخل بالغلط أو مو جاهز؟ يرجع للانتظار أول الدور'", "u.title='دخل بالغلط أو مو جاهز؟ يرجع للانتظار بنفس دوره'")
    p.write_text(s, encoding='utf-8'); print('patched', f)
