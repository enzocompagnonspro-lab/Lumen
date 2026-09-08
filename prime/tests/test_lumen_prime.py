import json, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class T(unittest.TestCase):
 def cli(self,*args):
  p=subprocess.run([sys.executable,str(ROOT/'runtime/lumen_prime.py'),*args],capture_output=True,text=True); self.assertEqual(p.returncode,0,p.stderr); return json.loads(p.stdout)
 def test_validate(self): self.assertTrue(self.cli('validate')['ok'])
 def test_visual(self): self.assertIn('VISUAL_GUARDIAN',self.cli('route',json.dumps({'request':'analyse le visuel canonique du sanctuaire'}))['route'])
 def test_source(self): self.assertIn('SOURCE_SCOUT',self.cli('route',json.dumps({'request':'vérifier les sources et preuves'}))['route'])
 def test_gate(self):
  r=self.cli('route',json.dumps({'request':'modifie le canon et publie'})); self.assertTrue(r['human_gate']); self.assertEqual(r['status'],'HUMAN_GATE')
 def test_no_community(self):
  m=json.loads((ROOT/'config/model_manifest.json').read_text(encoding='utf-8')); self.assertTrue(any('community' in x for x in m['forbidden']))
if __name__=='__main__': unittest.main()
