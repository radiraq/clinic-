#!/usr/bin/env python3
"""v0.22 (all six test screens):
1) WhatsApp bookings: every screen checks the n8n bookings list each minute. A booking for today
   is added to today's patients as «🤖 تسجيل آلي» (status مؤجل, nothing collected). When the patient
   arrives, «✓ وصل» puts him in the waiting queue with a fresh turn number and collects the money.
   Everything stays editable with ✎.
2) Backup: the doctor and secretary screens send the whole day's data to n8n (table clinic_backups)
   every 10 minutes and whenever the screen goes to the background."""
import pathlib, time
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html',
         'secretary-karma-test.html', 'writer-test.html', 'writer-karma-test.html']
BUILD = time.strftime('%Y%m%d%H%M%S')

JS = r"""<style id="v22css">tr[data-id^="wa-"]>td:first-child{box-shadow:inset -4px 0 0 #25a35a}.wa-tag{display:inline-block;margin-inline-start:6px;padding:1px 7px;border-radius:8px;background:#25a35a22;color:#2fbf71;font-size:12px;font-weight:700;white-space:nowrap}.b-arrive{background:#25a35a!important;color:#fff!important;border-color:#25a35a!important}</style>
<script id="v22js">
(function(){
 const API='https://radiraq.app.n8n.cloud/webhook/';
 const BK=API+(CLINIC_ID==='karma'?'screens-bookings-karma-p3v8n5':'screens-bookings-fallujah-f7k2x9');
 const BU=API+'screens-backup-q8m4t2';
 const TAG='🤖 تسجيل آلي';
 // Money for a WhatsApp booking is collected only when the patient arrives.
 const _ac=autoCollect;autoCollect=function(p){if(p&&p.wa&&!p.arrivedAt)return false;return _ac.apply(this,arguments)};
 // Arrival: into the waiting queue with a new turn number (arrival order) + collect.
 const _tr=transition;transition=function(p,status){const id=p&&p.id;refreshSharedState();const q=id&&list().find(x=>x.id===id);
  if(q&&q.wa&&!q.arrivedAt&&q.status==='مؤجل'&&status==='بانتظار الدخول'){q.arrivedAt=stamp();q.no=Math.max(0,...list().filter(x=>x.id!==id).map(x=>x.no||0))+1;q.regAt=stamp();q.status='بانتظار الدخول';q.statusReason='';q.statusBy=roleName();q.statusAt=stamp();autoCollect(q);
   audit('وصل '+q.name+' (حجز واتساب) — الدور '+q.no+(q.paid?' — قبض '+money(q.paid):''));render();toast('✓ وصل '+q.name+' • الدور '+q.no+(q.paid?' • انقبض '+money(q.paid):''));return}
  return _tr.apply(this,arguments)};
 const ymd=d=>new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Baghdad',year:'numeric',month:'2-digit',day:'2-digit'}).format(d);
 function bookDay(b){const t=toAsciiDigits(String(b.time||''));const m=t.match(/20\d\d-\d\d-\d\d/);if(m)return m[0];const at=new Date(b.at||Date.now());if(/غد|غدا|باچر|باكر|بكرة|بكره/.test(t))return ymd(new Date(at.getTime()+864e5));return ymd(at)}
 function ageOf(a){const m=toAsciiDigits(String(a||'')).match(/\d+(\.\d+)?/);const n=m?Number(m[0]):NaN;return Number.isFinite(n)&&n>=0&&n<=120?n:0}
 const marked=new Set();
 function mark(id){if(marked.has(id))return;marked.add(id);fetch(BK+'?mark='+encodeURIComponent(id)+'&t='+Date.now(),{cache:'no-store'}).catch(()=>marked.delete(id))}
 let busy=false;
 async function pull(){if(busy||!cloud.user||!cloud.db||!navigator.onLine)return;busy=true;try{
  const r=await fetch(BK+'?t='+Date.now(),{cache:'no-store'});if(!r.ok)return;const j=await r.json();const today=day();let added=[];
  for(const b of (j.bookings||[])){if(!b||!b.id||bookDay(b)!==today)continue;const id='wa-'+CLINIC_ID+'-'+b.id;
   if(S.patients.some(p=>p.id===id)){mark(b.id);continue}
   try{const s=await Promise.race([FB.getDoc(FB.doc(cloud.db,'clinics',CLINIC_ID,'patients',id)),new Promise((_,x)=>setTimeout(()=>x(Error('slow')),5000))]);if(s.exists()){mark(b.id);continue}}catch(e){continue}
   refreshSharedState();if(S.patients.some(p=>p.id===id))continue;
   const base=(S.prices&&S.prices.us)||20000,no=Math.max(0,...list().map(p=>p.no||0))+1,ph=normPhone(String(b.phone||''))||'';
   S.patients.push({id,no,name:String(b.name||'مريض واتساب').replace(/\s+/g,' ').trim().slice(0,70),phone:ph,age:ageOf(b.age),ageLabel:String(b.age||'').slice(0,30),exam:String(b.exam||'').trim().slice(0,120)||'غير محدد',base,originalPrice:base,priceEdited:false,discount:0,reason:'',paid:0,
    status:'مؤجل',statusReason:TAG+' — واتساب'+(b.time?' • '+String(b.time).slice(0,80):''),statusBy:'واتساب',statusAt:stamp(),clinic:clinic(),regBy:'واتساب',regAt:b.at||stamp(),wa:true,waBooking:b.id,waNotes:String(b.notes||'').slice(0,200),referrer:''});
   added.push(b.name);mark(b.id)}
  if(added.length){audit('تسجيل آلي من واتساب — '+added.join('، '));render();toast('📱 حجز جديد من واتساب: '+added.join('، '));try{if(role()!=='doctor')playSound('رسالة جديدة')}catch(e){}}
 }catch(e){console.warn('bookings',e)}finally{busy=false}}
 setInterval(pull,60000);setTimeout(pull,8000);document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')setTimeout(pull,1500)});
 // Show the tag and turn «للانتظار» into «✓ وصل» on booking rows.
 function tag(){document.querySelectorAll('[data-id^="wa-"]').forEach(row=>{const p=S.patients.find(x=>x.id===row.dataset.id);if(!p)return;
   if(!row.querySelector('.wa-tag')){const t=el('span',TAG,'wa-tag');t.title='انسجل تلقائيًا من حجز واتساب'+(p.waNotes&&p.waNotes!=='لا يوجد'?' • '+p.waNotes:'');const nm=row.querySelector('.cp,b,strong,td:nth-child(2)');(nm&&nm.parentNode?nm.parentNode:row).append(t)}
   if(p.status==='مؤجل'&&!p.arrivedAt)row.querySelectorAll('button').forEach(b=>{if(/للانتظار|إعادة للانتظار|وصل/.test(b.textContent)){b.textContent='✓ وصل';b.title='المريض وصل — يدخل الانتظار وينقبض المبلغ';b.classList.add('b-arrive');b.style.cssText+=';background:#25a35a;color:#fff;border-color:#25a35a'}else if(/قبض/.test(b.textContent)&&!/استرجاع/.test(b.textContent))b.remove()})})}
 const _r=render;render=function(){const r=_r.apply(this,arguments);try{tag()}catch(e){console.error(e)}return r};try{tag()}catch(e){}
 // Backup of the whole day to n8n (doctor + secretary screens).
 const backupRole=roleName()==='الطبيب'||role()==='secretary';let lastBody='';
 function backup(){if(!backupRole||!cloud.user||!navigator.onLine)return;try{const c=clinic(),own=x=>!x.clinic||x.clinic===c;const data={patients:S.patients.filter(own),ledger:S.ledger.filter(own),expenses:(S.expenses||[]).filter(own),closes:(S.closes||[]).filter(own),messages:(S.messages||[]).filter(own).slice(0,200),audit:(S.audit||[]).filter(own).slice(0,500)};
  if(!data.patients.length&&!data.ledger.length)return;const body=JSON.stringify({clinic:CLINIC_ID,day:S.day,by:roleName(),data});if(body===lastBody)return;lastBody=body;
  fetch(BU,{method:'POST',headers:{'Content-Type':'text/plain;charset=utf-8'},body,keepalive:body.length<60000}).then(r=>{if(!r.ok)lastBody=''}).catch(()=>{lastBody=''})}catch(e){console.warn('backup',e)}}
 setInterval(backup,10*60000);setTimeout(backup,30000);document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden')backup()});
 window.__pullBookings=pull;window.__backupNow=()=>{lastBody='';backup()};
})();
</script>
"""

for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'id="v22js"' in s: print('already', f); continue
    old = s[s.index("BUILD='"):].split("'")[1]; s = s.replace("BUILD='%s'" % old, "BUILD='%s'" % BUILD)
    s = s.replace("connect-src 'self' https://*.googleapis.com wss://*.googleapis.com;", "connect-src 'self' https://*.googleapis.com wss://*.googleapis.com https://radiraq.app.n8n.cloud;")
    s = s.rstrip(); assert s.endswith('</body></html>')
    p.write_text(s[:-len('</body></html>')] + JS + '</body></html>\n', encoding='utf-8'); print('patched', f)
(T / 'version.txt').write_text(BUILD + '\n')
print('BUILD', BUILD)
