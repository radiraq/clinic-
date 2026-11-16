#!/usr/bin/env python3
"""v0.5 changes for the doctor and secretary test screens (writer is rebuilt from doctor).
Run once; then run tools/make-writer.py."""
import pathlib, sys
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
DOC = ['doctor-test.html', 'doctor-karma-test.html']
SEC = ['secretary-test.html', 'secretary-karma-test.html']

def rep(s, old, new, f, n=1):
    c = s.count(old)
    if c != n: sys.exit(f'{f}: expected {n} of [{old[:70]}], found {c}')
    return s.replace(old, new)

EXAM_UI = ("d.append(row);\nconst exParts=String(p0.exam||'').split(' + ');"
 "const mkSel=(lbl,val,none)=>{const l=el('label',lbl);const s=el('select');if(none){const o=el('option','— بدون فحص ثاني');o.value='';s.append(o)}"
 "const names=examCatalog.map(x=>x.name);if(val&&!names.includes(val))names.unshift(val);names.forEach(n=>{const o=el('option',n);o.value=n;s.append(o)});"
 "s.value=val||'';s.style.width='100%';l.append(s);d.append(l);return s};"
 "const ex1=mkSel('🩺 نوع الفحص',exParts[0]),ex2=mkSel('＋ فحص ثاني (اختياري)',exParts[1]||'',true);"
 "d.append(el('small','تغيير الفحص ما يغيّر المبلغ المدفوع.','muted'));")
EXAM_SAVE = ("const newEx=ex1.value+(ex2.value&&ex2.value!==ex1.value?' + '+ex2.value:'');"
 "if(newEx&&newEx!==p.exam){changes.push('الفحص: '+p.exam+' ← '+newEx);p.exam=newEx}\n"
 "d.close();if(!changes.length)return toast('ما تغيّر شي');")

EXPENSE_OLD = "amount=Math.round(Number($('expenseAmount').value)*1000)"
EXPENSE_NEW = "amountK=Number(toAsciiDigits($('expenseAmount').value).trim()),amount=Math.round(amountK*1000)"
EXPENSE_CHECK_OLD = "if(!Number.isInteger(amount)||amount<5000||amount%5000!==0||amount>10000000)return void($('expenseError').textContent='اكتب المبلغ بالألف ومن مضاعفات 5 (مثال: 5، 10، 15).');"
EXPENSE_CHECK_NEW = ("if(!Number.isInteger(amountK)||amountK<1||amountK>10000)return void($('expenseError').textContent='اكتب المبلغ بالألف — رقم صحيح (مثال: 3 = ثلاث آلاف، 25 = خمسة وعشرين ألف).');"
 "if(amountK>=1000&&amountK%1000===0)return void($('expenseError').textContent='اكتب المبلغ بالألف بدون أصفار: مثلًا 25 مو 25000.');")

