#!/usr/bin/env python3
"""Build the writer (كاتبة) screens from the doctor screens.

The writer screen is exactly the doctor's screen (same layout and the same
patient actions) minus everything about money: no cash/accounts, expenses,
settings (prices, staff accounts), activity log, backup or amounts in the
patient history. She can register patients. Messages are signed "الكاتبة".

Run after every change to the doctor screens:
    python3 tools/make-writer.py
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / 'test'
LOGIN = (ROOT / 'tools' / 'writer-login-dialog.html').read_text(encoding='utf-8')

PAIRS = [
    # doctor file, writer file, clinic label, manifest, title, apple title, clinic-specific login heading
    ('doctor-test.html', 'writer-test.html', 'الفلوجة', 'writer-test.webmanifest',
     'عيادتي | شاشة الكاتبة — تجريبية', 'الكاتبة'),
    ('doctor-karma-test.html', 'writer-karma-test.html', 'الكرمة', 'writer-karma-test.webmanifest',
     'عيادتي | شاشة الكاتبة (الكرمة) — تجريبية', 'كاتبة الكرمة'),
]

WRITER_LAYER = r"""<style>
#nav [data-page=cash],#nav [data-page=expenses],#nav [data-page=settings],.clinic-switch,#cash,#expenses,#settings,#audit>.card:last-child,#backupBtn,#audit th:nth-child(4),#historyRows td:nth-child(4){display:none!important}
.w-done-tag{font-size:12px;color:#7bdbc2;margin-inline-start:6px;font-weight:700}
</style>
<script>
(function(){
 // Writer layer: the doctor's screen minus anything about money.
 const FORBIDDEN=['cash','expenses','settings'];
 const CK='writerCopied.'+CLINIC_ID;
 function copied(){try{const x=JSON.parse(localStorage.getItem(CK)||'{}');return x.day===day()?x:{day:day(),ids:[]}}catch(e){return{day:day(),ids:[]}}}
 window.onCopied=function(p){if(!p||!p.id)return;const c=copied();if(!c.ids.includes(p.id))c.ids.push(p.id);try{localStorage.setItem(CK,JSON.stringify(c))}catch(e){}tidy()};
 function tidy(){
  if(FORBIDDEN.includes(page)){document.querySelector('[data-page=queue]').click();return}
  const ids=copied().ids;
  document.querySelectorAll('#rows tr').forEach(tr=>{
   const nm=tr.querySelector('td:nth-child(2)');
   if(nm){const has=nm.querySelector('.w-done-tag');if(tr.dataset.id&&ids.includes(tr.dataset.id)){if(!has)nm.append(el('span','✓ نسختيه','w-done-tag'))}else if(has)has.remove()}
  });
 }
 const base=render;render=function(){const r=base.apply(this,arguments);try{tidy()}catch(e){console.error(e)}return r};
 const lg=document.querySelector('aside .logo');if(lg)lg.textContent='✎ شاشة الكاتبة';
 document.querySelector('.aside-foot').innerHTML='الكاتبة — عيادة '+clinic()+'<br>نسخة تجريبية • بيانات وهمية فقط';
 $('heading').textContent='شاشة الكاتبة';
 const au=document.querySelector('#nav [data-page=audit]');if(au)au.textContent='≡ سجل المرضى';
 try{tidy()}catch(e){}
})();
</script></body></html>"""


def must_replace(s, old, new, count=1, what=''):
    n = s.count(old)
    if n != count:
        sys.exit(f'make-writer: expected {count} of [{what or old[:60]}], found {n} — the doctor screen changed; update tools/make-writer.py')
    return s.replace(old, new)


def build(src, dst, label, manifest, title, apple):
    s = (TEST / src).read_text(encoding='utf-8')
    # Head: writer manifest, title, icon.
    s = re.sub(r'<link rel="manifest" href="[^"]*">', f'<link rel="manifest" href="{manifest}">', s, count=1)
    s = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', s, count=1)
    s = re.sub(r'apple-mobile-web-app-title" content="[^"]*"', f'apple-mobile-web-app-title" content="{apple}"', s, count=1)
    s = s.replace('href="../icon-doc-192.png"', 'href="../icon-sec-192.png"')
    # Role: writer; no cash; may register.
    # Same powers as the doctor's screen (enter, finish, defer, reorder, post void...),
    # but every message and action is signed as the writer.
    s = must_replace(s, "roleName=()=>({admin:'المدير',doctor:'الطبيب',secretary:'السكرتارية'}[role()])",
                     "roleName=()=>'الكاتبة'", what='roleName')
    s = must_replace(s, "$('heading').textContent='عيادتي';", "$('heading').textContent='شاشة الكاتبة';", what='heading')
    # Login: writer account (username + password) instead of the doctor's password.
    s, n = re.subn(r'<dialog id="doctorLogin".*?</dialog>', lambda m: LOGIN, s, count=1, flags=re.S)
    if n != 1: sys.exit('make-writer: doctor login dialog not found')
    s = must_replace(s, '<select style="display:none" id="role"',
                     '<button type="button" id="secretaryLogout" class="hidden">خروج</button><select style="display:none" id="role"', what='header logout')
    i, j = s.find('function showLogin('), s.find('var staffUsers=[];')
    if i < 0 or j < i: sys.exit('make-writer: login block not found')
    writer_login = """function showLogin(msg){document.querySelector('main').inert=true;document.querySelector('aside').inert=true;$('secretaryLogout').classList.add('hidden');$('loginSetupInfo').textContent=msg||'أدخلي اسم المستخدم وكلمة المرور اللي حددها الطبيب.';if(!$('secretaryLogin').open)$('secretaryLogin').showModal()}
function hideLogin(){document.querySelector('main').inert=false;document.querySelector('aside').inert=false;$('secretaryLogout').classList.remove('hidden');if($('secretaryLogin').open)$('secretaryLogin').close()}
async function checkRole(user){if(user.email===DOCTOR_EMAIL)return true;const k='clinicLive.writerOk.'+user.uid;try{const s=await FB.getDoc(FB.doc(cloud.db,'users',user.uid));const ok=s.exists()&&s.data().active===true&&s.data().clinic===CLINIC_ID&&s.data().role==='writer';try{ok?localStorage.setItem(k,'1'):localStorage.removeItem(k)}catch{}return ok}catch(e){return localStorage.getItem(k)==='1'}}
$('secretaryLogin').addEventListener('cancel',e=>{if(!cloud.user)e.preventDefault()});
$('secretaryLoginForm').onsubmit=async e=>{e.preventDefault();const u=$('loginUsername').value.trim().toLowerCase();$('secretaryLoginError').textContent='';$('secretaryLoginButton').disabled=true;try{await FB.signInWithEmailAndPassword(cloud.auth,u==='doctor'?DOCTOR_EMAIL:emailFor(u),$('loginPassword').value);$('secretaryLoginForm').reset()}catch(err){$('secretaryLoginError').textContent=authError(err)}finally{$('secretaryLoginButton').disabled=false}};
$('secretaryLogout').onclick=async()=>{if(await askDialog('تسجيل الخروج من هذا الجهاز؟',{ok:'خروج'}))FB.signOut(cloud.auth)};
"""
    s = s[:i] + writer_login + s[j:]
    s, n = re.subn(r"function afterLogin\(\)\{const F=FB;.*?\n", "function afterLogin(){}\n", s, count=1)
    if n != 1: sys.exit('make-writer: afterLogin not found')
    s = s.replace('هذا الحساب مو لهاي العيادة', 'هذا الحساب مو حساب كاتبة لهاي العيادة')
    # Writer heading inside the login dialog follows the clinic.
    s = s.replace('دخول الكاتبة — الفلوجة', 'دخول الكاتبة — ' + label)
    # Writer layer (hide everything about money).
    if not s.rstrip().endswith('</body></html>'): sys.exit('make-writer: unexpected file end')
    s = s.rstrip()[:-len('</body></html>')] + WRITER_LAYER + '\n'
    (TEST / dst).write_text(s, encoding='utf-8')
    print('built', dst, 'from', src)


for pair in PAIRS:
    build(*pair)
