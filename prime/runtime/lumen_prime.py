#!/usr/bin/env python3
import argparse, json, sqlite3, re, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_DEFAULT = ROOT / 'memory' / 'lumen_prime.db'
ROUTER = json.loads((ROOT/'config/router.json').read_text(encoding='utf-8'))
MANIFEST = json.loads((ROOT/'config/model_manifest.json').read_text(encoding='utf-8'))
GATES = json.loads((ROOT/'config/safety_gates.json').read_text(encoding='utf-8'))
MODEL_POLICY = json.loads((ROOT/'config/model_policy.json').read_text(encoding='utf-8'))

NOW = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()

def conn(db):
    c = sqlite3.connect(str(db))
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c

def init_db(db):
    db = Path(db)
    db.parent.mkdir(parents=True, exist_ok=True)
    c = conn(db)
    c.executescript((ROOT/'memory/schema.sql').read_text(encoding='utf-8'))
    c.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('schema_version','1')")
    c.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('model_version',?)", (MANIFEST['version'],))
    c.commit(); c.close()
    return {'ok': True, 'db': str(db)}

def route(text):
    t = text.lower(); scored = []
    for r in ROUTER['routes']:
        score = sum(1 for k in r['match'] if k.lower() in t)
        if score:
            scored.append((score, r['expert']))
    scored.sort(key=lambda x: (-x[0], x[1]))
    chosen = []
    for _, name in scored:
        if name not in chosen:
            chosen.append(name)
        if len(chosen) >= ROUTER['max_parallel_experts']:
            break
    return chosen or [ROUTER['fallback']]

def choose_model(task, frontier_available=False, observed_model=None):
    frontier_tasks = {
        x for rule in MODEL_POLICY['selection_rules']
        if rule['prefer'] == 'frontier_preferred'
        for x in rule['tasks']
    }
    desired = 'frontier_preferred' if task in frontier_tasks else 'primary_fallback'
    fallback = MODEL_POLICY['primary_fallback']['display_name']
    if desired == 'frontier_preferred' and frontier_available and observed_model:
        selected = observed_model
        tier = 'FRONTIER_OBSERVED'
        verified = True
    else:
        selected = fallback
        tier = 'PRIMARY_FALLBACK'
        verified = bool(observed_model and observed_model.lower() == fallback.lower())
    return {
        'selected_display_name': selected,
        'tier': tier,
        'frontier_available': bool(frontier_available),
        'frontier_candidate_verified': bool(frontier_available and observed_model),
        'observed_runtime_model': observed_model,
        'claim_verified': verified
    }

def upsert_node(c, nid, ntype, title, payload, evidence='REPORTED', canonical=False, source_ref=None):
    c.execute(
        """INSERT INTO nodes(id,node_type,title,payload_json,evidence_status,canonical,source_ref,updated_at)
           VALUES(?,?,?,?,?,?,?,?)
           ON CONFLICT(id) DO UPDATE SET
             node_type=excluded.node_type,title=excluded.title,payload_json=excluded.payload_json,
             evidence_status=excluded.evidence_status,canonical=excluded.canonical,
             source_ref=excluded.source_ref,updated_at=excluded.updated_at""",
        (nid, ntype, title, json.dumps(payload, ensure_ascii=False), evidence,
         1 if canonical else 0, source_ref, NOW())
    )

def upsert_edge(c, source_id, relation, target_id, payload=None, evidence='REPORTED'):
    c.execute(
        """INSERT INTO edges(source_id,relation,target_id,payload_json,evidence_status,updated_at)
           VALUES(?,?,?,?,?,?)
           ON CONFLICT(source_id,relation,target_id) DO UPDATE SET
             payload_json=excluded.payload_json,evidence_status=excluded.evidence_status,
             updated_at=excluded.updated_at""",
        (source_id, relation, target_id, json.dumps(payload or {}, ensure_ascii=False), evidence, NOW())
    )

