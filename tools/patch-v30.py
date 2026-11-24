#!/usr/bin/env python3
"""v0.30 (secretary + writer screens, Fallujah and Al-Karma) — «🟢 رابط الحجز» button.
Next to every patient who has a phone number in today's list, a WhatsApp button opens
WhatsApp on the same device, on that patient's chat, with the booking-link message ready.
The secretary only presses Send. After pressing, the button turns to «✓ الرابط» (saved on
the patient record: waLinkAt / waLinkBy, plus an audit line) so it is not sent twice;
it can still be pressed again if needed. Free: a normal WhatsApp message, no Meta template,
no n8n execution."""
import pathlib, time
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['secretary-test.html', 'secretary-karma-test.html', 'writer-test.html', 'writer-karma-test.html']
BUILD = time.strftime('%Y%m%d%H%M%S')

ADD = r"""<style id="v30css">
#rows .wa-link-btn{background:#1f9d55;color:#fff;border-color:#1f9d55;font-weight:700}
#rows .wa-link-btn.sent{background:transparent;color:#1f9d55;border-color:#1f9d55}
</style>
<script id="v30js">
(function(){
 // «🟢 رابط الحجز»: opens WhatsApp with the booking-link message ready; staff press Send.
 const LINK='https://dr-younis.space.fast/';
 const MSG='أهلًا وسهلًا بك في عيادة الدكتور يونس عبد الستار عكلة الكبيسي للسونار والدوبلر الملون 🌷\nيمكنكم حجز مواعيدكم القادمة بسهولة من الرابط:\n'+LINK+'\nواحفظوا هذا الرقم للتواصل معنا.';
 function waNum(ph){const d=normPhone(ph||'');return d?'964'+d.slice(1):''}
 function sentToday(p){const n=normPhone(p.phone||'');return S.patients.some(x=>x.waLinkAt&&x.clinic===p.clinic&&normPhone(x.phone||'')===n)}
 function openWa(url){if(window.AndroidBell){location.href=url}else{const w=window.open(url,'_blank');if(!w)location.href=url}}
 function send(id){refreshSharedState();const p=list().find(x=>x.id===id);if(!p)return;const num=waNum(p.phone);if(!num)return toast('رقم الهاتف غير صحيح');openWa('https://wa.me/'+num+'?text='+encodeURIComponent(MSG));if(!p.waLinkAt){p.waLinkAt=stamp();p.waLinkBy=roleName();audit('إرسال رابط الحجز بالواتساب — '+p.name)}render()}
 function add(){document.querySelectorAll('#rows tr[data-id]').forEach(tr=>{const p=S.patients.find(x=>x.id===tr.dataset.id);if(!p||!waNum(p.phone)||p.status==='ملغي')return;const td=tr.querySelector('td:last-child');if(!td||td.querySelector('.wa-link-btn'))return;const done=sentToday(p),b=el('button',done?'✓ الرابط':'🟢 رابط الحجز','wa-link-btn'+(done?' sent':''));b.type='button';b.title=done?'انرسل رابط الحجز — اضغطي إذا تريدين ترسلينه مرة ثانية':'إرسال رابط الحجز للمريض بالواتساب';b.onclick=ev=>{ev.stopPropagation();send(p.id)};td.prepend(b)})}
 const _r=render;render=function(){const r=_r.apply(this,arguments);try{add()}catch(e){console.error(e)}return r};
 try{add()}catch(e){}
})();
</script>
"""

ALL = FILES + ['doctor-test.html', 'doctor-karma-test.html']  # doctor screens: build stamp only
for f in ALL:
    p = T / f; s = p.read_text(encoding='utf-8')
    old0 = s[s.index("BUILD='"):].split("'")[1]
    if f not in FILES:
        p.write_text(s.replace("BUILD='%s'" % old0, "BUILD='%s'" % BUILD), encoding='utf-8'); print('stamped', f); continue
    if 'id="v30js"' in s: print('already', f); continue
    old = s[s.index("BUILD='"):].split("'")[1]; s = s.replace("BUILD='%s'" % old, "BUILD='%s'" % BUILD)
    s = s.rstrip(); assert s.endswith('</body></html>')
    p.write_text(s[:-len('</body></html>')] + ADD + '</body></html>\n', encoding='utf-8'); print('patched', f)
(T / 'version.txt').write_text(BUILD + '\n')
print('BUILD', BUILD)
