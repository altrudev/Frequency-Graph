import unittest
from unittest.mock import patch
from app.factory_context import context_for, investigate_with_memory
from app.graph import GraphError

class ContextTests(unittest.TestCase):
 def test_no_memory_no_false_recall(self):
  with patch('app.factory_context.query',return_value=[[],[],[]]):
   self.assertEqual(context_for(5000,10),[])
 def test_missing_episode_fails_closed(self):
  with patch('app.factory_context.query',return_value=[[],[['EP-1','UNVERIFIED','BASE']],[]]),patch('app.factory_context.read_episode',return_value=None):
   with self.assertRaises(GraphError):context_for(5000,10)
 def test_recalls_related_episode_and_provenance(self):
  old={'request':{'quantity':5000,'stock_kg':10},'sha256':'a'*64}
  current={'alternatives':[],'recommendation':'BASE'}
  with patch('app.factory_context.query',return_value=[[],[['EP-1','EQUIPMENT_CERTIFIED','UPGRADE_SIMULATION_ONLY']],[]]),patch('app.factory_context.read_episode',return_value=old),patch('app.factory_context.investigate',return_value=current):
   result=investigate_with_memory(5000,10)
  self.assertEqual(len(result['retrieved_episodes']),1)
  self.assertFalse(result['memory_changed_outcome'])
  self.assertEqual(result['provenance'][0]['episode'],'EP-1')
  self.assertIn('physical validation',result['memory_observation'])
 def test_different_batch_does_not_recall(self):
  old={'request':{'quantity':1200,'stock_kg':10},'sha256':'a'*64}
  with patch('app.factory_context.query',return_value=[[],[['EP-1','UNVERIFIED','BASE']],[]]),patch('app.factory_context.read_episode',return_value=old):
   self.assertEqual(context_for(5000,10),[])
