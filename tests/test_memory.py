import unittest
from unittest.mock import patch
from app.memory import history, seed_revision
class MemoryTests(unittest.TestCase):
 def test_qualified_revision_changes_status(self):
  raw=[[],[['REV-IDENTITY-BASELINE','old','BASELINE'],['REV-IDENTITY-QUALIFIED','new','QUALIFICATION']],[]]
  with patch('app.memory.query',return_value=raw) as call:
   result=history()
  self.assertTrue(result['changed'])
  self.assertEqual(len(result['revisions']),2)
  self.assertFalse(result['dispatched'])
  self.assertIn('REVIEWED_REVISION',call.call_args.args[0])
 def test_unrecognized_revision_cannot_write(self):
  with self.assertRaises(ValueError): seed_revision('DROP GRAPH')
 def test_reject_invalid_id(self):
  with self.assertRaises(ValueError): history("x' MATCH (n)")
