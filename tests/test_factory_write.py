import os
import unittest
from unittest.mock import patch
from app.factory_write import authorize,create_owned_episode

PAYLOAD={'id':'USER-TEST-001','quantity':1000,'stock':3,'prior':None,'evidence':'UNVERIFIED'}
class OwnerWriteTests(unittest.TestCase):
 def test_disabled_without_strong_key(self):
  with patch.dict(os.environ,{},clear=True):
   self.assertFalse(authorize('abc'))
   with self.assertRaises(PermissionError):create_owned_episode(PAYLOAD,'abc')
 def test_rejects_wrong_token(self):
  with patch.dict(os.environ,{'FG_EPISODE_WRITE_TOKEN':'s'*40}):
   with self.assertRaises(PermissionError):create_owned_episode(PAYLOAD,'x'*40)
 def test_owner_can_create_bounded_episode(self):
  with patch.dict(os.environ,{'FG_EPISODE_WRITE_TOKEN':'s'*40}),patch('app.factory_write.create_episode',return_value={'created':True}) as run:
   self.assertTrue(create_owned_episode(PAYLOAD,'s'*40)['created'])
   run.assert_called_once()
 def test_rejects_unexpected_fields(self):
  with patch.dict(os.environ,{'FG_EPISODE_WRITE_TOKEN':'s'*40}):
   with self.assertRaises(ValueError):create_owned_episode({**PAYLOAD,'cypher':'MATCH (n) DELETE n'},'s'*40)
 def test_boolean_quantity_not_integer(self):
  with patch.dict(os.environ,{'FG_EPISODE_WRITE_TOKEN':'s'*40}):
   with self.assertRaises(ValueError):create_owned_episode({**PAYLOAD,'quantity':True},'s'*40)
