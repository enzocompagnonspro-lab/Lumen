import json, subprocess, sys, unittest, tempfile, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BOOT=ROOT/'bootstrap'

class TestPrimeV2(unittest.TestCase):
    def cli(self,db,*args):
        p=subprocess.run([sys.executable,str(ROOT/'runtime/lumen_prime.py'),'--db',str(db),*args],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        return json.loads(p.stdout)
    def fixture_os(self,tmp):
        r=Path(tmp)/'os'
        (r/'config').mkdir(parents=True); (r/'registry').mkdir(); (r/'state').mkdir()
        mapping={
            'config/canon.json':'config__canon.json',
            'registry/knowledge.json':'registry__knowledge.json',
            'registry/journey.json':'registry__journey.json',
            'state/status.json':'state__status.json'
        }
        for rel,src in mapping.items(): shutil.copy2(BOOT/src,r/rel)
        return r
    def test_validate(self):
        db=Path(tempfile.mkdtemp())/'x.db'
        self.assertTrue(self.cli(db,'validate')['ok'])
    def test_model_fallback(self):
        db=Path(tempfile.mkdtemp())/'x.db'
        x=self.cli(db,'model','--task','deep_research')
        self.assertEqual(x['selected_display_name'],'GPT-5.6 Sol')
    def test_model_frontier_requires_observation(self):
        db=Path(tempfile.mkdtemp())/'x.db'
        x=self.cli(db,'model','--task','deep_research','--frontier-available')
        self.assertEqual(x['selected_display_name'],'GPT-5.6 Sol')
        self.assertFalse(x['claim_verified'])
        self.assertFalse(x['frontier_candidate_verified'])
    def test_observed_frontier_can_be_named(self):
        db=Path(tempfile.mkdtemp())/'x.db'
        x=self.cli(db,'model','--task','deep_research','--frontier-available','--observed-model','provider-observed-frontier')
        self.assertEqual(x['selected_display_name'],'provider-observed-frontier')
        self.assertTrue(x['claim_verified'])
        self.assertEqual(x['tier'],'FRONTIER_OBSERVED')
    def test_sync_graph(self):
        tmp=tempfile.mkdtemp(); db=Path(tmp)/'x.db'; osroot=self.fixture_os(tmp)
        x=self.cli(db,'sync-os','--root',str(osroot))
        self.assertTrue(x['ok']); self.assertEqual(x['counts']['CHAMBER'],7); self.assertEqual(x['counts']['CONTENT'],7)
    def test_memory(self):
        tmp=tempfile.mkdtemp(); db=Path(tmp)/'x.db'
        self.cli(db,'init-db')
        self.cli(db,'remember','--scope','user','--key','last_scene','--value','"journey"','--evidence','OBSERVED')
        x=self.cli(db,'recall','--scope','user','--key','last_scene')
        self.assertEqual(x[0]['value'],'journey')
    def test_context(self):
        tmp=tempfile.mkdtemp(); db=Path(tmp)/'x.db'; osroot=self.fixture_os(tmp)
        self.cli(db,'sync-os','--root',str(osroot))
        x=self.cli(db,'context','analyse la chambre Vision et la connaissance')
        self.assertTrue(x['routes']); self.assertIn('model_policy',x)

if __name__=='__main__': unittest.main()
