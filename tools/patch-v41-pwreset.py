"""v41 — password recovery through the clinic email (dr.radiraq@gmail.com).

Every account's login email becomes dr.radiraq+<username>@gmail.com, which Gmail
delivers to the clinic inbox, so «نسيت كلمة السر؟» can send a reset link there.
Usernames stay the same for staff. Old @fallujah.clinic accounts keep working:
login tries the new address first, then the old one. When MIGRATE is on, an old
account that logs in gets a one-time confirm link (to the clinic inbox) that moves
it to the new address. The doctor is recognised by his fixed account id, so his
screens keep working after his email changes (Firestore rules match by id too).

usage: python3 tools/patch-v41-pwreset.py MIGRATE(0|1) file.html [file.html ...]
"""
import sys

DOCTOR_UID = 'eTJZ2M7JvjUU6XwaIZugObD4Er43'
OLD_DEF = "DOCTOR_EMAIL='doctor@fallujah.clinic',EMAIL_DOMAIN='fallujah.clinic';"

HELPERS = r"""
var DOCTOR_UID='%(uid)s',RECOVERY_MAIL='dr.radiraq@gmail.com',MIGRATE_MAIL=%(migrate)s;
function newMail(u){return 'dr.radiraq+'+String(u).trim().toLowerCase()+'@gmail.com'}
function isDoc(user){return !!user&&(user.uid===DOCTOR_UID||user.email===DOCTOR_EMAIL||user.email===newMail('doctor'))}
async function moveToClinicMail(user,to){if(!MIGRATE_MAIL||!user||!to)return;const k='clinicLive.mailMove.'+user.uid;try{if(Date.now()-Number(localStorage.getItem(k)||0)<12*3600e3)return}catch{}try{const t=await user.getIdToken();const r=await fetch('https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key='+FB_CONFIG.apiKey,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({requestType:'VERIFY_AND_CHANGE_EMAIL',idToken:t,newEmail:to})});if(r.ok)try{localStorage.setItem(k,String(Date.now()))}catch{}}catch{}}
async function signInAny(auth,email,pw){const local=String(email).split('@')[0];if(!/@fallujah\.clinic$/.test(email))return FB.signInWithEmailAndPassword(auth,email,pw);try{return await FB.signInWithEmailAndPassword(auth,newMail(local),pw)}catch(e){if(!/invalid-credential|user-not-found|wrong-password|invalid-login/.test(e&&e.code||''))throw e}const cred=await FB.signInWithEmailAndPassword(auth,email,pw);if(typeof cloud!=='undefined'&&auth===cloud.auth&&!/^(hajz|hajzk|n8n-bookings)$/.test(local))moveToClinicMail(cred.user,newMail(local));return cred}
async function forgotPw(u,out){u=String(u||'').trim().toLowerCase();if(!u){out.textContent='اكتب اسم المستخدم أولاً، بعدين اضغط «نسيت كلمة السر؟».';return}if(!navigator.onLine){out.textContent='يحتاج إنترنت.';return}try{await FB.sendPasswordResetEmail(cloud.auth,newMail(u));out.textContent='✓ انرسل رابط تغيير كلمة السر لإيميل العيادة ('+RECOVERY_MAIL+'). افتحه من إيميل العيادة واكتب كلمة سر جديدة. إذا ما وصل، يحتاج الحساب يتحوّل لإيميل العيادة أولاً — الطبيب يسوّي حساب جديد.'}catch(e){out.textContent='تعذر الإرسال: '+(e&&e.code||e)}}
"""

FORGOT_BTN = '<button type="button" id="forgotPw" style="background:transparent;border:0;color:#8fc1ff;text-decoration:underline;font-size:.95em">نسيت كلمة السر؟</button>'


def patch(path, migrate):
    s = open(path, encoding='utf-8').read()
    if 'function forgotPw(' in s:
        print('already patched:', path); return
    assert OLD_DEF in s, path
    s = s.replace(OLD_DEF, OLD_DEF + HELPERS % {'uid': DOCTOR_UID, 'migrate': 'true' if migrate else 'false'}, 1)
    s = s.replace('cloud.user.email===DOCTOR_EMAIL', 'isDoc(cloud.user)')
    s = s.replace('(user.email===DOCTOR_EMAIL)', '(isDoc(user))').replace('{if(user.email===DOCTOR_EMAIL)', '{if(isDoc(user))').replace('{return user.email===DOCTOR_EMAIL}', '{return isDoc(user)}')
    s = s.replace('FB.signInWithEmailAndPassword(', 'signInAny(')
    # the helper itself must keep calling Firebase directly
    s = s.replace('return signInAny(auth,email,pw)', 'return FB.signInWithEmailAndPassword(auth,email,pw)')
    s = s.replace('try{return await signInAny(auth,newMail(local),pw)}', 'try{return await FB.signInWithEmailAndPassword(auth,newMail(local),pw)}')
    s = s.replace('const cred=await signInAny(auth,email,pw)', 'const cred=await FB.signInWithEmailAndPassword(auth,email,pw)')
    # new staff accounts are created on the clinic address straight away
    s = s.replace('createUserWithEmailAndPassword(a2,emailFor(username),password)', 'createUserWithEmailAndPassword(a2,newMail(username),password)')
    s = s.replace('لتغيير كلمة المرور: أنشئ حسابًا باسم جديد وأوقف القديم.',
                  'نسيت كلمة المرور؟ من شاشة الدخول اضغط «نسيت كلمة السر؟» ويوصل رابط لإيميل العيادة dr.radiraq@gmail.com.')
    # «نسيت كلمة السر؟» on the login dialogs
    if 'id="secretaryLoginButton">دخول</button>' in s:
        s = s.replace('id="secretaryLoginButton">دخول</button>', 'id="secretaryLoginButton">دخول</button>' + FORGOT_BTN, 1)
        hook = "$('forgotPw').onclick=()=>forgotPw($('loginUsername').value,$('secretaryLoginError'));"
    else:
        assert 'id="doctorLoginButton">دخول</button>' in s, path
        s = s.replace('id="doctorLoginButton">دخول</button>', 'id="doctorLoginButton">دخول</button>' + FORGOT_BTN, 1)
        hook = "$('forgotPw').onclick=()=>forgotPw('doctor',$('doctorLoginError'));"
    i = s.rfind('</body>')
    s = s[:i] + '<script id="v41pw">' + hook + '</script>\n' + s[i:]
    # sanity: helpers still call Firebase directly
    assert s.count('FB.signInWithEmailAndPassword(') == 3, (path, s.count('FB.signInWithEmailAndPassword('))
    open(path, 'w', encoding='utf-8').write(s)
    print('patched:', path)


if __name__ == '__main__':
    mig = sys.argv[1] == '1'
    for p in sys.argv[2:]:
        patch(p, mig)
