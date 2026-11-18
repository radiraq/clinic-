#!/usr/bin/env python3
"""v0.10: registration time shown under each patient's turn number in today's list.
New patients store regAt; older ones use the time their payment was recorded at
registration (ledger pay-<id>), else the audit line. Doctor + secretary screens;
run tools/make-writer.py afterwards."""
import pathlib, sys
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html', 'secretary-karma-test.html']
OLD = "regBy:roleName(),referrer:"
NEW = "regBy:roleName(),regAt:stamp(),referrer:"
LAYER = r"""<style id="v10reg">.reg-t{display:block;font-size:11px;font-weight:600;color:var(--muted);margin-top:3px;white-space:nowrap;direction:rtl}@media(max-width:760px){tbody td.num .reg-t{display:inline-block;margin:0 6px 0 0}}</style>
<script id="v10js">
(function(){
 // When was this patient registered?
 function regAt(p){if(p.regAt)return p.regAt;const l=(S.ledger||[]).find(x=>x._id==='pay-'+p.id);if(l&&l.at)return l.at;const a=(S.audit||[]).filter(x=>String(x.text||x.action||'').startsWith('إضافة '+p.name)).map(x=>x.at).sort()[0];return a||''}
 function tag(){document.querySelectorAll('#rows tr[data-id]').forEach(tr=>{const p=list().find(x=>x.id===tr.dataset.id),td=tr.querySelector('td.num')||tr.querySelector('td');if(!p||!td)return;const at=regAt(p);let t=td.querySelector('.reg-t');if(!at){if(t)t.remove();return}if(!t){t=el('span','','reg-t');td.append(t)}const s='🕒 '+time(at);if(t.textContent!==s)t.textContent=s;t.title='وقت التسجيل'})}
 const base=render;render=function(){const r=base.apply(this,arguments);try{tag()}catch(e){console.error(e)}return r};try{tag()}catch(e){}
})();
</script>
</body></html>"""
for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v10js"' in s: print('already', f); continue
    if s.count(OLD) != 1: sys.exit('patch-v10: push not found in ' + f)
    s = s.replace(OLD, NEW).rstrip(); assert s.endswith('</body></html>')
    s = s[:-len('</body></html>')] + LAYER + '\n'
    p.write_text(s, encoding='utf-8'); print('patched', f)
