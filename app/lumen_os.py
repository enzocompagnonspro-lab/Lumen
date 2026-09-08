from __future__ import annotations
import argparse, json, hashlib, zipfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
def load(rel:str)->Any:return json.loads((ROOT/rel).read_text(encoding='utf-8-sig'))
def save(rel:str,obj:Any):
 p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
def sha(p:Path):return hashlib.sha256(p.read_bytes()).hexdigest()
def status():return load('state/status.json')
def event(kind,message,data=None):
 s=status();eid=int(s.get('last_event_id',0))+1;s['last_event_id']=eid;save('state/status.json',s);rec={'id':eid,'ts':now(),'kind':kind,'message':message,'data':data or {}};f=ROOT/'state/events.jsonl';f.parent.mkdir(parents=True,exist_ok=True)
 with f.open('a',encoding='utf-8') as h:h.write(json.dumps(rec,ensure_ascii=False)+'\n')
 return rec
def mission(mid=None):
 data=load('registry/missions.json')['missions'];target=mid or status().get('current_mission');return next((m for m in data if m['id']==target),data[0])
def task_map(m=None):return {t['id']:t for t in (m or mission())['tasks']}
def deps_done(t,m=None):
 tm=task_map(m);return all(tm.get(d,{}).get('status')=='DONE' for d in t.get('blocked_by',[]))
def next_task(m=None):
 m=m or mission()
 for t in m['tasks']:
  if t.get('status')=='READY' and deps_done(t,m):return t
 return None
def update_task(tid,new_status,note=None):
 data=load('registry/missions.json')
 for m in data['missions']:
  for t in m['tasks']:
   if t['id']==tid:
    t['status']=new_status
    if note is not None:t['note']=note
 save('registry/missions.json',data)
def validate():
 canon=load('config/canon.json');assets=load('registry/assets.json')['assets'];checks=[]
 def add(n,o,d=''):checks.append({'name':n,'ok':bool(o),'detail':d})
 add('canon_name',canon.get('name')=='LUMEN');add('community_disabled',canon.get('community_enabled') is False);add('gold_color',canon.get('palette',{}).get('gold')=='#CFAE6A');add('paths',all(k in canon.get('paths',{}) for k in ['VOIR','COMPRENDRE','AGIR']))
 for a in assets:
  p=ROOT/a['file'];add('asset_exists:'+a['id'],p.exists(),str(p));
  if p.exists():add('asset_hash:'+a['id'],sha(p)==a['sha256'],sha(p))
 html=(ROOT/'projects/golden-sanctuary/index.html').read_text(encoding='utf-8');add('no_community_in_scene','community' not in html.lower() and 'communauté' not in html.lower());add('protected_golden_layers',html.count('data-depth=')>=8)
 ok=all(c['ok'] for c in checks);rep={'ts':now(),'ok':ok,'checks':checks};save('evidence/validation-latest.json',rep);s=status();s['last_validation']=rep['ts'];s['health']='PASS' if ok else 'FAIL';save('state/status.json',s);event('VALIDATION','LUMEN validation '+('PASS' if ok else 'FAIL'),{'checks':len(checks)});return rep
def living_tech():
 p=ROOT/'projects/golden-sanctuary/index.html';text=p.read_text(encoding='utf-8') if p.exists() else '';k=load('registry/knowledge.json');checks=[]
 def add(n,o,d=''):checks.append({'name':n,'ok':bool(o),'detail':d})
 add('index_exists',p.exists());add('knowledge_registry',len(k.get('categories',[]))==6 and len(k.get('contents',[]))>=7,f"categories={len(k.get('categories',[]))}, contents={len(k.get('contents',[]))}")
 for marker in ['knowledgeSearch','renderResults','data-category','data-content','STATE_KEY','localStorage','article-monde-lucide.png','articleHome','portalTraverse']:add('contains:'+marker,marker in text)
 add('six_category_hotspots',text.count('data-category=')>=6,str(text.count('data-category=')));add('featured_content_hotspots',text.count('data-content=')>=7,str(text.count('data-content=')));add('golden_depth_layers_preserved',text.count('data-depth=')>=8,str(text.count('data-depth=')));add('voir_agir_still_governed',text.count('data-locked="true"')>=2);add('no_community','community' not in text.lower() and 'communauté' not in text.lower());add('article_asset',(ROOT/'projects/golden-sanctuary/assets/article-monde-lucide.png').exists())
 ok=all(c['ok'] for c in checks);rep={'ts':now(),'iteration':'LIVING-01','ok':ok,'checks':checks};save('evidence/living-system-technical-qa.json',rep);update_task('L-006','DONE' if ok else 'READY')
 if ok:
  update_task('L-007','READY');s=status();s['current_task']='L-007';s['next_action']='Run scripts/CERTIFY-LIVING-01.ps1 on Windows for observed browser QA.';save('state/status.json',s)
 event('QA_TECH_LIVING_01','Living technical QA '+('PASS' if ok else 'FAIL'),{'checks':len(checks)});return rep
