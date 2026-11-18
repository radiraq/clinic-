#!/usr/bin/env python3
"""v0.9: doctor (and writer) screens pop up only the secretary's messages — the writer's
quick messages to the secretary no longer alert the doctor. Run make-writer.py after."""
import pathlib, sys
T = pathlib.Path(__file__).resolve().parent.parent / 'test'
OLD = "const incoming=fresh.filter(m=>m.clinic===clinic()&&m.from!==roleName())"
NEW = "const incoming=fresh.filter(m=>m.clinic===clinic()&&m.from!==roleName()&&m.from==='السكرتارية')"
for f in ['doctor-test.html', 'doctor-karma-test.html']:
    p = T / f; s = p.read_text(encoding='utf-8')
    if NEW in s: print('already', f); continue
    if s.count(OLD) != 1: sys.exit('patch-v09: notifyIncoming not found in ' + f)
    p.write_text(s.replace(OLD, NEW), encoding='utf-8'); print('patched', f)
