#!/usr/bin/env python3
"""v0.24 (all six test screens) — tidy WhatsApp booking rows (doctor's choice: same list, cleaner).
- Green «🤖 حجز واتساب» tag next to the name (and the red «💵 غير مدفوع» beside it after arrival).
- Before arrival: no «مؤجل» badge and no long line; only a short «⏰ time» under the status.
- «✓ وصل» (and later «💵 قبض») is the first, big green/orange button of the row.
- New bookings keep the requested time in p.waTime and a short status line."""
import pathlib, time
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html',
         'secretary-karma-test.html', 'writer-test.html', 'writer-karma-test.html']
BUILD = time.strftime('%Y%m%d%H%M%S')

REPL = [
 ("status:'مؤجل',statusReason:TAG+' — واتساب'+(b.time?' • '+String(b.time).slice(0,80):''),statusBy:'واتساب',",
  "status:'مؤجل',statusReason:'🤖 حجز واتساب',waTime:String(b.time||'').slice(0,80),statusBy:'واتساب',"),
]
ADD = r"""<style id="v24css">
#rows tr[data-id^="wa-"] button.b-arrive{background:#25a35a!important;color:#fff!important;border-color:#25a35a!important;font-weight:800;min-width:42%;font-size:16px}
#rows tr[data-id^="wa-"] button.wa-pay{background:#e08a1e!important;color:#fff!important;border-color:#e08a1e!important;font-weight:800;min-width:42%;font-size:16px}
#rows tr[data-id^="wa-"] .wa-tag,#rows tr[data-id^="wa-"] .wa-unpaid{margin:2px 0 2px 6px;vertical-align:middle}
#rows tr[data-id^="wa-"] td.wa-st .wa-when{display:inline-block;padding:2px 8px;border-radius:8px;background:#ffffff10;font-size:13px;font-weight:700}
</style>
<script id="v24js">
(function(){
 function when(p){let t=String(p.waTime||'');if(!t){const r=String(p.statusReason||'');const i=r.indexOf('•');t=i>=0?r.slice(i+1):''}
  t=toAsciiDigits(t).replace(/20\d\d-\d\d-\d\d/g,' ').replace(/\(.*?\)/g,' ').replace(/(^|\s)(اليوم|الأحد|الاثنين|الإثنين|الثلاثاء|الأربعاء|الاربعاء|الخميس|الجمعة|السبت)(?=\s|،|,|$)/g,' ').replace(/[،,•]/g,' ').replace(/واتساب/g,' ').replace(/\s+/g,' ').trim();return t.slice(0,36)}
 function fix(){document.querySelectorAll('tr[data-id^="wa-"]').forEach(tr=>{const p=S.patients.find(x=>x.id===tr.dataset.id);if(!p)return;const td=tr.children,nameTd=td[1],stTd=td[2],actTd=td[3];
   const tag=tr.querySelector('.wa-tag');if(tag){tag.textContent='🤖 حجز واتساب';if(nameTd){const nm=nameTd.querySelector('.cp');if(tag.parentNode!==nameTd||tag.previousElementSibling!==nm){if(nm)nm.after(tag);else nameTd.prepend(tag)}}}
   const un=tr.querySelector('.wa-unpaid');if(un&&tag&&un.previousElementSibling!==tag)tag.after(un);
   if(stTd&&!p.arrivedAt&&p.status==='مؤجل'){const w=when(p);if(!stTd.classList.contains('wa-st')||stTd.dataset.w!==w){stTd.classList.add('wa-st');stTd.dataset.w=w;stTd.replaceChildren();if(w)stTd.append(el('small','⏰ '+w,'wa-when'))}}
   else if(stTd&&stTd.classList.contains('wa-st')){stTd.classList.remove('wa-st')}
   if(actTd){const a=tr.querySelector('.b-arrive'),pay=tr.querySelector('.wa-pay'),first=pay||a;if(first&&actTd.firstElementChild!==first)actTd.prepend(first)}})}
 const _r=render;render=function(){const r=_r.apply(this,arguments);try{fix()}catch(e){console.error(e)}return r};try{fix()}catch(e){}
})();
</script>
"""

for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v24js"' in s: print('already', f); continue
    for a, b in REPL:
        n = s.count(a); assert n == 1, (f, n, a[:70]); s = s.replace(a, b)
    old = s[s.index("BUILD='"):].split("'")[1]; s = s.replace("BUILD='%s'" % old, "BUILD='%s'" % BUILD)
    s = s.rstrip(); assert s.endswith('</body></html>')
    p.write_text(s[:-len('</body></html>')] + ADD + '</body></html>\n', encoding='utf-8'); print('patched', f)
(T / 'version.txt').write_text(BUILD + '\n')
print('BUILD', BUILD)
