#!/usr/bin/env python3
"""v0.31 (secretary screens, Fallujah and Al-Karma; writer + doctor: build stamp only) — compact, consistent patient
cards on the phone + call buttons.
Advisory board (2026-11-24): every card on a phone has the same four lines, whatever the
booking type:
  1) turn number ............ one time chip (⏳ waiting, or 🕒 booking time if not arrived yet)
  2) name (+ التالي) and a small line: exam • age • phone
  3) small chips: booking type, status / appointment, price + paid / not paid (one chip)
  4) one action row: the main action is the only wide button (وصل / إدخال / إنهاء / قبض),
     then small buttons: 🟢 رابط, 📞 (call menu), ⋯
Removed duplicates: the separate «💵 ما دافع» badge (the price chip says it), the 🕒 time when
⏳ is shown, the full-width «رابط الحجز» button.
New: «📞» menu next to the WhatsApp link, only when the patient has a valid phone:
  ☎️ اتصال عادي  -> tel:+964…  (opens the phone dialer)
  🟢 اتصال واتساب -> opens the patient's WhatsApp chat (wa.me, no text); the call button is at
     the top of the chat. WhatsApp has no public link that starts a call directly.
Each call is written to the audit log. Desktop table keeps its columns."""
import pathlib, time
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['secretary-test.html', 'secretary-karma-test.html']
BUILD = time.strftime('%Y%m%d%H%M%S')

