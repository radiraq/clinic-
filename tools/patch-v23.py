#!/usr/bin/env python3
"""v0.23 (all six test screens) — WhatsApp bookings: arrival and payment are separate.
- «✓ وصل» only puts the patient in the waiting queue; nothing is collected.
- On the secretary and writer screens a quick box asks «قبضتي X؟»; otherwise a red «💵 غير مدفوع» tag
  and a «💵 قبض» button stay on the row until the money is taken. The doctor screen never collects.
- Editing a booking (exam, price) never collects money by itself.
- A booking's money is never collected automatically (also not by the background reconcile)."""
import pathlib, time
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html',
         'secretary-karma-test.html', 'writer-test.html', 'writer-karma-test.html']
BUILD = time.strftime('%Y%m%d%H%M%S')

REPL = [
 # edit dialog: no automatic "difference" collection for an unpaid WhatsApp booking
 ("if(p.status!=='ملغي'){const net=Math.max(0,p.base-p.discount-(p.refunded||0)),diff=net-(p.paid||0);",
  "if(p.status!=='ملغي'&&!(p.wa&&!p.paid)){const net=Math.max(0,p.base-p.discount-(p.refunded||0)),diff=net-(p.paid||0);"),
 # bookings are never auto-collected
 ("const _ac=autoCollect;autoCollect=function(p){if(p&&p.wa&&!p.arrivedAt)return false;return _ac.apply(this,arguments)};",
  "const _ac=autoCollect;autoCollect=function(p){if(p&&p.wa)return false;return _ac.apply(this,arguments)};"),
 # arrival: queue only, then ask (secretary / writer)
 ("q.statusBy=roleName();q.statusAt=stamp();autoCollect(q);\n   audit('وصل '+q.name+' (حجز واتساب) — الدور '+q.no+(q.paid?' — قبض '+money(q.paid):''));render();toast('✓ وصل '+q.name+' • الدور '+q.no+(q.paid?' • انقبض '+money(q.paid):''));return}",
  "q.statusBy=roleName();q.statusAt=stamp();\n   audit('وصل '+q.name+' (حجز واتساب) — الدور '+q.no+' — غير مدفوع');render();toast('✓ وصل '+q.name+' • الدور '+q.no);if(window.__waCanCollect&&__waCanCollect())setTimeout(()=>window.__waAskCollect(q.id),250);return}"),
 # row buttons: hide the normal «قبض» on bookings; add «💵 قبض» + red tag after arrival
 ("else if(/قبض/.test(b.textContent)&&!/استرجاع/.test(b.textContent))b.remove()})})}",
  "else if(/قبض/.test(b.textContent)&&!/استرجاع/.test(b.textContent))b.remove()});"
  "row.querySelectorAll('button').forEach(b=>{if(/قبض/.test(b.textContent)&&!/استرجاع/.test(b.textContent)&&!b.classList.contains('wa-pay'))b.remove()});"
  "let un=row.querySelector('.wa-unpaid');const need=p.arrivedAt&&!p.paid&&!p.refunded&&p.status!=='ملغي'&&(p.base-(p.discount||0))>0;"
  "if(need&&!un){un=el('span','💵 غير مدفوع','wa-unpaid');row.querySelector('.wa-tag')?.after(un)}else if(!need&&un)un.remove();"
  "if(need&&window.__waCanCollect&&__waCanCollect()&&!row.querySelector('.wa-pay')){const pb=btn('💵 قبض '+money(p.base-(p.discount||0)),()=>window.__waAskCollect(p.id));pb.className='wa-pay';const anyBtn=row.querySelector('button');(anyBtn&&anyBtn.parentNode?anyBtn.parentNode:row).prepend(pb)}"
  "else if(!need)row.querySelector('.wa-pay')?.remove()})}"),
]
ADD = r"""<style id="v23css">.wa-unpaid{display:inline-block;margin-inline-start:6px;padding:1px 7px;border-radius:8px;background:#e5484d22;color:#ff6b6b;font-size:12px;font-weight:800;white-space:nowrap}.wa-pay{background:#e08a1e!important;color:#fff!important;border-color:#e08a1e!important;font-weight:800}</style>
<script id="v23js">
(function(){
 // Who may take money for a WhatsApp booking: the secretary and the writer (not the doctor screen).
 window.__waCanCollect=()=>roleName()==='السكرتارية'||roleName()==='الكاتبة'||role()==='secretary';
 function collect(id){refreshSharedState();const q=list().find(x=>x.id===id);if(!q||!q.wa||q.paid||q.refunded||q.status==='ملغي')return;const amt=q.base-(q.discount||0);if(!(amt>0))return;
  q.paid=amt;q.paidBy=roleName();q.paidAt=stamp();const lid='pay-'+q.id,old=S.ledger.find(l=>l._id===lid);
  if(old){old.amount=amt;old.label='قبض';old.by=roleName();old.at=stamp()}else S.ledger.push({_id:lid,at:stamp(),clinic:clinic(),patientId:q.id,amount:amt,label:'قبض',reason:q.name,by:roleName()});
  audit('قبض '+money(amt)+' — '+q.name+' (حجز واتساب)');render();toast('✓ انقبض '+money(amt)+' من '+q.name)}
 window.__waAskCollect=async function(id){if(!__waCanCollect())return;const q=list().find(x=>x.id===id);if(!q||q.paid)return;const amt=q.base-(q.discount||0);
  const ok=await askDialog('💵 قبضتي '+money(amt)+' من '+q.name+'؟ (إذا المبلغ غلط، اضغطي «تراجع» وعدّلي السعر من ✎ أول)',{ok:'✓ نعم قبضت'});if(ok)collect(id)};
})();
</script>
"""

for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v23js"' in s: print('already', f); continue
    for a, b in REPL:
        n = s.count(a); assert n == 1, (f, n, a[:70]); s = s.replace(a, b)
    old = s[s.index("BUILD='"):].split("'")[1]; s = s.replace("BUILD='%s'" % old, "BUILD='%s'" % BUILD)
    s = s.rstrip(); assert s.endswith('</body></html>')
    p.write_text(s[:-len('</body></html>')] + ADD + '</body></html>\n', encoding='utf-8'); print('patched', f)
(T / 'version.txt').write_text(BUILD + '\n')
print('BUILD', BUILD)
