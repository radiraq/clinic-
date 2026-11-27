#!/usr/bin/env python3
"""v0.40 (doctor screens only) — «📅 حجوزات الأسبوع» button.
A header button on the doctor screen opens a window listing this clinic's bookings
(WhatsApp, online link and phone bookings: wa:true) for today and the next 6 days,
day by day with the count beside each day. Read-only: it changes no patient data.

Usage:
  python3 tools/patch-v40.py preview   -> writes test/doctor-week-preview.html and
                                          test/doctor-karma-week-preview.html (live screens untouched)
  python3 tools/patch-v40.py live      -> patches doctor-test.html and doctor-karma-test.html
"""
import pathlib, sys, time
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
PAIRS = [('doctor-test.html', 'doctor-week-preview.html'),
         ('doctor-karma-test.html', 'doctor-karma-week-preview.html')]
MODE = sys.argv[1] if len(sys.argv) > 1 else 'preview'
BUILD = time.strftime('%Y%m%d%H%M%S')

BTN_ANCHOR = '<button type="button" id="refreshBtn"'
BTN = '<button type="button" id="weekBtn" class="week-btn" title="حجوزات الأسبوع" aria-label="حجوزات الأسبوع">📅 <span>الأسبوع</span></button>'

ADD = r"""<style id="v40css">
.week-btn{font-weight:700}
#weekDlg{width:min(560px,96vw);max-height:88vh;padding:0;border-radius:16px}
#weekDlg .wk-head{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:14px 16px;border-bottom:1px solid #77889944;position:sticky;top:0;background:inherit}
#weekDlg .wk-head h2{margin:0;font-size:18px}
#weekDlg .wk-body{padding:10px 14px 16px;overflow:auto}
#weekDlg .wk-sum{margin:2px 0 10px;font-weight:700}
#weekDlg details{border:1px solid #77889955;border-radius:12px;margin:8px 0;padding:0 10px}
#weekDlg summary{display:flex;align-items:center;justify-content:space-between;padding:11px 2px;cursor:pointer;font-weight:700;list-style:none}
#weekDlg summary::-webkit-details-marker{display:none}
#weekDlg .wk-n{min-width:30px;text-align:center;border-radius:99px;padding:2px 10px;background:#2f9e74;color:#fff;font-size:14px}
#weekDlg .wk-n.z{background:transparent;color:inherit;opacity:.45;border:1px solid #77889966}
#weekDlg details.wk-empty summary{opacity:.6;cursor:default}
#weekDlg .wk-today{color:#f5c26b;font-size:12px;margin-inline-start:6px}
#weekDlg .wk-p{border-top:1px dashed #77889955;padding:8px 2px}
#weekDlg .wk-p b{font-size:16px}
#weekDlg .wk-p small{display:block;opacity:.8;margin-top:2px}
#weekDlg .wk-tag{font-size:11px;border-radius:8px;padding:1px 7px;margin-inline-start:6px;border:1px solid}
#weekDlg .wk-tag.ok{color:#2f9e74;border-color:#2f9e74}
#weekDlg .wk-tag.tel{color:#5aa9ff;border-color:#5aa9ff}
#weekDlg .wk-tag.dup{color:#f5c26b;border-color:#f5c26b}
@media(max-width:600px){.week-btn span{display:none}}
</style>
<dialog id="weekDlg"><div class="wk-head"><h2>📅 حجوزات الأسبوع</h2><button type="button" id="weekClose" aria-label="إغلاق">✕</button></div><div class="wk-body" id="weekBody"></div></dialog>
<script id="v40js">
(function(){
 const b=$('weekBtn'),dlg=$('weekDlg'),body=$('weekBody');if(!b||!dlg)return;
 const WD=['الأحد','الاثنين','الثلاثاء','الأربعاء','الخميس','الجمعة','السبت'];
 const ymd=d=>new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Baghdad',year:'numeric',month:'2-digit',day:'2-digit'}).format(d);
 function days(){const out=[],now=Date.now();for(let i=0;i<7;i++){const s=ymd(new Date(now+i*864e5));const [y,m,d]=s.split('-').map(Number);out.push({s,wd:WD[new Date(Date.UTC(y,m-1,d)).getUTCDay()],label:d+'/'+m,today:i===0})}return out}
 async function load(){
  body.replaceChildren(el('p','⏳ جاري جلب الحجوزات…','muted'));
  if(!window.FB||!cloud||!cloud.db||!cloud.user){body.replaceChildren(el('p','ما متصل بالسيرفر — سوّي تحديث وجرّب مرة ثانية.','muted'));return}
  const D=days();let docs=[];
  try{const c=FB.collection(cloud.db,'clinics',CLINIC_ID,'patients');
   const snap=await FB.getDocs(FB.query(c,FB.where('day','>=',D[0].s),FB.where('day','<=',D[6].s)));
   docs=snap.docs.map(x=>x.data()).filter(p=>p&&p.wa&&p.status!=='ملغي')}
  catch(e){body.replaceChildren(el('p','صار خطأ بجلب الحجوزات: '+(e&&e.message||e),'muted'));return}
  const total=docs.length;body.replaceChildren();
  body.append(el('p',total?('مجموع الحجوزات: '+total+' (اليوم + 6 أيام الجاية)'):'ماكو حجوزات بالأسبوع الجاي.','wk-sum'));
  D.forEach(d=>{
   const L=docs.filter(p=>p.day===d.s).sort((a,b)=>String(a.regAt||'').localeCompare(String(b.regAt||'')));
   const det=el('details');if(!L.length)det.className='wk-empty';if(L.length)det.open=true;
   const sm=el('summary');const t=el('span',d.wd+' '+d.label);if(d.today)t.append(el('span','اليوم','wk-today'));
   sm.append(t,el('span',String(L.length),'wk-n'+(L.length?'':' z')));det.append(sm);
   if(!L.length)sm.addEventListener('click',e=>e.preventDefault());
   const seen={};
   L.forEach(p=>{const r=el('div',undefined,'wk-p');const nm=el('b',p.name||'—');r.append(nm);
    if(p.tel)nm.append(el('span','📞 تلفون','wk-tag tel'));
    if(p.arrivedAt||p.status!=='مؤجل')nm.append(el('span','✓ وصل','wk-tag ok'));
    const k=String(p.name||'').replace(/\s+/g,' ').trim()+'|'+(p.phone||'');if(seen[k])nm.append(el('span','مكرر','wk-tag dup'));seen[k]=1;
    const info=[p.ageLabel||(p.age?p.age+' سنة':''),p.exam,p.phone].filter(Boolean).join(' • ');
    if(info)r.append(el('small',info));
    const w=String(p.waTime||'').replace(/\(.*?\)/g,'').trim();if(w&&!/20\d\d-\d\d-\d\d/.test(w))r.append(el('small','⏰ '+w));
    if(p.waNotes&&!/^💵/.test(p.waNotes))r.append(el('small','📝 '+p.waNotes));
    det.append(r)});
   body.append(det)});
 }
 b.onclick=()=>{try{dlg.showModal()}catch(e){dlg.setAttribute('open','')}load()};
 $('weekClose').onclick=()=>dlg.close();
 dlg.addEventListener('click',e=>{if(e.target===dlg)dlg.close()});
})();
</script>
"""

for src, prev in PAIRS:
    s = (T / src).read_text(encoding='utf-8')
    if 'id="v40js"' in s: print('already', src); continue
    assert s.count(BTN_ANCHOR) == 1, src
    s = s.replace(BTN_ANCHOR, BTN + BTN_ANCHOR)
    if MODE == 'live':
        old = s[s.index("BUILD='"):].split("'")[1]; s = s.replace("BUILD='%s'" % old, "BUILD='%s'" % BUILD)
    s = s.rstrip(); assert s.endswith('</body></html>'), src
    s = s[:-len('</body></html>')] + ADD + '</body></html>\n'
    out = T / (src if MODE == 'live' else prev)
    out.write_text(s, encoding='utf-8'); print('wrote', out.name)
if MODE == 'live':
    (T / 'version.txt').write_text(BUILD + '\n'); print('BUILD', BUILD)