ADD = r"""<style id="v31css">
#rows .call-act>summary{list-style:none;cursor:pointer;color:#60a5fa;border:1px solid #3b82f666;border-radius:9px}
#rows .call-act>summary::-webkit-details-marker{display:none}
#rows .call-act .menu{display:flex;flex-direction:column;gap:6px;padding:8px;background:var(--paper);border:1px solid var(--line);border-radius:10px;box-shadow:0 6px 20px #0006}
#rows .call-act .menu button{font-size:14px;padding:10px 12px;text-align:right}
#rows .call-act .c-tel{background:#2563eb;color:#fff;border-color:#2563eb}
#rows .call-act .c-wa{background:#1f9d55;color:#fff;border-color:#1f9d55}
@media(max-width:760px){
 #rows tr[data-id]{display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:10px 12px;margin-bottom:8px;border-inline-start:4px solid transparent;contain:inline-size;box-sizing:border-box}
 #rows tr[data-id^="wa-"]{border-inline-start-color:#25a35a}
 #rows tr.tel-row{border-inline-start-color:#3b82f6}
 #rows tr[data-id]>td:first-child{box-shadow:none!important}
 /* 1: number + one time chip */
 #rows tr[data-id]>td.num{order:1;flex:1 1 100%;display:flex;align-items:center;gap:8px;font-size:15px;font-weight:800}
 #rows tr[data-id]>td.num .reg-t,#rows tr[data-id]>td.num .reg-e{margin:0 auto 0 0;font-size:12px;font-weight:700}
 #rows tr[data-id]:not(.m-booked)>td.num .reg-e~.reg-t,#rows tr[data-id]:not(.m-booked)>td.num .reg-t:has(~.reg-e){display:none}
 #rows tr.m-booked>td.num .reg-e{display:none}
 /* 2: name + small details line (the name cell is flattened so its pieces can line up) */
 #rows tr[data-id]>td.m-name{display:contents}
 #rows tr[data-id]>td.m-name>b{order:2;flex:1 1 100%;font-size:16px;line-height:1.3}
 #rows tr[data-id]>td.m-name>small{order:3;flex:1 1 100%;margin-top:-4px;opacity:.75;font-size:12px}
 /* 3: small chips */
 #rows tr[data-id]>td.m-name>.wa-tag{order:4;margin:0;font-size:11px}
 #rows tr[data-id] .wa-unpaid,#rows tr[data-id] .tel-unpaid{display:none}
 #rows tr[data-id]>td.m-st{order:4;flex:0 1 auto;display:flex;flex-wrap:wrap;align-items:center;gap:4px}
 #rows tr[data-id]>td.m-st:empty{display:none}
 #rows tr[data-id]>td.m-st .badge{font-size:11px;padding:2px 8px}
 #rows tr[data-id]>td.m-st small{font-size:11px;opacity:.75}
 #rows tr[data-id]>td.m-st .wa-when{font-size:11px!important;padding:2px 8px!important}
 #rows tr[data-id]>td.m-pay{order:4;flex:0 0 auto;display:inline-flex;align-items:center;gap:5px;padding:2px 8px;border-radius:8px;background:#ffffff10;font-size:11px}
 #rows tr[data-id]>td.m-pay b{display:inline;font-size:12px}
 #rows tr[data-id]>td.m-pay small{font-size:11px}
 #rows tr[data-id]>td.m-pay small~small{display:none}
 #rows tr[data-id]>td.m-pay.unpaid{background:#e5484d22;color:#ff8080}
 #rows tr[data-id]>td.m-pay.paid small{display:none}
 #rows tr[data-id]>td.m-pay.paid::after{content:'✓ مدفوع';color:#7bdbc2}
 /* 4: one action row */
 #rows tr[data-id]>td.m-act{order:5;flex:1 1 100%;display:flex;flex-wrap:wrap;align-items:stretch;gap:5px;margin-top:4px}
 #rows tr[data-id]>td.m-act>*{flex:0 0 auto;min-width:0!important}
 #rows tr[data-id]>td.m-act>button{padding:8px 7px!important;font-size:13px!important;min-height:40px;white-space:nowrap}
 #rows tr[data-id]>td.m-act>button.m-main{flex:1 1 0;overflow:hidden;text-overflow:ellipsis;min-width:80px!important;font-size:15px!important;font-weight:800}
 #rows tr[data-id]>td.m-act>.wa-link-btn{order:6}
 #rows tr[data-id]>td.m-act>.call-act{order:7}
 #rows tr[data-id]>td.m-act>.more-act:not(.call-act){order:8}
 #rows tr[data-id]>td.m-act>details>summary{min-width:38px;padding:0 4px;min-height:40px;display:flex;align-items:center;justify-content:center;box-sizing:border-box}
 #rows tr[data-id]>td.m-act .wa-link-btn .m-long{display:none}
}
@media(max-width:379px){#rows tr[data-id]>td.m-act .wa-link-btn .m-word{display:none}}
</style>
<script id="v31js">
(function(){
 // Phone cards: same four lines on every card; «📞» call menu (normal call / WhatsApp call).
 const MAIN=['b-arrive','b-in','b-done','wa-pay','b-pay'];
 function waNum(ph){const d=normPhone(ph||'');return d?'964'+d.slice(1):''}
 function go(url){if(window.AndroidBell||url.startsWith('tel:')){location.href=url}else{const w=window.open(url,'_blank');if(!w)location.href=url}}
 function call(p,how){const n=waNum(p.phone);if(!n)return toast('رقم الهاتف غير صحيح');
  if(how==='tel')go('tel:+'+n);else go('https://wa.me/'+n);
  try{audit((how==='tel'?'☎️ اتصال عادي':'🟢 اتصال واتساب')+' — '+p.name)}catch(e){}}
 function callMenu(p){const d=el('details',undefined,'more-act call-act');const s=el('summary','📞');s.title='اتصال بالمريض';s.setAttribute('aria-label','اتصال بالمريض');d.append(s);const m=el('div',undefined,'menu');
  const a=el('button','☎️ اتصال عادي','c-tel');a.type='button';a.onclick=ev=>{ev.stopPropagation();d.open=false;call(p,'tel')};
  const b=el('button','🟢 اتصال واتساب','c-wa');b.type='button';b.title='يفتح محادثة المريض بالواتساب — اضغطي زر الاتصال فوق';b.onclick=ev=>{ev.stopPropagation();d.open=false;call(p,'wa')};
  m.append(a,b);d.append(m);return d}
 function tidy(){document.querySelectorAll('#rows tr[data-id]').forEach(tr=>{const p=S.patients.find(x=>x.id===tr.dataset.id);if(!p)return;const tds=[...tr.children];if(tds.length<5)return;
  const [num,name,st,pay,act]=[tds[0],tds[1],tds[2],tds[3],tds[tds.length-1]];
  name.classList.add('m-name');st.classList.add('m-st');act.classList.add('m-act');
  // buttons that landed in the name / price cells go to the action row, main action first
  [name,st,pay].forEach(td=>td.querySelectorAll(':scope>button').forEach(b=>act.prepend(b)));
  const main=[...act.querySelectorAll(':scope>button')].find(b=>MAIN.some(c=>b.classList.contains(c)));
  act.querySelectorAll(':scope>button.m-main').forEach(b=>{if(b!==main)b.classList.remove('m-main')});
  if(main){main.classList.add('m-main');act.prepend(main)}
  // price + paid state as one chip
  const due=(p.base||0)-(p.discount||0);pay.classList.add('m-pay');
  pay.classList.toggle('unpaid',due>0&&!p.paid&&!p.refunded&&p.status!=='ملغي');pay.classList.toggle('paid',!!p.paid&&!p.refunded&&due>0);
  tr.classList.toggle('m-booked',!!(p.wa&&!p.arrivedAt&&p.status==='مؤجل'));
  const wl=act.querySelector('.wa-link-btn');if(wl&&!wl.querySelector('.m-long')){const sent=wl.classList.contains('sent');wl.replaceChildren(document.createTextNode(sent?'✓':'🟢'),el('span',sent?' الرابط':' رابط','m-word'),el('span',sent?'':' الحجز','m-long'))}
  const ok=!!waNum(p.phone);let c=act.querySelector('.call-act');
  if(ok&&!c){c=callMenu(p);const more=act.querySelector('.more-act:not(.call-act)');more?act.insertBefore(c,more):act.append(c)}else if(!ok&&c)c.remove()})}
 document.addEventListener('click',e=>{document.querySelectorAll('#rows details.call-act[open]').forEach(d=>{if(!d.contains(e.target))d.open=false})});
 const _r=render;render=function(){const r=_r.apply(this,arguments);try{tidy()}catch(e){console.error(e)}return r};
 try{tidy()}catch(e){}
})();
</script>
"""

ALL = FILES + ['writer-test.html', 'writer-karma-test.html', 'doctor-test.html', 'doctor-karma-test.html']  # build stamp only
for f in ALL:
    p = T / f; s = p.read_text(encoding='utf-8')
    old0 = s[s.index("BUILD='"):].split("'")[1]
    if f not in FILES:
        p.write_text(s.replace("BUILD='%s'" % old0, "BUILD='%s'" % BUILD), encoding='utf-8'); print('stamped', f); continue
    if 'id="v31js"' in s: print('already', f); continue
    s = s.replace("BUILD='%s'" % old0, "BUILD='%s'" % BUILD)
    s = s.rstrip(); assert s.endswith('</body></html>')
    p.write_text(s[:-len('</body></html>')] + ADD + '</body></html>\n', encoding='utf-8'); print('patched', f)
(T / 'version.txt').write_text(BUILD + '\n')
print('BUILD', BUILD)
