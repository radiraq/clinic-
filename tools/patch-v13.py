#!/usr/bin/env python3
"""v0.13: «داخل الفحص الآن» / «المريض الجاي» cards show the referring doctor, the
registration time with how long ago, and (inside) how long the exam has been going.
Doctor screens (writer is built from them); run tools/make-writer.py afterwards."""
import pathlib
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html']
LAYER = r"""<style id="v13now">#nowCard .nc-x{display:flex;flex-wrap:wrap;gap:6px 12px;margin-top:8px;font-size:14px;font-weight:700}#nowCard .nc-x span{white-space:nowrap}#nowCard .nc-ref{color:#9fd3ff}#nowCard .nc-reg{color:var(--muted)}#nowCard .nc-ago{color:#7bdbc2}#nowCard .nc-ago[data-lvl='1']{color:#f5c26b}#nowCard .nc-ago[data-lvl='2']{color:#ff8a8a}#nowCard .nc-in-t{color:#7bdbc2}</style>
<script id="v13js">
(function(){
 function regAt(p){if(p.regAt)return p.regAt;const l=(S.ledger||[]).find(x=>x._id==='pay-'+p.id);if(l&&l.at)return l.at;return ''}
 function dur(at){const m=Math.max(0,Math.floor((Date.now()-new Date(at))/60000)),h=Math.floor(m/60),r=m%60;return{t:m<1?'هسه':m<60?m+' د':h+' س'+(r?' و'+r+' د':''),lvl:m>=60?'2':m>=30?'1':'0'}}
 function extra(box,p,inside){if(!box)return;let x=box.querySelector('.nc-x');if(!p){if(x)x.remove();return}
  const parts=[];if(p.referrer)parts.push(['nc-ref','↩ '+p.referrer]);const at=regAt(p);if(at){parts.push(['nc-reg','🕒 سجّل '+time(at)]);const d=dur(at);parts.push(['nc-ago','⏳ صار له '+d.t,d.lvl])}
  if(inside&&p.enteredAt)parts.push(['nc-in-t','🩺 داخل من '+dur(p.enteredAt).t]);
  const key=JSON.stringify(parts);if(x&&x.dataset.k===key)return;if(!x){x=el('div',undefined,'nc-x');box.append(x)}x.dataset.k=key;x.replaceChildren();
  parts.forEach(([c,t,l])=>{const s=el('span',t,c);if(l)s.dataset.lvl=l;x.append(s)})}
 function run(){const c=document.getElementById('nowCard');if(!c)return;const inside=list().find(p=>p.status==='داخل الفحص'||p.status===OUT);let next=null;try{next=nextPatient()}catch(e){}
  extra(c.querySelector('.nc-in'),inside,true);extra(c.querySelector('.nc-next'),next,false)}
 const base=render;render=function(){const r=base.apply(this,arguments);try{run()}catch(e){console.error(e)}return r};setInterval(()=>{try{run()}catch(e){}},30000);try{run()}catch(e){}
})();
</script>
</body></html>"""
for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v13js"' in s: print('already', f); continue
    s = s.rstrip(); assert s.endswith('</body></html>')
    p.write_text(s[:-len('</body></html>')] + LAYER + '\n', encoding='utf-8'); print('patched', f)
