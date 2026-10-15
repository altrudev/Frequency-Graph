import unittest
from unittest.mock import patch
from app.fixture import RECORDS,EDGES
from app.graph import evidence
class FixtureTests(unittest.TestCase):
    def test_unique_ids(self):
        ids=[r[0] for r in RECORDS];self.assertEqual(len(ids),len(set(ids)))
    def test_no_orphan_edge(self):
        ids={r[0] for r in RECORDS};self.assertTrue(all(a in ids and b in ids for a,b in EDGES))
    def test_evidence_boundary(self):
        with patch('app.graph.query',return_value=[[],[['identity','Identity Service','ADR-001','Synthetic note']],[]]):
            e=evidence('identity')
        self.assertEqual(e['verification'],'FIXTURE_RECORD_ONLY')
    def test_no_unbounded_cypher(self):
        self.assertLessEqual(len(RECORDS),150)
        self.assertLessEqual(len(EDGES),300)
