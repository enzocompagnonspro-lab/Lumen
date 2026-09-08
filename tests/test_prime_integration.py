import json, subprocess, sys, unittest, tempfile, shutil, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PRIME=ROOT/'prime'/'runtime'/'lumen_prime.py'
class TestPrimeIntegration(unittest.TestCase):
    def test_prime_exists(self): self.assertTrue(PRIME.exists())
    def test_canon_locked(self):
        c=json.loads((ROOT/'config/canon.json').read_text(encoding='utf-8'))
        self.assertEqual(c['status'],'CANON_LOCKED_T008'); self.assertFalse(c['community_enabled'])
    def test_server_prime_routes(self):
        s=(ROOT/'app/server.py').read_text(encoding='utf-8')
        for x in ['/api/prime/health','/api/prime/stats','/api/prime/search','/api/prime/context','/api/prime/model']: self.assertIn(x,s)
    def test_sync_current_os(self):
        tmp=Path(tempfile.mkdtemp())/'prime.db'
        p=subprocess.run([sys.executable,str(PRIME),'--db',str(tmp),'sync-os','--root',str(ROOT)],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr); x=json.loads(p.stdout); self.assertTrue(x['ok']); self.assertEqual(x['counts']['CHAMBER'],7); self.assertEqual(x['counts']['CONTENT'],7)
    def test_main_status_not_auto_advanced(self):
        s=json.loads((ROOT/'state/status.json').read_text(encoding='utf-8'))
        self.assertEqual(s['current_task'],'J-007')
if __name__=='__main__': unittest.main()
