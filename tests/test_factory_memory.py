import unittest
from unittest.mock import patch
from app.factory_memory import canonical_snapshot, record_experiment, replay
from app.graph import GraphError

N=[{'id':'mixer','name':'Mixer'},{'id':'sugar','name':'Sugar'}]
E=[{'from':'sugar','to':'mixer'}]
class FactoryMemoryTests(unittest.TestCase):
    def test_canonical_is_order_independent(self):
        self.assertEqual(canonical_snapshot(N,E,{}),canonical_snapshot(list(reversed(N)),E,{}))
    def test_unknown_edge_rejected(self):
        with self.assertRaises(ValueError):
            canonical_snapshot(N,[{'from':'bad','to':'mixer'}],{})
    def test_duplicate_nodes_rejected(self):
        with self.assertRaises(ValueError):
            canonical_snapshot(N+N,E,{})
    def test_immutable_identity_conflict(self):
        with patch('app.factory.read',return_value={'nodes':N}),patch('app.factory_memory.query',return_value=[[],[['wrongdigest']],[]]):
            with self.assertRaises(GraphError):
                record_experiment('TEST-001',N,E,{})
    def test_corrupted_graph_snapshot_fails_closed(self):
        with patch('app.factory_memory.query',return_value=[[],[['bm90IGpzb24=','deadbeef']],[]]):
            with self.assertRaises(GraphError):
                replay('TEST-001')