def sync_os(db, osroot):
    osroot = Path(osroot)
    required = ['config/canon.json','registry/knowledge.json','registry/journey.json','state/status.json']
    missing = [r for r in required if not (osroot/r).exists()]
    if missing:
        return {'ok': False, 'missing': missing}
    init_db(db)
    c = conn(db)
    canon = json.loads((osroot/'config/canon.json').read_text(encoding='utf-8'))
    knowledge = json.loads((osroot/'registry/knowledge.json').read_text(encoding='utf-8'))
    journey = json.loads((osroot/'registry/journey.json').read_text(encoding='utf-8'))
    status = json.loads((osroot/'state/status.json').read_text(encoding='utf-8'))

    upsert_node(c, 'canon:lumen', 'CANON', 'LUMEN Canon', canon, 'OBSERVED', True, str(osroot/'config/canon.json'))
    for cat in knowledge.get('categories', []):
        upsert_node(c, 'category:'+cat['id'], 'CATEGORY', cat['label'], cat, 'OBSERVED', True, str(osroot/'registry/knowledge.json'))
    for item in knowledge.get('contents', []):
        nid = 'content:'+item['id']
        upsert_node(c, nid, 'CONTENT', item['title'], item, 'OBSERVED', True, str(osroot/'registry/knowledge.json'))
        cid = 'category:'+item['category']
        if c.execute('SELECT 1 FROM nodes WHERE id=?', (cid,)).fetchone():
            upsert_edge(c, nid, 'BELONGS_TO', cid, {}, 'OBSERVED')

    chambers = journey.get('chambers', [])
    for ch in chambers:
        upsert_node(c, 'chamber:'+ch['id'], 'CHAMBER', ch['label'], ch, 'OBSERVED', True, str(osroot/'registry/journey.json'))
    ordered = sorted(chambers, key=lambda x: x.get('order', 999))
    for a, b in zip(ordered, ordered[1:]):
        upsert_edge(c, 'chamber:'+a['id'], 'NEXT', 'chamber:'+b['id'], {}, 'OBSERVED')
    for ch in chambers:
        unlock = ch.get('unlock')
        if isinstance(unlock, str) and unlock.endswith('.complete'):
            dep = unlock.split('.')[0]
            if c.execute('SELECT 1 FROM nodes WHERE id=?', ('chamber:'+dep,)).fetchone():
                upsert_edge(c, 'chamber:'+dep, 'UNLOCKS', 'chamber:'+ch['id'], {}, 'OBSERVED')

    c.execute(
        """INSERT OR REPLACE INTO memories(scope,key,value_json,evidence_status,provenance,updated_at)
           VALUES(?,?,?,?,?,?)""",
        ('system','lumen_os_status',json.dumps(status,ensure_ascii=False),'OBSERVED',str(osroot/'state/status.json'),NOW())
    )
    c.execute(
        'INSERT INTO events(event_type,payload_json,evidence_status,provenance,ts) VALUES(?,?,?,?,?)',
        ('os_sync',json.dumps({'root':str(osroot),'version':status.get('version')},ensure_ascii=False),'OBSERVED',str(osroot),NOW())
    )
    c.commit()
    counts = {t: c.execute('SELECT count(*) FROM nodes WHERE node_type=?', (t,)).fetchone()[0]
              for t in ['CANON','CATEGORY','CONTENT','CHAMBER']}
    edges = c.execute('SELECT count(*) FROM edges').fetchone()[0]
    c.close()
    return {'ok': True, 'counts': counts, 'edges': edges, 'os_version': status.get('version'), 'db': str(db)}

def remember(db, scope, key, value, evidence='REPORTED', provenance='runtime'):
    init_db(db)
    c = conn(db)
    c.execute(
        """INSERT OR REPLACE INTO memories(scope,key,value_json,evidence_status,provenance,updated_at)
           VALUES(?,?,?,?,?,?)""",
        (scope,key,json.dumps(value,ensure_ascii=False),evidence,provenance,NOW())
    )
    c.execute('INSERT INTO events(event_type,payload_json,evidence_status,provenance,ts) VALUES(?,?,?,?,?)',
              ('memory_write',json.dumps({'scope':scope,'key':key},ensure_ascii=False),evidence,provenance,NOW()))
    c.commit(); c.close()
    return {'ok': True, 'scope': scope, 'key': key}

def recall(db, scope=None, key=None):
    c = conn(db)
    q = 'SELECT * FROM memories WHERE 1=1'; params=[]
    if scope:
        q += ' AND scope=?'; params.append(scope)
    if key:
        q += ' AND key=?'; params.append(key)
    q += ' ORDER BY updated_at DESC'
    rows=[]
    for r in c.execute(q, params):
        d=dict(r); d['value']=json.loads(d.pop('value_json')); rows.append(d)
    c.close(); return rows

def search_graph(db, term, limit=12):
    c = conn(db)
    pattern = '%'+term.lower()+'%'
    rows = c.execute(
        """SELECT id,node_type,title,payload_json,evidence_status,canonical,source_ref
           FROM nodes WHERE lower(title) LIKE ? OR lower(payload_json) LIKE ?
           ORDER BY canonical DESC,title LIMIT ?""",
        (pattern, pattern, limit)
    ).fetchall()
    out=[]
    for r in rows:
        d=dict(r); d['payload']=json.loads(d.pop('payload_json')); out.append(d)
    c.close(); return out

