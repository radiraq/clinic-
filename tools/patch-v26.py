#!/usr/bin/env python3
"""v0.26 (all six test screens) — «مرضى اليوم» counts only patients who are actually in the clinic.
WhatsApp / phone bookings that have not arrived yet (wa, no arrivedAt, status «مؤجل») were counted in
«مرضى اليوم», so the number never matched «مكتمل» at the end of the day. They are now shown separately
as «+N حجز لم يصل» under the card (and on the secretary's «حساب اليوم» line)."""
import pathlib, time
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
FILES = ['doctor-test.html', 'doctor-karma-test.html', 'secretary-test.html',
         'secretary-karma-test.html', 'writer-test.html', 'writer-karma-test.html']
BUILD = time.strftime('%Y%m%d%H%M%S')
BK = "p.wa&&!p.arrivedAt&&p.status==='مؤجل'"
NOTE = "booked.length?'+ '+booked.length+' حجز لم يصل':"

COMMON = [
 ("let L=list(),active=L.filter(p=>p.status!=='ملغي'),",
  "let L=list(),booked=L.filter(p=>%s),active=L.filter(p=>p.status!=='ملغي'&&!booked.includes(p))," % BK),
]
STAFF = [("['مرضى اليوم',active.length,'']", "['مرضى اليوم',active.length,%s'']" % NOTE)]
SEC = [
 ("['مرضى اليوم',active.length,'جميع المراجعين التجريبيين']",
  "['مرضى اليوم',active.length,%s'جميع المراجعين التجريبيين']" % NOTE),
 ("done=P.filter(p=>p.status==='مكتمل').length;",
  "done=P.filter(p=>p.status==='مكتمل').length,here=P.length-booked.length;"),
 ("'مرضى اليوم: '+P.length+' • منجز: '+done+",
  "'مرضى اليوم: '+here+' • منجز: '+done+(booked.length?' • حجز لم يصل: '+booked.length:'')+"),
]

for f in FILES:
    p = T / f; s = p.read_text(encoding='utf-8')
    if 'booked=L.filter(' in s: print('already', f); continue
    for a, b in COMMON + (SEC if f.startswith('secretary') else STAFF):
        n = s.count(a); assert n == 1, (f, n, a[:70]); s = s.replace(a, b)
    old = s[s.index("BUILD='"):].split("'")[1]; s = s.replace("BUILD='%s'" % old, "BUILD='%s'" % BUILD)
    p.write_text(s, encoding='utf-8'); print('patched', f)
(T / 'version.txt').write_text(BUILD + '\n')
print('BUILD', BUILD)