LAYER = r"""<style id="v05">
/* v0.5: colours + icons for actions, icon-only copy, phone-safe dialogs */
#rows button.b-in{background:#16724b!important;color:#fff!important;border-color:#16724b!important}
#rows button.b-in:disabled{opacity:.4}
#rows button.b-done{background:#1f5fa8!important;color:#fff!important;border-color:#1f5fa8!important}
#rows button.b-cancel{color:#ff8f8f!important;border-color:#ff8f8f66!important;background:transparent!important}
#rows button.b-defer{color:#f2b84b!important;border-color:#f2b84b66!important;background:transparent!important}
#rows button.b-back,#rows button.b-undo{color:#c2adff!important;border-color:#c2adff77!important;background:transparent!important}
#rows button.b-pay{background:#2f9e74!important;color:#fff!important;border-color:#2f9e74!important}
#rows button.b-refund{color:#f2b84b!important;border-color:#f2b84b66!important;background:transparent!important}
#rows button.b-edit{min-width:40px}
#rows .cp-both span{display:none}
#rows .cp-both{min-width:40px;justify-content:center;padding:6px 10px!important}
#rows .cp-both small{opacity:1!important;font-size:18px!important}
dialog{max-width:calc(100vw - 16px)!important;box-sizing:border-box;overflow-x:hidden}
dialog input,dialog select,dialog textarea{max-width:100%;box-sizing:border-box}
dialog .age-row{display:flex;gap:6px}dialog .age-row input{min-width:0;flex:1 1 0;width:auto!important}
dialog label{display:block;margin-top:10px}
.more-act{position:relative}
@media(max-width:760px){.more-act .menu{position:absolute;inset-inline-end:0;inset-inline-start:auto;max-width:calc(100vw - 24px);min-width:150px;z-index:20;box-sizing:border-box}.more-act .menu button{white-space:nowrap}}
</style>
<script id="v05js">
(function(){
 const MAP={'إدخال':['▶ إدخال','b-in','إدخال المريض للفحص'],'إنهاء':['✓ إنهاء','b-done','إنهاء الفحص'],'إلغاء الفحص':['✕ إلغاء','b-cancel','إلغاء الفحص'],'إلغاء':['✕ إلغاء','b-cancel','إلغاء الفحص'],
  'تأجيل':['⏱ تأجيل','b-defer','تأجيل المريض'],'إعادة للانتظار':['↩ للانتظار','b-back','إعادة المريض للانتظار'],'✓ رجع':['↩ رجع','b-back','المريض رجع'],
  'قبض':['💵 قبض','b-pay','قبض المبلغ'],'استرجاع مبلغ':['↺ استرجاع','b-refund','استرجاع مبلغ للمريض'],'✎ تعديل':['✎','b-edit','تعديل الاسم والعمر والهاتف والفحص'],'✎':['✎','b-edit','تعديل الاسم والعمر والهاتف والفحص']};
 window.backToWaiting=function(id){refreshSharedState();const p=list().find(x=>x.id===id);if(!p||p.status!=='داخل الفحص')return toast('المريض مو داخل الفحص');
  p.status='بانتظار الدخول';p.enteredAt=null;p.enteredBy=null;p.statusBy=roleName();p.statusAt=stamp();
  S.waitingOrder??={};const q=waitingQueue().map(x=>x.id).filter(x=>x!==p.id);S.waitingOrder[clinic()]=[p.id,...q];S.nextPatient??={};delete S.nextPatient[clinic()];
  audit('إرجاع '+p.name+' للانتظار (أول الدور)');render();toast('↩ رجع '+p.name+' للانتظار — أول الدور')};
 function tidy(){document.querySelectorAll('#rows tr').forEach(tr=>{
  tr.querySelectorAll('td:last-child button').forEach(b=>{if(b.classList.contains('cp')||b.dataset.v5)return;const m=MAP[b.textContent.trim()];if(!m)return;b.textContent=m[0];b.classList.remove('ghost');b.classList.add(m[1]);b.title=m[2];b.setAttribute('aria-label',m[2]);b.dataset.v5='1'});
  const both=tr.querySelector('.cp-both');if(both){both.title='نسخ الاسم والعمر';both.setAttribute('aria-label','نسخ الاسم والعمر')}
  const id=tr.dataset.id,p=id&&list().find(x=>x.id===id),td=tr.querySelector('td:last-child');
  if(p&&td&&p.status==='داخل الفحص'&&!td.querySelector('.b-undo')){const u=btn('↩ للانتظار',()=>backToWaiting(id));u.type='button';u.classList.add('b-undo');u.title='دخل بالغلط أو مو جاهز؟ يرجع للانتظار أول الدور';u.dataset.v5='1';const done=td.querySelector('.b-done');done?done.after(u):td.prepend(u)}
 })}
 const base=render;render=function(){const r=base.apply(this,arguments);try{tidy()}catch(e){console.error(e)}return r};try{tidy()}catch(e){}
})();
</script>
</body></html>"""

for f in DOC + SEC:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v05js"' in s: print('already', f); continue
    s = rep(s, "d.append(row);\nconst err=el('p','')", EXAM_UI + "\nconst err=el('p','')", f)
    s = rep(s, "d.close();if(!changes.length)return toast('ما تغيّر شي');", EXAM_SAVE, f)
    s = rep(s, EXPENSE_OLD, EXPENSE_NEW, f)
    s = rep(s, EXPENSE_CHECK_OLD, EXPENSE_CHECK_NEW, f)
    s = s.replace('<label>المبلغ (ألف دينار)<input id="expenseAmount" type="number" min="5" max="10000" step="5" required><small>بالألف — من مضاعفات 5 فقط (مثال: 15 = خمسة عشر ألف)</small>',
                  '<label>المبلغ (ألف دينار)<input id="expenseAmount" type="number" min="1" max="10000" step="1" required><small>بالألف بدون أصفار — أي رقم (مثال: 3 = ثلاث آلاف، 25 = خمسة وعشرين ألف)</small>')
    if f in SEC:
        s = rep(s, "$('discount').disabled=!admin()", "$('discount').disabled=false", f, 2)
        s = rep(s, "d>base||(!admin()&&d)||", "d>base||", f)
        s = rep(s, "filtered.forEach(p=>{let tr=el('tr')", "filtered.forEach(p=>{let tr=el('tr');tr.dataset.id=p.id", f)
    s = s.rstrip()
    if not s.endswith('</body></html>'): sys.exit(f + ': bad end')
    s = s[:-len('</body></html>')] + LAYER + '\n'
    p.write_text(s, encoding='utf-8'); print('patched', f)
