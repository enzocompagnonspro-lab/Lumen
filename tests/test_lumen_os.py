import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TestLumenOS(unittest.TestCase):
 def test_canon(self):
  c=json.loads((ROOT/'config/canon.json').read_text(encoding='utf-8'));self.assertEqual(c['name'],'LUMEN');self.assertFalse(c['community_enabled']);self.assertEqual(c['palette']['gold'],'#CFAE6A')
 def test_assets_exist(self):
  a=json.loads((ROOT/'registry/assets.json').read_text(encoding='utf-8'))['assets'];self.assertEqual(len(a),10)
  for x in a:self.assertTrue((ROOT/x['file']).exists())
 def test_living_registry(self):
  k=json.loads((ROOT/'registry/knowledge.json').read_text(encoding='utf-8'));self.assertEqual(len(k['categories']),6);self.assertGreaterEqual(len(k['contents']),7)
 def test_human_gate(self):
  m=json.loads((ROOT/'registry/missions.json').read_text(encoding='utf-8'))['missions'][0];t={x['id']:x for x in m['tasks']};self.assertEqual(t['T-008']['status'],'DONE');self.assertEqual(t['T-008']['decision'],'APPROVED')
 def test_cli_validation(self):
  q=subprocess.run([sys.executable,str(ROOT/'app/lumen_os.py'),'validate'],cwd=ROOT,capture_output=True,text=True);self.assertEqual(q.returncode,0);self.assertTrue(json.loads(q.stdout)['ok'])
 def test_journey_registry(self):
  j=json.loads((ROOT/'registry/journey.json').read_text(encoding='utf-8'));self.assertEqual(len(j['chambers']),7);self.assertEqual(j['chambers'][0]['id'],'vision')
 def test_journey_scene_markers(self):
  h=(ROOT/'projects/golden-sanctuary/index.html').read_text(encoding='utf-8');self.assertIn('scene-journey',h);self.assertGreaterEqual(h.count('data-chamber='),7);self.assertIn('e2e-verify',h)
if __name__=='__main__':unittest.main()
