#!/usr/bin/env python3
"""v0.12: under the registration time, how long ago the patient registered (minutes /
hours), for patients not finished yet; refreshed every 30 seconds. Doctor + secretary
screens; run tools/make-writer.py afterwards."""
import pathlib, sys
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html', 'secretary-karma-test.html']
R = [
 ("const s='🕒 '+time(at);if(t.textContent!==s)t.textContent=s;t.title='وقت التسجيل'})}",
  "const s='🕒 '+time(at);if(t.textContent!==s)t.textContent=s;t.title='وقت التسجيل';"
  "let e=td.querySelector('.reg-e');const live=!['مكتمل','ملغي'].includes(p.status);"
  "if(!live){if(e)e.remove();return}if(!e){e=el('span','','reg-e');td.append(e)}const ago=since(at);if(e.textContent!==ago.t)e.textContent=ago.t;e.dataset.lvl=ago.lvl})}\n"
  " function since(at){const m=Math.max(0,Math.floor((Date.now()-new Date(at))/60000));const h=Math.floor(m/60),r=m%60;"
  "return{t:'⏳ '+(m<1?'هسه':m<60?m+' د':h+' س'+(r?' و'+r+' د':'')),lvl:m>=60?'2':m>=30?'1':'0'}}\n"
  " setInterval(()=>{try{tag()}catch(e){}},30000);", 'tag'),
 ("<style id=\"v10reg\">", "<style id=\"v10reg\">.reg-e{display:block;font-size:12px;font-weight:700;color:#7bdbc2;margin-top:2px;white-space:nowrap}.reg-e[data-lvl='1']{color:#f5c26b}.reg-e[data-lvl='2']{color:#ff8a8a}@media(max-width:760px){tbody td.num .reg-e{display:inline-block;margin:0 6px 0 0}}", 'style'),
]
for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'reg-e' in s: print('already', f); continue
    for o, n, w in R:
        if s.count(o) != 1: sys.exit('patch-v12: ' + w + ' not found in ' + f)
        s = s.replace(o, n)
    p.write_text(s, encoding='utf-8'); print('patched', f)
