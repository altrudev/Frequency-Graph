"""Fixed-recipe Constructor experiment. No external actions or deployment authority.

Use `python -m app.constructor` on a trusted operator host to generate, test and
record a candidate. Public access can only read the last recorded result.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from .graph import GraphError, _rows, query

RECIPE_ID = 'RECIPE-IDENTITY-FAILOVER-001'
CANDIDATE_ID = 'CANDIDATE-IDENTITY-FAILOVER-001'
RECIPE_CODE = '''"""In-memory identity routing exercise: never makes network requests."""
class IdentityRoute:
    def choose(self, primary_healthy, standby_healthy, standby_verified):
        if primary_healthy:
            return 'primary'
        if standby_healthy and standby_verified:
            return 'standby'
        raise RuntimeError('identity unavailable: fail closed')
'''
# The evaluator is independently specified; no test contents are constructed by
# the recipe, nor are they retrieved from untrusted graph strings.
ACCEPTANCE = '''import unittest
from candidate import IdentityRoute
class Verification(unittest.TestCase):
    def test_primary(self): self.assertEqual(IdentityRoute().choose(True,False,False),'primary')
    def test_verified_standby(self): self.assertEqual(IdentityRoute().choose(False,True,True),'standby')
    def test_unverified_standby_rejected(self):
        with self.assertRaises(RuntimeError): IdentityRoute().choose(False,True,False)
    def test_total_outage_rejected(self):
        with self.assertRaises(RuntimeError): IdentityRoute().choose(False,False,True)
    def test_primary_preferred(self): self.assertEqual(IdentityRoute().choose(True,True,True),'primary')
if __name__=='__main__': unittest.main(verbosity=1)
'''

def select_recipe():
    rows = _rows(query("MATCH (r:ConstructionRecipe {id:'RECIPE-IDENTITY-FAILOVER-001'})-[:APPLIES_TO]->(n:Component {id:'identity'}) RETURN r.id,r.category,r.applicability LIMIT 1"))
    if len(rows) != 1 or rows[0][0] != RECIPE_ID or rows[0][1] != 'MOCK_FAILOVER':
        raise GraphError('No applicable verified recipe registered in FalkorDB')
    return {'id':rows[0][0], 'category':rows[0][1], 'applicability':rows[0][2]}

def seed_recipe():
    query("MERGE (r:ConstructionRecipe {id:'RECIPE-IDENTITY-FAILOVER-001'}) SET r.category='MOCK_FAILOVER',r.applicability='SYNTHETIC_IN_MEMORY_ONLY',r.trust='CANDIDATE_REQUIRES_INDEPENDENT_TEST'",readonly=False)
    query("MATCH (r:ConstructionRecipe {id:'RECIPE-IDENTITY-FAILOVER-001'}),(n:Component {id:'identity'}) MERGE (r)-[:APPLIES_TO]->(n)",readonly=False)

def verify_candidate():
    recipe = select_recipe()  # fail closed if FalkorDB has no recipe
    with TemporaryDirectory(prefix='frequency-candidate-') as folder:
        Path(folder,'candidate.py').write_text(RECIPE_CODE,encoding='utf-8')
        Path(folder,'verify.py').write_text(ACCEPTANCE,encoding='utf-8')
        proc = subprocess.run([sys.executable,'-B','verify.py'],cwd=folder,
            capture_output=True,text=True,timeout=15,env={'PYTHONPATH':'','PYTHONDONTWRITEBYTECODE':'1'})
    digest=hashlib.sha256(RECIPE_CODE.encode()).hexdigest()
    return {'recipe':recipe,'candidate_id':CANDIDATE_ID,'sha256':digest,
            'passed':proc.returncode==0 and 'Ran 5 tests' in proc.stderr and 'OK' in proc.stderr,
            'test_count':5,'test_output':(proc.stdout+'\n'+proc.stderr)[-1200:],
            'scope':'SYNTHETIC_IN_MEMORY_ONLY','deployed':False,'authorized':False}

def record_result(result):
    # Fixed identifiers and allowlisted fields, never arbitrary user-supplied Cypher.
    status='PASS' if result['passed'] else 'FAIL'
    if result['candidate_id'] != CANDIDATE_ID or result['recipe']['id'] != RECIPE_ID:
        raise ValueError('Unexpected construction identifiers')
    if result['sha256'] != hashlib.sha256(RECIPE_CODE.encode()).hexdigest():
        raise ValueError('Candidate digest mismatch')
    query(f"MERGE (c:ConstructionCandidate {{id:'{CANDIDATE_ID}'}}) SET c.sha256='{result['sha256']}',c.status='{status}',c.scope='SYNTHETIC_IN_MEMORY_ONLY',c.deployed=false,c.authorized=false,c.test_count=5",readonly=False)
    query(f"MATCH (c:ConstructionCandidate {{id:'{CANDIDATE_ID}'}}),(r:ConstructionRecipe {{id:'{RECIPE_ID}'}}) MERGE (c)-[:BUILT_FROM]->(r)",readonly=False)
    query(f"MATCH (c:ConstructionCandidate {{id:'{CANDIDATE_ID}'}}),(s:Scenario {{id:'identity-outage-001'}}) MERGE (c)-[:PROPOSED_FOR]->(s)",readonly=False)
    return result

def read_result():
    rows=_rows(query("MATCH (c:ConstructionCandidate {id:'CANDIDATE-IDENTITY-FAILOVER-001'})-[:BUILT_FROM]->(r:ConstructionRecipe) RETURN c.id,c.sha256,c.status,c.test_count,c.scope,c.deployed,c.authorized,r.id LIMIT 1"))
    if not rows:return None
    c,d,status,count,scope,deployed,authorized,r=rows[0]
    def falkor_bool(value):
        if value in (True, 1, 'true', 'True', '1'): return True
        if value in (False, 0, 'false', 'False', '0'): return False
        raise GraphError('Unexpected boolean from FalkorDB')
    return {'candidate_id':c,'recipe_id':r,'sha256':d,'status':status,'test_count':count,
            'scope':scope,'deployed':falkor_bool(deployed),'authorized':falkor_bool(authorized),
            'verification':'INDEPENDENT_FIXED_TESTS_NOT_INTEGRATION_OR_SECURITY_ACCEPTANCE'}

if __name__=='__main__':
    seed_recipe()
    print(json.dumps(record_result(verify_candidate()),indent=2))