def context_packet(db, request, frontier_available=False):
    routes = route(request)
    terms = [w for w in re.findall(r"[\wÀ-ÿ'-]+", request.lower()) if len(w)>=5][:6]
    hits=[]; seen=set(); mem=[]
    if Path(db).exists():
        for term in terms:
            for h in search_graph(db, term, 4):
                if h['id'] not in seen:
                    seen.add(h['id']); hits.append(h)
                if len(hits)>=12: break
            if len(hits)>=12: break
        mem = recall(db)[:8]
    task = 'deep_research' if any(x in request.lower() for x in ['analyse','recherche','comprendre','architecture','audit']) else 'routine_routing'
    return {
        'request': request,
        'routes': routes,
        'model_policy': choose_model(task, frontier_available),
        'knowledge_hits': hits[:12],
        'memory': mem,
        'epistemic_rule': ['OBSERVED','REPORTED','INFERRED','UNKNOWN'],
        'human_gate_required': any(k in request.lower() for k in ['publie','change le canon','déploie','deploie','irréversible','irreversible'])
    }

def stats(db):
    c=conn(db)
    out={
        'nodes': c.execute('SELECT count(*) FROM nodes').fetchone()[0],
        'edges': c.execute('SELECT count(*) FROM edges').fetchone()[0],
        'memories': c.execute('SELECT count(*) FROM memories').fetchone()[0],
        'events': c.execute('SELECT count(*) FROM events').fetchone()[0],
        'by_type': {r[0]:r[1] for r in c.execute('SELECT node_type,count(*) FROM nodes GROUP BY node_type')}
    }
    c.close(); return out

def validate():
    checks=[
        ('manifest_v2', MANIFEST['version']=='2.0.0'),
        ('model_policy_frontier_unverified', MODEL_POLICY['frontier_preferred']['display_name'] is None and MODEL_POLICY['frontier_preferred']['availability']=='UNVERIFIED_UNTIL_RUNTIME_OBSERVED'),
        ('fallback_sol', MODEL_POLICY['primary_fallback']['display_name']=='GPT-5.6 Sol'),
        ('router_governor', ROUTER['fallback']=='GOVERNOR'),
        ('human_gate_canon', 'canonical_change' in GATES['human_gate_required_for']),
        ('no_invented_model_id', MODEL_POLICY['frontier_preferred']['model_id'] is None)
    ]
    return {'ok': all(v for _,v in checks), 'checks':[{'name':n,'ok':v} for n,v in checks]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--db', default=str(DB_DEFAULT))
    sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('validate'); sub.add_parser('init-db'); sub.add_parser('stats')
    s=sub.add_parser('sync-os'); s.add_argument('--root',required=True)
    m=sub.add_parser('model'); m.add_argument('--task',default='deep_research'); m.add_argument('--frontier-available',action='store_true'); m.add_argument('--observed-model')
    r=sub.add_parser('route'); r.add_argument('request')
    c=sub.add_parser('context'); c.add_argument('request'); c.add_argument('--frontier-available',action='store_true')
    rem=sub.add_parser('remember'); rem.add_argument('--scope',required=True); rem.add_argument('--key',required=True); rem.add_argument('--value',required=True); rem.add_argument('--evidence',default='REPORTED')
    rec=sub.add_parser('recall'); rec.add_argument('--scope'); rec.add_argument('--key')
    q=sub.add_parser('search'); q.add_argument('term')
    a=p.parse_args(); db=Path(a.db)
    if a.cmd=='validate': out=validate()
    elif a.cmd=='init-db': out=init_db(db)
    elif a.cmd=='sync-os': out=sync_os(db,a.root)
    elif a.cmd=='stats': out=stats(db)
    elif a.cmd=='model': out=choose_model(a.task,a.frontier_available,a.observed_model)
    elif a.cmd=='route':
        raw=a.request
        try:
            payload=json.loads(raw)
            text=payload.get('request','') if isinstance(payload,dict) else str(payload)
        except Exception:
            text=raw
        lower=text.lower()
        human=any(k in lower for k in ['publie','publication','déploie','deploie','change le canon','modifie le canon','irréversible','irreversible'])
        independent=any(k in lower for k in ['golden','master','release','valide','approuve'])
        out={'route':route(text),'human_gate':human,'status':'HUMAN_GATE' if human else ('PREPARE' if independent else 'ANSWER'),'independent_review_recommended':independent}
    elif a.cmd=='context': out=context_packet(db,a.request,a.frontier_available)
    elif a.cmd=='remember':
        try: value=json.loads(a.value)
        except Exception: value=a.value
        out=remember(db,a.scope,a.key,value,a.evidence)
    elif a.cmd=='recall': out=recall(db,a.scope,a.key)
    else: out=search_graph(db,a.term)
    print(json.dumps(out,indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
