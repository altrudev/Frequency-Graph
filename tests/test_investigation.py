import unittest
from app.investigation import investigation,simulate_edge_removal
G={'nodes':[{'id':x,'name':x} for x in ['a','b','c','d']], 'edges':[{'from':x,'to':y} for x,y in [('a','b'),('a','c'),('b','d'),('c','d')]]}
class InvestigationTests(unittest.TestCase):
    def test_indirect_path(self):
        report=investigation(G,'d')
        self.assertEqual([p['source'] for p in report['paths']],['b','c','a'])
        self.assertEqual(report['paths'][-1]['depth'],2)
    def test_alternative_path_retained(self):
        s=simulate_edge_removal(G,'a','b')
        self.assertEqual([x['id'] for x in s['lost_reachability']],['b'])
        self.assertEqual(s['after_reachable'],2)
        self.assertFalse(s['mutated'])
    def test_no_database_mutation(self):
        before=repr(G)
        simulate_edge_removal(G,'a','b')
        self.assertEqual(repr(G),before)
    def test_injection_denied(self):
        with self.assertRaises(ValueError):simulate_edge_removal(G,"a' MATCH (n)",'b')
    def test_non_edge_denied(self):self.assertIsNone(simulate_edge_removal(G,'a','d'))
    def test_cycle_bounded(self):
        g={'nodes':[{'id':x,'name':x} for x in ['a','b']],'edges':[{'from':'a','to':'b'},{'from':'b','to':'a'}]}
        self.assertEqual(len(investigation(g,'a')['paths']),1)
if __name__=='__main__':unittest.main()
