#!/usr/bin/env python3
"""v0.19: the first five registration fields (الاسم، العمر، نوع الفحص، السعر، الهاتف) are
faint red while empty and turn faint green once filled. Doctor + secretary screens;
run tools/make-writer.py afterwards."""
import pathlib
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html', 'secretary-karma-test.html']
LAYER = r"""<style id="v19css">
#patientForm .f-empty{background:rgba(220,70,70,.10)!important;border-color:rgba(230,100,100,.45)!important}
#patientForm .f-ok{background:rgba(40,170,110,.10)!important;border-color:rgba(70,185,130,.45)!important}
body:not(.dark) #patientForm .f-empty{background:#fdf0f0!important;border-color:#efc4c4!important}
body:not(.dark) #patientForm .f-ok{background:#eefaf3!important;border-color:#b9e2cb!important}
</style>
<script id="v19js">
(function(){
 // Faint red when empty, faint green when filled: name, age, exam, price, phone.
 const groups=[['name'],['age','ageMonths','ageDays'],['exam'],['pricePreset'],['phone']];
 function paint(){groups.forEach(ids=>{const els=ids.map(id=>$(id)).filter(Boolean);if(!els.length)return;const ok=els.some(e=>String(e.value||'').trim()!==''&&e.value!=='__newexam__');els.forEach(e=>{e.classList.toggle('f-ok',ok);e.classList.toggle('f-empty',!ok)})})}
 const f=$('patientForm');if(!f)return;f.addEventListener('input',paint);f.addEventListener('change',paint);f.addEventListener('reset',()=>setTimeout(paint,0));
 const base=render;render=function(){const r=base.apply(this,arguments);try{paint()}catch(e){}return r};paint();
})();
</script>
</body></html>"""
for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v19js"' in s: print('already', f); continue
    s = s.rstrip(); assert s.endswith('</body></html>')
    p.write_text(s[:-len('</body></html>')] + LAYER + '\n', encoding='utf-8'); print('patched', f)
