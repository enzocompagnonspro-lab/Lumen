from __future__ import annotations
import json, mimetypes, os, re
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT=Path(__file__).resolve().parents[1]
PROJECT=(ROOT/'projects'/'golden-journey').resolve()
CONTENT=(ROOT/'content').resolve()

class Handler(BaseHTTPRequestHandler):
    server_version='LUMENREAL/1.7'
    def _json(self,obj,status=200):
        b=json.dumps(obj,ensure_ascii=False).encode('utf-8')
        self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.send_header('Cache-Control','no-store'); self.end_headers()
        if self.command!='HEAD': self.wfile.write(b)
    def _file(self,p:Path):
        try: rp=p.resolve(strict=True)
        except FileNotFoundError: return self.send_error(404)
        if PROJECT not in rp.parents and rp!=PROJECT: return self.send_error(403)
        if not rp.is_file(): return self.send_error(404)
        data=rp.read_bytes(); typ=mimetypes.guess_type(str(rp))[0] or 'application/octet-stream'
        self.send_response(200); self.send_header('Content-Type',typ); self.send_header('Content-Length',str(len(data))); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Cache-Control','no-store'); self.end_headers()
        if self.command!='HEAD': self.wfile.write(data)
    def _api(self,path):
        if path=='/api/real/health': return self._json({'ok':True,'mission':'LUMEN-REAL-01','mode':'READ_ONLY_CONTENT'})
        if path=='/api/real/catalog': return self._json(json.loads((CONTENT/'catalog.json').read_text(encoding='utf-8')))
        if path=='/api/real/sources': return self._json(json.loads((CONTENT/'sources'/'sources.json').read_text(encoding='utf-8')))
        m=re.fullmatch(r'/api/real/lesson/([a-z0-9-]+)',path)
        if m:
            p=CONTENT/'lessons'/(m.group(1)+'.json')
            if not p.exists(): return self._json({'error':'NOT_FOUND'},404)
            return self._json(json.loads(p.read_text(encoding='utf-8')))
        return self._json({'error':'NOT_FOUND'},404)
    def _handle(self):
        parsed=urlparse(self.path); path=unquote(parsed.path)
        if path.startswith('/api/'): return self._api(path)
        if path in ('/','/golden-journey','/golden-journey/'): return self._file(PROJECT/'index.html')
        if path.startswith('/golden-journey/'):
            rel=path[len('/golden-journey/'):]
            if any(x in rel for x in ['..','\\']) or rel.startswith('/'): return self.send_error(403)
            return self._file(PROJECT/rel)
        return self.send_error(404)
    def do_GET(self): self._handle()
    def do_HEAD(self): self._handle()
    def log_message(self,fmt,*args): print('[HTTP]',fmt%args)

def main():
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--host',default='127.0.0.1'); p.add_argument('--port',type=int,default=8765); a=p.parse_args()
    print(f'LUMEN REAL-01 http://{a.host}:{a.port}/golden-journey/')
    ThreadingHTTPServer((a.host,a.port),Handler).serve_forever()
if __name__=='__main__': main()
