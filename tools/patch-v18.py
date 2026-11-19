#!/usr/bin/env python3
"""v0.18: registration order chosen by the doctor —
الاسم ← العمر ← نوع الفحص (+ فحص ثاني) ← السعر (+ الخصم) ← الهاتف ← الطبيب المحوِّل ←
مراجعة سابقة ← سونار قديم ← عمليات سابقة ← زر التسجيل.
Doctor + secretary screens; run tools/make-writer.py afterwards."""
import pathlib
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html', 'secretary-karma-test.html']
LAYER = r"""<style id="v18css">#patientForm .formgrid>details.reg-disc{grid-column:1/-1;margin:-4px 0 4px}#patientForm .formgrid>details.reg-disc summary{cursor:pointer;font-size:13px;color:var(--muted)}#patientForm .formgrid>details.reg-disc .formgrid{margin-top:10px}</style>
<script id="v18js">
(function(){
 // Registration order: name, age, exam, price (+discount), phone, referrer, previous visit, old scan, surgeries.
 const f=$('patientForm');if(!f)return;const g=f.querySelector('.formgrid');if(!g)return;
 const lab=id=>{const e=$(id);return e?e.closest('label'):null};
 const exam2=$('toggleSecondExam')?$('toggleSecondExam').closest('div'):null;
 const disc=$('discount')?$('discount').closest('details'):null;if(disc){disc.classList.add('reg-disc');disc.style.marginTop=''}
 const sg=f.querySelector('.sg-box');
 const order=[lab('name'),lab('age'),lab('exam'),exam2,lab('pricePreset'),disc,lab('phone'),lab('referrer'),lab('prevVisit'),lab('oldScan'),sg].filter(Boolean);
 ['age','exam','pricePreset'].forEach(id=>{const l=lab(id);if(l)l.classList.add('full')});
 order.forEach(n=>g.append(n));
})();
</script>
</body></html>"""
for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v18js"' in s: print('already', f); continue
    s = s.rstrip(); assert s.endswith('</body></html>')
    p.write_text(s[:-len('</body></html>')] + LAYER + '\n', encoding='utf-8'); print('patched', f)
