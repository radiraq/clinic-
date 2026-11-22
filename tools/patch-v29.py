#!/usr/bin/env python3
"""v0.29 (all six test screens) — phone number is never required at registration.
- «📞 حجز تلفون» no longer blocks saving when the phone is empty (it was the only place
  that required it). A wrong number is still rejected; an empty one is fine.
- The phone box is no longer painted red when empty (it looked mandatory). It turns green
  when a valid number is typed, and stays neutral when empty.
Features that use the phone already skip empty numbers: search, previous-visit lookup,
WhatsApp booking import (phone:'' when missing)."""
import pathlib, time
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html',
         'secretary-karma-test.html', 'writer-test.html', 'writer-karma-test.html']
BUILD = time.strftime('%Y%m%d%H%M%S')

REPL = [
 ("  if(mode==='tel'&&!normPhone($('phone').value)){e.preventDefault();$('formError').textContent='📞 حجز التلفون يحتاج رقم الهاتف (مثل 07701234567) حتى نتواصل وياه.';$('phone').focus();return}\n",
  ""),
 ("ينحجز بدون فلوس • رقم الهاتف ضروري • لما يوصل",
  "ينحجز بدون فلوس • رقم الهاتف اختياري • لما يوصل"),
 ("const groups=[['name'],['age','ageMonths','ageDays'],['exam'],['pricePreset'],['phone']];",
  "const groups=[['name'],['age','ageMonths','ageDays'],['exam'],['pricePreset']];"),
]
ADD = r"""<script id="v29js">
(function(){
 // Phone is optional: neutral when empty, green when a valid number is typed.
 const f=$('patientForm'),ph=$('phone');if(!f||!ph)return;
 function paint(){const ok=!!normPhone(ph.value);ph.classList.toggle('f-ok',ok);ph.classList.remove('f-empty')}
 f.addEventListener('input',paint);f.addEventListener('change',paint);f.addEventListener('reset',()=>setTimeout(paint,0));paint();
})();
</script>
"""

for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v29js"' in s: print('already', f); continue
    for a, b in REPL:
        n = s.count(a); assert n == 1, (f, n, a[:70]); s = s.replace(a, b)
    old = s[s.index("BUILD='"):].split("'")[1]; s = s.replace("BUILD='%s'" % old, "BUILD='%s'" % BUILD)
    s = s.rstrip(); assert s.endswith('</body></html>')
    p.write_text(s[:-len('</body></html>')] + ADD + '</body></html>\n', encoding='utf-8'); print('patched', f)
(T / 'version.txt').write_text(BUILD + '\n')
print('BUILD', BUILD)
