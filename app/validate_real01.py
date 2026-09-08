from pathlib import Path
import json, re, sys
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def ck(n,v,d=''): checks.append({'name':n,'ok':bool(v),'detail':str(d)})
cat=json.loads((ROOT/'content/catalog.json').read_text(encoding='utf-8'))
sources=json.loads((ROOT/'content/sources/sources.json').read_text(encoding='utf-8'))
sids={s['id'] for s in sources['sources']}
lessons=[]
for p in sorted((ROOT/'content/lessons').glob('*.json')): lessons.append(json.loads(p.read_text(encoding='utf-8')))
ck('28_topics',sum(len(c['topics']) for c in cat['chambers'])==28,sum(len(c['topics']) for c in cat['chambers']))
ck('3_real_lessons',len(lessons)==3,len(lessons))
for l in lessons:
 ck(f'{l["id"]}:six_sections',len(l['sections'])==6,len(l['sections']))
 ck(f'{l["id"]}:source_refs',all(x in sids for x in l['sources']),l['sources'])
 ck(f'{l["id"]}:reflection',bool(l.get('reflection_prompt')))
 ck(f'{l["id"]}:transmission',bool(l.get('transmission_question')))
html=(ROOT/'projects/golden-journey/index.html').read_text(encoding='utf-8')
js=(ROOT/'projects/golden-journey/app.js').read_text(encoding='utf-8')
css=(ROOT/'projects/golden-journey/styles.css').read_text(encoding='utf-8')
ck('no_community','community' not in (html+js).lower())
ck('semantic_text','<main' in html and '<section' in html)
ck('reduced_motion','prefers-reduced-motion' in css)
ck('self_reported','SELF_REPORTED' in js)
ck('independent_false','independentlyVerified:false' in js)
ck('browser_e2e_harness','REAL01_E2E_PASS' in js and 'runE2E' in js and 'verifyE2E' in js)
ck('no_user_innerhtml',not bool(re.search(r'innerHTML\s*=\s*[^`\'\"]',js)))
ck('canonical_home_asset',(ROOT/'projects/golden-journey/assets/sanctuaire.png').exists())
ck('mobile_asset',(ROOT/'projects/golden-journey/assets/mobile-home.png').exists())
out={'mission':'LUMEN-REAL-01','ok':all(x['ok'] for x in checks),'checks':checks}
print(json.dumps(out,ensure_ascii=False,indent=2))
sys.exit(0 if out['ok'] else 1)