def living_visual():
 f=ROOT/'evidence/browser-qa-living-01.json';browser=None
 if f.exists():
  try:browser=json.loads(f.read_text(encoding='utf-8-sig'))
  except:browser=None
 tech=load('evidence/living-system-technical-qa.json') if (ROOT/'evidence/living-system-technical-qa.json').exists() else living_tech();observed=bool(browser and browser.get('result')=='PASS')
 checks=[{'name':'technical_qa','ok':bool(tech.get('ok'))},{'name':'browser_observed','ok':observed,'detail':(browser or {}).get('result','NOT_OBSERVED') if isinstance(browser,dict) else 'NOT_OBSERVED'},{'name':'golden_rest_fidelity','ok':bool(observed and browser.get('checks',{}).get('golden_rest_fidelity'))},{'name':'library_idle_fidelity','ok':bool(observed and browser.get('checks',{}).get('library_idle_fidelity'))},{'name':'search_state_rendered','ok':bool(observed and browser.get('checks',{}).get('search_state_rendered'))},{'name':'article_fidelity','ok':bool(observed and browser.get('checks',{}).get('article_fidelity'))}]
 ok=all(x['ok'] for x in checks);rep={'ts':now(),'iteration':'LIVING-01','result':'PASS' if ok else ('PENDING_BROWSER_OBSERVATION' if tech.get('ok') and not observed else 'ITERATE'),'ok':ok,'checks':checks,'browser_report':browser or {}};save('evidence/living-system-visual-qa.json',rep)
 if ok:
  update_task('L-007','DONE');update_task('L-008','READY');s=status();s['current_task']='L-008';s['next_action']='Independent review LUMEN-LIVING-SYSTEM-01 required; do not auto-approve.';save('state/status.json',s)
 event('QA_VISUAL_LIVING_01','Living visual QA '+rep['result'],{'checks':len(checks)});return rep

def journey_tech():
 p=ROOT/'projects/golden-sanctuary/index.html';text=p.read_text(encoding='utf-8') if p.exists() else '';j=load('registry/journey.json');checks=[]
 def add(n,o,d=''):checks.append({'name':n,'ok':bool(o),'detail':d})
 add('journey_registry',len(j.get('chambers',[]))==7,str(len(j.get('chambers',[]))))
 add('journey_asset',(ROOT/'projects/golden-sanctuary/assets/carte-du-voyage.png').exists())
 for marker in ['scene-journey','data-chamber','syncJourney','journey.unlocked','e2e-persist','sessionStorage','libraryJourney','articleJourney']:add('contains:'+marker,marker in text)
 add('seven_chamber_hotspots',text.count('data-chamber=')>=7,str(text.count('data-chamber=')))
 add('golden_depth_layers_preserved',text.count('data-depth=')>=8,str(text.count('data-depth=')))
 add('no_community','community' not in text.lower() and 'communauté' not in text.lower())
 ok=all(c['ok'] for c in checks);rep={'ts':now(),'iteration':'LIVING-02','ok':ok,'checks':checks};save('evidence/journey-system-technical-qa.json',rep);update_task('J-006','DONE' if ok else 'READY')
 if ok:
  update_task('J-007','READY');s=status();s['current_task']='J-007';s['next_action']='Run scripts/CERTIFY-LIVING-02.ps1 on Windows for browser E2E and persistence QA.';save('state/status.json',s)
 event('QA_TECH_LIVING_02','Journey technical QA '+('PASS' if ok else 'FAIL'),{'checks':len(checks)});return rep

def journey_visual():
 f=ROOT/'evidence/browser-qa-living-02.json';browser=None
 if f.exists():
  try:browser=json.loads(f.read_text(encoding='utf-8-sig'))
  except:browser=None
 tech=load('evidence/journey-system-technical-qa.json') if (ROOT/'evidence/journey-system-technical-qa.json').exists() else journey_tech();observed=bool(browser and browser.get('result')=='PASS')
 ck=(browser or {}).get('checks',{}) if isinstance(browser,dict) else {}
 checks=[{'name':'technical_qa','ok':bool(tech.get('ok'))},{'name':'browser_observed','ok':observed,'detail':(browser or {}).get('result','NOT_OBSERVED') if isinstance(browser,dict) else 'NOT_OBSERVED'},{'name':'golden_rest_fidelity','ok':bool(observed and ck.get('golden_rest_fidelity'))},{'name':'journey_idle_fidelity','ok':bool(observed and ck.get('journey_idle_fidelity'))},{'name':'journey_interaction_rendered','ok':bool(observed and ck.get('journey_interaction_rendered'))},{'name':'e2e_seed','ok':bool(observed and ck.get('e2e_seed'))},{'name':'persistence_after_reload','ok':bool(observed and ck.get('persistence_after_reload'))}]
 ok=all(x['ok'] for x in checks);rep={'ts':now(),'iteration':'LIVING-02','result':'PASS' if ok else ('PENDING_BROWSER_OBSERVATION' if tech.get('ok') and not observed else 'ITERATE'),'ok':ok,'checks':checks,'browser_report':browser or {}};save('evidence/journey-system-visual-qa.json',rep)
 if ok:
  update_task('J-007','DONE');update_task('J-008','READY');s=status();s['current_task']='J-008';s['next_action']='Independent review LUMEN-LIVING-SYSTEM-02 required; do not auto-approve.';save('state/status.json',s)
 event('QA_VISUAL_LIVING_02','Journey visual QA '+rep['result'],{'checks':len(checks)});return rep

