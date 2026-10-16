import unittest
from unittest.mock import patch
from app.factory_episode import read_episode,create_episode
from app.graph import GraphError

class EpisodeMemoryTests(unittest.TestCase):
 def test_missing_episode_returns_none(self):
  with patch('app.factory_episode.query',return_value=[[],[],[]]):
   self.assertIsNone(read_episode('MISSING'))
 def test_corruption_fails_closed(self):
  with patch('app.factory_episode.query',return_value=[[],[['bm90LWpzb24=','1234']],[]]):
   with self.assertRaises(GraphError):read_episode('BROKEN')
 def test_bad_evidence_rejected(self):
  with self.assertRaises(ValueError):create_episode('TEST',evidence='TRUST_ME')
 def test_missing_prior_context_rejected(self):
  with patch('app.factory_episode.investigate',return_value={'sha256':'old','finding':{},'alternatives':[],'recommendation':None}),patch('app.factory_episode.query',return_value=[[],[],[]]),patch('app.factory_episode.read_episode',return_value=None):
   with self.assertRaises(ValueError):create_episode('EP-NEW',prior='EP-MISSING')
