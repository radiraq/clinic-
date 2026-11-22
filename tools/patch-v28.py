#!/usr/bin/env python3
"""v0.28 (doctor + writer test screens) — shorter Settings page.
Approved by the doctor after review by his advisory board.
- Settings cards fold: 👨‍⚕️ الأطباء المحولين, 🩺 الفحوصات والأسعار, 👤 حسابات الكادر.
  All closed at start, with a count; opening one closes the others.
- Exams: one short line per exam (name • under 10 • 10+) with ✎; the edit fields
  (and حفظ / حذف) open only for that exam. Search box filters by name.
- «＋ فحص جديد» and «＋ حساب جديد» forms hidden behind a button.
- «فتح شاشة السكرتيرة / الكاتبة» and «تسجيل خروج» always visible at the bottom.
Save/delete/reorder logic is untouched; only the display changes."""
import pathlib, time
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'writer-test.html', 'writer-karma-test.html']
ALL = FILES + ['secretary-test.html', 'secretary-karma-test.html']
BUILD = time.strftime('%Y%m%d%H%M%S')

REPL = [
 # «✎ تعديل السعر» from the price check bar: open the folded exam first.
 ("const t=[...document.querySelectorAll('#catalogRows input')].find(i=>i.value===x.name);if(t){",
  "const t=[...document.querySelectorAll('#catalogRows input')].find(i=>i.value===x.name);if(t){try{window.__openExam&&window.__openExam(t)}catch(e){}"),
]

