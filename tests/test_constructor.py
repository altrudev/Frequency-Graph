import os
import unittest
from unittest.mock import patch
from app.constructor import verify_candidate,select_recipe,record_result,read_result,RECIPE_ID
from app.graph import GraphError
class ConstructorTests(unittest.TestCase):
 def test_verified_fixed_candidate(self):
  with patch('app.constructor.select_recipe',return_value={'id':RECIPE_ID,'category':'MOCK_FAILOVER','applicability':'SYNTHETIC_IN_MEMORY_ONLY'}):
   result=verify_candidate()
  self.assertTrue(result['passed'],result['test_output'])
  self.assertFalse(result['deployed'])
  self.assertFalse(result['authorized'])
  self.assertEqual(result['test_count'],5)
 def test_absent_recipe_fails_closed(self):
  with patch('app.constructor.query',return_value=[[],[],[]]):
   with self.assertRaises(GraphError): select_recipe()
 def test_persisted_flags_are_not_truthy_strings(self):
  row=[[],[['CANDIDATE-IDENTITY-FAILOVER-001','hash','PASS',5,'SYNTHETIC_IN_MEMORY_ONLY','false','false',RECIPE_ID]],[]]
  with patch('app.constructor.query',return_value=row):
   result=read_result()
  self.assertIs(result['deployed'],False)
  self.assertIs(result['authorized'],False)