def make_journey_pack():
 tm=task_map();ready=tm.get('J-007',{}).get('status')=='DONE' and tm.get('J-008',{}).get('status')=='READY'
 if not ready:return {'ok':False,'status':'NOT_READY','detail':'J-007 must be DONE and J-008 READY'}
 out=ROOT/'LUMEN-REVIEW-PACK-LIVING-02.zip';files=['evidence/browser-golden-rest-living-02.png','evidence/browser-journey-idle-living-02.png','evidence/browser-journey-vision-living-02.png','evidence/browser-journey-persist-living-02.png','evidence/browser-qa-living-02.json','evidence/journey-system-technical-qa.json','evidence/journey-system-visual-qa.json','evidence/validation-latest.json','projects/golden-sanctuary/index.html','registry/knowledge.json','registry/journey.json','state/status.json','registry/missions.json']
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for rel in files:
   p=ROOT/rel
   if p.exists():z.write(p,rel)
 event('REVIEW_PACK','Living System 02 review pack created',{'file':out.name});return {'ok':True,'status':'READY','file':out.name,'path':str(out)}

def auto_run():
 out=[['VALIDATE',validate()['ok']]];m=mission()
 if m['id']=='M-0002-LUMEN-LIVING-SYSTEM-01':
  t=living_tech();out.append(['L-006',t['ok']]);nt=next_task()
  if nt and nt['id']=='L-007' and nt.get('safe_auto'):r=living_visual();out.append(['L-007',r['ok']])
 elif m['id']=='M-0003-LUMEN-LIVING-SYSTEM-02':
  t=journey_tech();out.append(['J-006',t['ok']]);nt=next_task()
  if nt and nt['id']=='J-007' and nt.get('safe_auto'):r=journey_visual();out.append(['J-007',r['ok']])
 nt=next_task()
 if nt and not nt.get('safe_auto',False):event('REVIEW_OR_HUMAN_GATE','Auto-run stopped before non-automatic task',{'task':nt['id'],'title':nt['title']})
 return out
def make_living_pack():
 tm=task_map();ready=tm.get('L-007',{}).get('status')=='DONE' and tm.get('L-008',{}).get('status')=='READY'
 if not ready:return {'ok':False,'status':'NOT_READY','detail':'L-007 must be DONE and L-008 READY'}
 out=ROOT/'LUMEN-REVIEW-PACK-LIVING-01.zip';files=['evidence/browser-golden-rest-living-01.png','evidence/browser-library-idle-living-01.png','evidence/browser-library-search-living-01.png','evidence/browser-article-living-01.png','evidence/browser-qa-living-01.json','evidence/living-system-technical-qa.json','evidence/living-system-visual-qa.json','evidence/validation-latest.json','projects/golden-sanctuary/index.html','registry/knowledge.json','state/status.json','registry/missions.json']
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for rel in files:
   p=ROOT/rel
   if p.exists():z.write(p,rel)
 event('REVIEW_PACK','Living System review pack created',{'file':out.name});return {'ok':True,'status':'READY','file':out.name,'path':str(out)}
def print_status():
 s=status();m=mission();print(json.dumps({'status':s,'mission':{'id':m['id'],'title':m['title'],'status':m['status'],'iteration':m.get('iteration')},'next_task':next_task(m)},indent=2,ensure_ascii=False))
def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True)
 for c in ['status','validate','next','auto','qa-living-tech','qa-living-visual','living-review-pack','qa-journey-tech','qa-journey-visual','journey-review-pack']:sub.add_parser(c)
 a=ap.parse_args()
 if a.cmd=='status':print_status()
 elif a.cmd=='validate':print(json.dumps(validate(),indent=2,ensure_ascii=False))
 elif a.cmd=='next':print(json.dumps(next_task(),indent=2,ensure_ascii=False))
 elif a.cmd=='auto':print(json.dumps(auto_run(),indent=2,ensure_ascii=False))
 elif a.cmd=='qa-living-tech':print(json.dumps(living_tech(),indent=2,ensure_ascii=False))
 elif a.cmd=='qa-living-visual':print(json.dumps(living_visual(),indent=2,ensure_ascii=False))
 elif a.cmd=='living-review-pack':print(json.dumps(make_living_pack(),indent=2,ensure_ascii=False))
 elif a.cmd=='qa-journey-tech':print(json.dumps(journey_tech(),indent=2,ensure_ascii=False))
 elif a.cmd=='qa-journey-visual':print(json.dumps(journey_visual(),indent=2,ensure_ascii=False))
 elif a.cmd=='journey-review-pack':print(json.dumps(make_journey_pack(),indent=2,ensure_ascii=False))
if __name__=='__main__':main()