ADD = r"""<style id="v28css">
#settings .set-card{padding:0!important;margin-bottom:12px!important;overflow:hidden}
#settings .set-head{display:flex;align-items:center;gap:10px;width:100%;padding:16px 18px;background:transparent;border:0;color:inherit;font:inherit;font-size:18px;font-weight:800;text-align:right;cursor:pointer}
#settings .set-head .set-n{margin-inline-start:auto;font-size:13px;font-weight:700;padding:2px 10px;border-radius:20px;background:#ffffff14}
#settings .set-head::after{content:'▾';font-size:16px;opacity:.7;transition:transform .2s}
#settings .set-card.open .set-head::after{transform:rotate(180deg)}
#settings .set-body{padding:0 18px 16px}
#settings .set-card:not(.open) .set-body{display:none}
#settings .set-body>h2{display:none}
#settings .set-hint{font-size:13px;margin:0 0 10px}
#settings .set-tools{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 10px}
#settings .set-tools>*{flex:1 1 140px;margin:0!important}
#settings .set-hide{display:none!important}
#settings .set-foot{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px}
#settings .set-foot button{flex:1 1 140px}
#settings table:has(#catalogRows){display:block;width:100%}
#settings table:has(#catalogRows) thead{display:none!important}
#settings table:has(#catalogRows) tbody{display:block}
#catalogRows tr.cat-c{display:flex!important;flex-wrap:wrap;align-items:center;gap:6px;padding:6px 4px!important;margin:0!important;border:0!important;border-bottom:1px solid #ffffff14!important;border-radius:0!important;background:transparent!important;box-shadow:none!important}
#catalogRows tr.cat-c>td{display:none!important}
#catalogRows tr.cat-c>td.cat-sum{display:flex!important;flex:1 1 100%!important;align-items:center;gap:8px;padding:0!important;border:0!important;width:auto!important}
#catalogRows .cat-sum b{flex:1;min-width:0;overflow-wrap:anywhere;font-size:15px}
#catalogRows .cat-sum .cat-p{white-space:nowrap;font-size:14px;opacity:.85;direction:rtl}
#catalogRows .cat-sum button{padding:6px 12px;min-width:44px}
#catalogRows tr.cat-c.ed{background:#ffffff08!important;border-radius:10px!important;padding:8px!important;margin:4px 0!important}
#catalogRows tr.cat-c.ed>td:not(.cat-sum){display:block!important;flex:1 1 30%!important;padding:0!important;border:0!important;width:auto!important}
#catalogRows tr.cat-c.ed>td:last-child{display:flex!important;flex:1 1 100%!important;gap:6px}
#catalogRows tr.cat-c.ed>td:last-child button{flex:1}
#catalogRows tr.cat-c.ed .cat-lbl{display:block!important;margin-bottom:3px}
#catalogRows tr.cat-c.cat-off{display:none!important}
</style>
<script id="v28js">
(function(){
 const st=document.getElementById('settings');if(!st||!document.getElementById('docNewExamForm'))return;
 const mk=(t,txt,c)=>{const e=document.createElement(t);if(txt!=null)e.textContent=txt;if(c)e.className=c;return e};
 const b=(txt,fn,c)=>{const e=mk('button',txt,c);e.type='button';e.onclick=fn;return e};
 let openKey=null,search='';const editing=new Set();
 function kindOf(c){if(c.id==='refCard')return'ref';if(c.querySelector('#catalogRows'))return'exam';if(c.querySelector('#secretaryAccountForm'))return'acc';return''}
 const TITLE={ref:'👨‍⚕️ الأطباء المحولين',exam:'🩺 الفحوصات والأسعار',acc:'👤 حسابات الكادر'};
 const HINT={ref:'اضغط ☆ حتى يطلع الطبيب أول القائمة.',exam:'كل سطر: سعر أقل من ١٠ سنوات • سعر ١٠ سنوات فأكثر (بالألف دينار). التعديل يطبّق على التسجيلات الجديدة فقط.',acc:'كل سكرتيرة أو كاتبة إلها حساب تدخل بيه من أي جهاز.'};
 function count(k){try{if(k==='ref')return(S.referrers||[]).length;if(k==='exam')return examCatalog.length;if(k==='acc')return staffUsers.length}catch(e){}return''}
 function setOpen(k){openKey=openKey===k?null:k;st.querySelectorAll('.set-card').forEach(c=>c.classList.toggle('open',c.dataset.k===openKey))}
 function toggler(btnTxt,target,first){const t=b(btnTxt,()=>{const hid=target.classList.toggle('set-hide');t.classList.toggle('primary',hid);if(!hid){const f=target.querySelector(first);f&&f.focus()}},'primary');target.classList.add('set-hide');return t}
 function fold(c){const k=kindOf(c);if(!k||c.dataset.k)return;c.dataset.k=k;c.classList.add('set-card');
  const body=mk('div',null,'set-body');while(c.firstChild)body.append(c.firstChild);
  const h=b('',()=>setOpen(k),'set-head');h.append(mk('span',TITLE[k]),mk('span','','set-n'));c.append(h,body);
  body.querySelectorAll(':scope>p.muted,:scope>.section-note').forEach(p=>{if(!p.querySelector('input,button'))p.classList.add('set-hide')});
  body.querySelector(':scope>h2')?.after(mk('p',HINT[k],'muted set-hint'));
  if(k==='exam'){const form=document.getElementById('docNewExamForm'),wrap=document.getElementById('catalogRows').closest('.tablewrap');
   const tools=mk('div',null,'set-tools');const q=mk('input');q.type='search';q.placeholder='🔍 ابحث عن فحص';q.id='catSearch';q.oninput=()=>{search=q.value.trim();filter()};
   tools.append(toggler('＋ فحص جديد',form,'input'),q);const ord=body.querySelector('.ord-btn');if(ord){tools.append(ord)}form.before(tools)}
  if(k==='acc'){const form=document.getElementById('secretaryAccountForm');form.before(toggler('＋ حساب جديد',form,'select'));
   const foot=document.getElementById('openSecretaryPreview')?.closest('.actions');if(foot){foot.classList.add('set-foot');foot.classList.remove('actions');st.append(foot)}}
  c.classList.toggle('open',openKey===k)}
 function filter(){const s=search.toLowerCase();document.querySelectorAll('#catalogRows tr.cat-c').forEach(tr=>tr.classList.toggle('cat-off',!!s&&!tr.dataset.n.toLowerCase().includes(s)))}
 function compact(){const root=document.getElementById('catalogRows');if(!root)return;
  [...root.children].forEach(tr=>{if(tr.classList.contains('cat-c'))return;const ins=tr.querySelectorAll('input');if(ins.length<3)return;
   const name=ins[0].value;tr.classList.add('cat-c');tr.dataset.n=name;
   const sum=mk('td',null,'cat-sum');sum.append(mk('b',name),mk('span',ins[1].value+' • '+ins[2].value+' ألف','cat-p'));
   const ed=b('✎',()=>{const on=tr.classList.toggle('ed');on?editing.add(name):editing.delete(name);ed.textContent=on?'✕':'✎';if(on)ins[1].focus()});ed.title='تعديل';sum.append(ed);tr.prepend(sum);
   if(editing.has(name)){tr.classList.add('ed');ed.textContent='✕'}});
  editing.forEach(n=>{if(![...root.children].some(tr=>tr.dataset.n===n))editing.delete(n)});filter()}
 window.__openExam=function(inp){const tr=inp.closest('tr');if(openKey!=='exam')setOpen('exam');if(tr&&!tr.classList.contains('ed'))tr.querySelector('.cat-sum button')?.click();if(search){search='';const q=document.getElementById('catSearch');if(q)q.value='';filter()}};
 function run(){try{st.querySelectorAll(':scope>.card').forEach(fold);compact();st.querySelectorAll('.set-card').forEach(c=>{const n=c.querySelector('.set-n');if(n){const v=count(c.dataset.k);n.textContent=v===''?'':v}})}catch(e){console.error(e)}}
 // Saving an exam re-renders the list: drop the editing mark of the saved row so it closes.
 document.getElementById('catalogRows').addEventListener('click',e=>{const x=e.target.closest('td:last-child button');if(x&&x.textContent==='حفظ'){const tr=x.closest('tr');tr&&editing.delete(tr.dataset.n)}},true);
 const mo=new MutationObserver(()=>{mo.disconnect();run();watch()});function watch(){mo.observe(st,{childList:true,subtree:true})}
 run();watch();
})();
</script>
"""

for f in ALL:
    p = T / f
    s = p.read_text(encoding='utf-8')
    if f in FILES:
        assert 'id="v28js"' not in s, f + ' already patched'
        for a, b_ in REPL:
            n = s.count(a)
            assert n == 1, (f, a[:50], n)
            s = s.replace(a, b_)
        s = s.replace('</body></html>', ADD + '</body></html>', 1)
    old = s[s.find("BUILD='"):s.find("BUILD='") + 22]
    assert old.startswith("BUILD='") and old.endswith("'"), (f, old)
    s = s.replace(old, "BUILD='" + BUILD + "'")
    p.write_text(s, encoding='utf-8')
    print('patched', f)
(T / 'version.txt').write_text(BUILD + '\n')
print('BUILD', BUILD)
