import unittest
from unittest.mock import patch
from app.factory_agent import investigate

GRAPH={'nodes':[{'id':x} for x in ('sugar','strawberry','lemon','pink','yellow','mixer','cooker','molder','coater','pack','out')],
'edges':[{'from':a,'to':b} for a,b in [('sugar','mixer'),('strawberry','mixer'),('pink','mixer'),('mixer','cooker'),('cooker','molder'),('molder','coater'),('coater','pack'),('pack','out')]]}
STAGES=[[],[['cooker',2],['molder',3],['pack',5]],[]]
class AgentTests(unittest.TestCase):
 def run_agent(self,q=5000,stock=10,graph=GRAPH):
  with patch('app.factory_agent.read',return_value=graph),patch('app.factory_agent.query',return_value=STAGES):
   return investigate(q,stock)
 def test_bottleneck_and_unverified_fails_closed(self):
  x=self.run_agent()
  self.assertEqual(x['finding']['bottleneck'],'Cooking')
  self.assertEqual(x['recommendation'],'BASE')
  self.assertFalse(next(v for v in x['alternatives'] if v['id']=='UPGRADE')['eligible'])
  self.assertFalse(x['dispatched'])
 def test_inventory_shortage_rejects_all(self):
  x=self.run_agent(stock=2)
  self.assertIsNone(x['recommendation'])
  self.assertFalse(any(y['eligible'] for y in x['alternatives']))
 def test_deterministic_digest(self):
  self.assertEqual(self.run_agent()['sha256'],self.run_agent()['sha256'])
 def test_broken_graph_rejected(self):
  graph={'nodes':GRAPH['nodes'],'edges':GRAPH['edges'][:-1]}
  with self.assertRaises(ValueError):self.run_agent(graph=graph)
 def test_bounds(self):
  for q,s in [(1,10),(9000,10),(5000,0),(5000,99)]:
   with self.subTest(q=q,s=s),self.assertRaises(ValueError):self.run_agent(q,s)
