#!/usr/bin/env python3
"""v0.17: previous-visit list starts with «لا» (default); new question «عنده سونار قديم
لنفس الفحص؟» (لا / نعم) in registration and edit, shown as 📄 in the list and cards.
Doctor + secretary screens; run tools/make-writer.py afterwards."""
import pathlib, sys
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html', 'secretary-karma-test.html']
def must(s, o, n, w):
    if s.count(o) != 1: sys.exit(f'patch-v17: expected 1 of [{w}], found {s.count(o)}')
    return s.replace(o, n)
R = [
 ("const PV={'':'— ما معروف',no:'لا — أول مرة',same:'نعم — لنفس الفحص',other:'نعم — لفحص آخر'};",
  "const PV={no:'لا — أول مرة',same:'نعم — لنفس الفحص',other:'نعم — لفحص آخر'};", 'pv list'),
 ("s.value=v||'';return s};", "s.value=v||'no';return s};\n"
  " window.osSelect=function(v){const s=el('select');[['no','لا'],['yes','نعم']].forEach(([k,t])=>{const o=el('option',t);o.value=k;s.append(o)});s.value=v==='yes'?'yes':'no';return s};", 'pv default + os'),
 ("const l=el('label','🔁 عنده مراجعة سابقة عدنا؟');l.className='full';regPv=pvSelect('');regPv.id='prevVisit';l.append(regPv);const hint=el('small','','muted');hint.id='pvHint';l.append(hint);\n  regSg=surgBlock([]);regSg.classList.add('full');anchor.after(l,regSg)})();",
  "const l=el('label','🔁 عنده مراجعة سابقة عدنا؟');l.className='full';regPv=pvSelect('');regPv.id='prevVisit';l.append(regPv);const hint=el('small','','muted');hint.id='pvHint';l.append(hint);\n"
  "  const l2=el('label','📄 عنده سونار قديم لنفس الفحص؟');l2.className='full';regOs=osSelect('');regOs.id='oldScan';l2.append(regOs);\n"
  "  regSg=surgBlock([]);regSg.classList.add('full');anchor.after(l,l2,regSg)})();", 'mount'),
 ("let regSg=null,regPv=null,history=[];", "let regSg=null,regPv=null,regOs=null,history=[];", 'vars'),
 ("else if(regPv&&!regPv.value){regPv.value='no';", "else if(regPv){regPv.value='no';", 'auto no'),
 ("if(regPv)regPv.value='';history=[];", "if(regPv)regPv.value='no';if(regOs)regOs.value='no';history=[];", 'reset'),
 ("return{surgeries:regSg?regSg.value:[],prevVisit:regPv?regPv.value:''}};", "return{surgeries:regSg?regSg.value:[],prevVisit:regPv?regPv.value:'no',oldScan:regOs?regOs.value:'no'}};", 'extra'),
 ("const t=[];const pv=pvText(p);if(pv)t.push(['hx-tag hx-pv',pv]);", "const t=[];const pv=pvText(p);if(pv)t.push(['hx-tag hx-pv',pv]);if(p.oldScan==='yes')t.push(['hx-tag hx-os','📄 عنده سونار قديم']);", 'tags'),
 (".hx-pv{color:#fde9c8;background:#5a3a12}", ".hx-pv{color:#fde9c8;background:#5a3a12}.hx-os{color:#dbeafe;background:#1d3f5f}body:not(.dark) .hx-os{color:#1d3f5f;background:#dbeafe}", 'css'),
 ("pv=field('🔁 مراجعة سابقة',pvSelect(p0.prevVisit||'')),", "pv=field('🔁 مراجعة سابقة',pvSelect(p0.prevVisit||'')),os=field('📄 عنده سونار قديم لنفس الفحص؟',osSelect(p0.oldScan||'')),", 'edit field'),
 ("if((pv.value||'')!==(p.prevVisit||'')){", "if(os.value!==(p.oldScan==='yes'?'yes':'no')){ch.push('سونار قديم: '+(os.value==='yes'?'نعم':'لا'));p.oldScan=os.value}if(pv.value!==(p.prevVisit||'no')){", 'edit save'),
]
for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'osSelect' in s: print('already', f); continue
    for o, n, w in R: s = must(s, o, n, w)
    p.write_text(s, encoding='utf-8'); print('patched', f)
