#!/usr/bin/env python3
"""v0.14: now/next cards — one detail line: exam • age • referring doctor (instead of the
turn number) • how long the patient waited (inside: registration → entry; next: since
registration). Replaces the v0.13 extra line. Doctor screens; run make-writer.py after."""
import pathlib, re, sys
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html']
LAYER = r"""<style id="v13now">#nowCard .nc-d .nc-ref{color:#9fd3ff;font-weight:700}#nowCard .nc-d .nc-w{color:#7bdbc2;font-weight:700;white-space:nowrap}#nowCard .nc-d .nc-w[data-lvl='1']{color:#f5c26b}#nowCard .nc-d .nc-w[data-lvl='2']{color:#ff8a8a}</style>
<script id="v13js">
(function(){
 // Detail line of the now/next cards: exam • age • referrer • waiting time.
 function regAt(p){if(p.regAt)return p.regAt;const l=(S.ledger||[]).find(x=>x._id==='pay-'+p.id);return l&&l.at||''}
 function mins(a,b){return Math.max(0,Math.floor((new Date(b)-new Date(a))/60000))}
 function fmt(m){const h=Math.floor(m/60),r=m%60;return m<1?'هسه':m<60?m+' د':h+' س'+(r?' و'+r+' د':'')}
 function line(box,p,inside){if(!box||!p)return;const d=box.querySelector('.nc-d');if(!d)return;
  const at=regAt(p),parts=[[null,p.exam],[null,ageShow(p)?'العمر '+ageShow(p):'']];if(p.referrer)parts.push(['nc-ref','↩ '+p.referrer]);
  if(at){const m=inside&&p.enteredAt?mins(at,p.enteredAt):mins(at,Date.now());parts.push(['nc-w',(inside&&p.enteredAt?'⏳ انتظر ':'⏳ ينتظر من ')+fmt(m),m>=60?'2':m>=30?'1':'0'])}
  const key=JSON.stringify(parts);if(d.dataset.k===key)return;d.dataset.k=key;d.replaceChildren();
  parts.filter(x=>x[1]).forEach(([c,t,l],i)=>{if(i)d.append(' • ');if(c){const s=el('span',t,c);if(l)s.dataset.lvl=l;d.append(s)}else d.append(t)})}
 function run(){const c=document.getElementById('nowCard');if(!c)return;const inside=list().find(p=>p.status==='داخل الفحص'||p.status===OUT);let next=null;try{next=nextPatient()}catch(e){}
  line(c.querySelector('.nc-in'),inside,true);line(c.querySelector('.nc-next'),next,false)}
 const base=render;render=function(){const r=base.apply(this,arguments);try{run()}catch(e){console.error(e)}return r};setInterval(()=>{try{run()}catch(e){}},5000);try{run()}catch(e){}
})();
</script>
"""
for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'nc-w' in s: print('already', f); continue
    s, n = re.subn(r'<style id="v13now">.*?</script>\n', lambda m: LAYER, s, count=1, flags=re.S)
    if n != 1: sys.exit('patch-v14: v13 block not found in ' + f)
    p.write_text(s, encoding='utf-8'); print('patched', f)
