import unittest
from unittest.mock import patch
from app.counterfactual import investigate_scenario

class CounterfactualTests(unittest.TestCase):
 def test_unknown_scenario_not_invented(self):
  self.assertIsNone(investigate_scenario('unknown'))
 def test_reject_injection(self):
  with self.assertRaises(ValueError): investigate_scenario("x' MATCH (n)")
 def test_graph_derived_and_not_authorized(self):
  responses=[ [[],[['identity-outage-001','Identity service unavailable','identity','Identity Service']],[]],
   [[],[['portal','Customer Portal']],[]],
   [[],[['DEC-IDENTITY-001','Require identity','QUALIFIED_BY','EVD-IDENTITY-002','ADR-003','Synthetic']],[]],
   [[],[['INV-IDENTITY-001','recorded']],[]]]
  with patch('app.counterfactual.query',side_effect=responses) as q:
   report=investigate_scenario()
  self.assertEqual(q.call_count,4)
  self.assertFalse(report['dispatched'])
  self.assertEqual(report['affected'][0]['id'],'portal')
  self.assertEqual(report['memory'][0]['status'],'recorded')
  self.assertEqual(report['evidence'][0]['relation'],'QUALIFIED_BY')
