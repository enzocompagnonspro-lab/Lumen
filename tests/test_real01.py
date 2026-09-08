import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Real01(unittest.TestCase):
 def test_validator(self):
  p=subprocess.run([sys.executable,str(ROOT/'app/validate_real01.py')],capture_output=True,text=True); self.assertEqual(p.returncode,0,p.stdout+p.stderr)
 def test_catalog_truth(self):
  c=json.loads((ROOT/'content/catalog.json').read_text(encoding='utf-8')); sts=[t['status'] for ch in c['chambers'] for t in ch['topics']]; self.assertEqual(sts.count('DRAFT_REVIEWABLE'),3); self.assertEqual(sts.count('TO_PRODUCE'),25)
 def test_historical_gate_untouched(self):
  s=json.loads((ROOT/'state/status.json').read_text(encoding='utf-8')); self.assertNotEqual(s.get('current_task'),'J-008')
 def test_no_external_write_api(self):
  s=(ROOT/'app/real_server.py').read_text(encoding='utf-8'); self.assertNotIn('do_POST',s); self.assertNotIn('do_PUT',s)
if __name__=='__main__': unittest.main()
