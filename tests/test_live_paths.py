import unittest
from unittest.mock import patch
from app.counterfactual import investigate_scenario
class LivePathTests(unittest.TestCase):
 def test_path_is_derived_from_graph(self):
  results=[[[],[['identity-outage-001','Outage','identity','Identity']],[]],[[],[['portal','Portal']],[]],[[],[],[]],[[],[],[]]]
  with patch('app.counterfactual.query',side_effect=results),patch('app.counterfactual.snapshot',return_value={'nodes':[{'id':'portal','name':'Portal'},{'id':'identity','name':'Identity'}],'edges':[{'from':'portal','to':'identity'}]}):
   x=investigate_scenario()
  self.assertEqual(x['affected'][0]['path'],['portal','identity'])
