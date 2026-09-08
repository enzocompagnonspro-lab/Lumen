from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, urllib.parse, subprocess, sys, os

ROOT=Path(__file__).resolve().parents[1]
PRIME=ROOT/'prime'/'runtime'/'lumen_prime.py'
PRIME_DB=ROOT/'prime'/'memory'/'lumen_prime.db'

class H(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        p=urllib.parse.urlparse(path).path
        if p=='/': p='/web/index.html'
        return str(ROOT/p.lstrip('/'))

    def _json(self,obj,status=200):
        b=json.dumps(obj,ensure_ascii=False,indent=2).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(b)))
        self.end_headers(); self.wfile.write(b)

    def _prime(self,args):
        if not PRIME.exists():
            return {'ok':False,'error':'PRIME_RUNTIME_MISSING'}
        p=subprocess.run([sys.executable,str(PRIME),'--db',str(PRIME_DB),*args],cwd=ROOT,capture_output=True,text=True)
        if p.returncode!=0:
            return {'ok':False,'error':'PRIME_RUNTIME_FAILED','stderr':p.stderr[-2000:]}
        try: return json.loads(p.stdout)
        except Exception: return {'ok':False,'error':'PRIME_BAD_JSON','stdout':p.stdout[-2000:]}

    def do_GET(self):
        u=urllib.parse.urlparse(self.path); p=u.path; qs=urllib.parse.parse_qs(u.query)
        if p.startswith('/api/'):
            rel={
                '/api/status':'state/status.json','/api/assets':'registry/assets.json',
                '/api/scenes':'registry/scenes.json','/api/missions':'registry/missions.json',
                '/api/validation':'evidence/validation-latest.json','/api/knowledge':'registry/knowledge.json',
                '/api/journey':'registry/journey.json'
            }.get(p)
            if rel:
                f=ROOT/rel
                if f.exists():
                    b=f.read_bytes(); self.send_response(200); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b); return
            if p=='/api/prime/health':
                self._json(self._prime(['validate'])); return
            if p=='/api/prime/stats':
                self._json(self._prime(['stats'])); return
            if p=='/api/prime/search':
                q=(qs.get('q') or [''])[0]
                if not q: self._json({'ok':False,'error':'QUERY_REQUIRED'},400); return
                self._json(self._prime(['search',q])); return
            if p=='/api/prime/context':
                request=(qs.get('request') or [''])[0]
                if not request: self._json({'ok':False,'error':'REQUEST_REQUIRED'},400); return
                args=['context',request]
                if (qs.get('frontier') or ['0'])[0]=='1': args.append('--frontier-available')
                self._json(self._prime(args)); return
            if p=='/api/prime/model':
                task=(qs.get('task') or ['deep_research'])[0]
                args=['model','--task',task]
                if (qs.get('frontier') or ['0'])[0]=='1': args.append('--frontier-available')
                self._json(self._prime(args)); return
        return super().do_GET()

if __name__=='__main__':
    port=int(os.environ.get('LUMEN_PORT','8787'))
    print(f'LUMEN OS PRIME: http://127.0.0.1:{port}')
    ThreadingHTTPServer(('127.0.0.1',port),H).serve_forever()
