import unittest
from unittest.mock import patch
from app.factory import read,seed
class FactoryTests(unittest.TestCase):
 def test_factory_graph_contract(self):
  rows=[[[],[['sugar','Sugar','ingredient',0],['mixer','Mixing','machine',1]],[]],[[],[['sugar','mixer']],[]]]
  with patch('app.factory.query',side_effect=rows):
   result=read()
  self.assertEqual(result['nodes'][0]['id'],'sugar')
  self.assertEqual(result['edges'],[{'from':'sugar','to':'mixer'}])
  self.assertFalse(result['physical_validation'])
  self.assertEqual(result['persistence'],'GRAPH_READ_ONLY_PUBLIC')
 def test_seed_is_idempotent_merge_only(self):
  with patch('app.factory.query') as q:
   seed()
  self.assertTrue(all('MERGE' in c.args[0] for c in q.call_args_list))
