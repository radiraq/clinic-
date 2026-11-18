#!/usr/bin/env python3
"""v0.11: warn on any screen whose device clock is wrong (compared with the server's Date
header), because every recorded time (registration, payments, messages) comes from the
device clock. Doctor + secretary screens; run tools/make-writer.py afterwards."""
import pathlib
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html', 'secretary-karma-test.html']
LAYER = r"""<style id="v11clock">#clockWarn{position:fixed;top:0;left:0;right:0;z-index:9500;background:#b91c1c;color:#fff;font-weight:800;font-size:15px;text-align:center;padding:10px 12px;line-height:1.6}#clockWarn.hidden{display:none}#clockWarn small{display:block;font-weight:500;font-size:12px;opacity:.9}</style>
<script id="v11js">
(function(){
 const w=document.createElement('div');w.id='clockWarn';w.className='hidden';w.setAttribute('role','alert');document.body.append(w);
 function fmt(ms){const m=Math.round(Math.abs(ms)/60000);if(m>=60){const h=Math.floor(m/60),r=m%60;return h+' ساعة'+(r?' و'+r+' دقيقة':'')}return m+' دقيقة'}
 function check(){const t0=Date.now();fetch('version.txt?clock='+t0,{cache:'no-store'}).then(r=>{const d=r.headers.get('date');if(!d)return;const t1=Date.now(),server=new Date(d).getTime()+500;if(!Number.isFinite(server))return;const off=(t0+t1)/2-server;
  if(Math.abs(off)>5*60000){w.innerHTML='';w.append('⚠️ ساعة هذا الجهاز غلط — '+(off>0?'متقدمة':'متأخرة')+' '+fmt(off));const s=document.createElement('small');s.textContent='الأوقات المسجلة راح تطلع غلط. صححي الساعة: الإعدادات ← التاريخ والوقت ← شغّلي «الوقت التلقائي» وتأكدي من ص/م.';w.append(s);w.classList.remove('hidden')}else w.classList.add('hidden')}).catch(()=>{})}
 check();setInterval(check,10*60000);document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')check()});
})();
</script>
</body></html>"""
for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v11js"' in s: print('already', f); continue
    s = s.rstrip(); assert s.endswith('</body></html>')
    p.write_text(s[:-len('</body></html>')] + LAYER + '\n', encoding='utf-8'); print('patched', f)
