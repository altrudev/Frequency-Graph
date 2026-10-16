import unittest
from unittest.mock import patch
from app.counterfactual import investigate_scenario
class TopologyContractTests(unittest.TestCase):
 def test_live_query_preserves_topology_and_path(self):
  rows=[[[],[['identity-outage-001','Outage','identity','Identity']],[]],[[],[['portal','Portal']],[]],[[],[],[]],[[],[],[]]]
  graph={'nodes':[{'id':'portal','name':'Portal','kind':'web'},{'id':'identity','name':'Identity','kind':'service'}],'edges':[{'from':'portal','to':'identity'}]}
  with patch('app.counterfactual.query',side_effect=rows),patch('app.counterfactual.snapshot',return_value=graph):
   result=investigate_scenario()
  self.assertEqual(result['topology'],graph)
  self.assertEqual(result['affected'][0]['path'],['portal','identity'])
  self.assertFalse(result['dispatched'])
