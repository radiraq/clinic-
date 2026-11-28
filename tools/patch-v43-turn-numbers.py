"""v43 — turn numbers count only real patients in the queue.

Cancelled patients and phone/WhatsApp bookings that haven't arrived no longer
push the next turn number up, so the sequence has no gaps (1, 2, 3 ...).
"""
import pathlib, time
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
B = time.strftime('%Y%m%d%H%M%S')
REAL = "(x=>x.status!=='ملغي'&&!((x.tel||x.wa)&&!x.arrivedAt&&x.status==='مؤجل'))"
for f in sorted(T.glob('*.html')):
    s = f.read_text(encoding='utf-8')
    if 'v43turns' in s: print('already', f.name); continue
    a = "let no=Math.max(0,...list().map(p=>p.no))+1;"
    b = "Math.max(0,...list().filter(x=>x.id!==id).map(x=>x.no||0))+1"
    assert s.count(a) == 1 and s.count(b) == 1, f.name
    s = s.replace(a, "let no=Math.max(0,...list().filter(%s).map(p=>p.no||0))+1;/*v43turns*/" % REAL)
    s = s.replace(b, "Math.max(0,...list().filter(x=>x.id!==id).filter(%s).map(x=>x.no||0))+1" % REAL)
    s = s.replace("BUILD='%s'" % s[s.index("BUILD='"):].split("'")[1], "BUILD='%s'" % B, 1)
    f.write_text(s, encoding='utf-8'); print('patched', f.name)
(T / 'version.txt').write_text(B + '\n')
