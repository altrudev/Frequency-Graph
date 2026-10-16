"""Live FalkorDB acceptance; explicitly skipped unless enabled."""
import os
import unittest
from app.memory import history,seed_revision
from app.counterfactual import investigate_scenario
from app.graph import GraphError

@unittest.skipUnless(os.getenv('FG_LIVE_TEST')=='1','Requires live FalkorDB')
class GraphNativeMemoryAcceptance(unittest.TestCase):
 def test_revision_persistence(self):
  seed_revision('baseline')
  seed_revision('qualification')
  first=history()
  seed_revision('qualification')
  self.assertEqual(first,history())
  self.assertTrue(first['changed'])
  self.assertEqual(len(first['revisions']),2)
  self.assertEqual(investigate_scenario()['memory'][0]['status'],'recorded')
 def test_fail_closed_on_unavailable_database(self):
  port=os.environ.get('FALKORDB_PORT')
  try:
   os.environ['FALKORDB_PORT']='9'
   with self.assertRaises(GraphError):history()
  finally:
   if port is None:os.environ.pop('FALKORDB_PORT',None)
   else:os.environ['FALKORDB_PORT']=port
