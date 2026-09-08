from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, urllib.parse, subprocess, sys, os
ROOT=Path(__file__).resolve().parents[1]
class H(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        p=urllib.parse.urlparse(path).path
        if p=='/': p='/web/index.html'
        return str(ROOT/p.lstrip('/'))
    def do_GET(self):
        p=urllib.parse.urlparse(self.path).path
        if p.startswith('/api/'):
            rel={'/api/status':'state/status.json','/api/assets':'registry/assets.json','/api/scenes':'registry/scenes.json','/api/missions':'registry/missions.json','/api/validation':'evidence/validation-latest.json','/api/knowledge':'registry/knowledge.json'}.get(p)
            if rel:
                f=ROOT/rel
                if f.exists():
                    b=f.read_bytes(); self.send_response(200); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b); return
        return super().do_GET()
if __name__=='__main__':
    port=int(os.environ.get('LUMEN_PORT','8787'))
    print(f'LUMEN OS: http://127.0.0.1:{port}')
    ThreadingHTTPServer(('127.0.0.1',port),H).serve_forever()
