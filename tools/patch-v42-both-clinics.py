"""v42 — one staff account can work in both clinics (Fallujah and Al-Karma).

A users doc may carry clinics:['fallujah','karma']. Staff screens accept the account
if its clinic matches OR the screen's clinic is in that list. The doctor's account
list shows such accounts on both doctor screens, with a «🏥 العيادتين» toggle.
Firestore rules must accept the same (staffOf checks clinics too).
"""
import glob, time, pathlib

T = pathlib.Path(__file__).resolve().parent.parent / 'test'
BUILD = time.strftime('%Y%m%d%H%M%S')
BOTH = "['fallujah','karma']"

for f in sorted(T.glob('*.html')):
    s = f.read_text(encoding='utf-8')
    if 'v42both' in s:
        print('already', f.name); continue
    n0 = s
    # staff screens: role check
    s = s.replace("s.data().clinic===CLINIC_ID", "(s.data().clinic===CLINIC_ID||(s.data().clinics||[]).includes(CLINIC_ID))")
    # doctor screens: account list + toggle
    s = s.replace("filter(u=>u.clinic===CLINIC_ID)", "filter(u=>u.clinic===CLINIC_ID||(u.clinics||[]).includes(CLINIC_ID))")
    old = "root.append(row)})}"
    if 'function renderSecretaryAccount' in s:
        assert old in s, f.name
        tog = ("const both=(u.clinics||[]).length>1;const tb=btn(both?'🏥 العيادتين ✓':'🏥 العيادتين',async()=>{if(!await askDialog(both?('حساب '+u.username+' يرجع لعيادة وحدة بس؟'):('حساب '+u.username+' يشتغل بالفلوجة والكرمة؟'),{ok:'نعم'}))return;"
               "try{await FB.updateDoc(FB.doc(cloud.db,'users',u.uid),{clinics:both?[u.clinic]:" + BOTH + "});audit((both?'عيادة وحدة':'العيادتين')+' — حساب '+u.username)}catch(err){toast('تعذر التعديل: '+(err.code||err.message))}});"
               "tb.title='يشتغل بالعيادتين';if(both)tb.style.borderColor='#5fd38d';row.append(tb);/*v42both*/")
        i = s.index('function renderSecretaryAccount'); j = s.index(old, i)
        s = s[:j] + tog + s[j:]
    if s != n0:
        s = s.replace("BUILD='%s'" % s[s.index("BUILD='"):].split("'")[1], "BUILD='%s'" % BUILD, 1)
        if 'v42both' not in s:
            s = s.replace("<script id=\"v41pw\">", "<script id=\"v41pw\">/*v42both*/", 1)
        f.write_text(s, encoding='utf-8'); print('patched', f.name)
(T / 'version.txt').write_text(BUILD + '\n'); print('BUILD', BUILD)
