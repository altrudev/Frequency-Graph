import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app.export_snapshot import build_snapshot, export

class ExportTests(unittest.TestCase):
    def test_atomic_repeatable(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'snapshot.json'
            data={'source':{'classification':'SYNTHETIC'}}
            a=export(path,data,'2026-10-15T00:00:00Z')
            b=export(path,data,'2026-10-15T00:00:00Z')
            self.assertEqual(a,b)
            self.assertEqual(json.loads(path.read_text())['sha256'],a)
            self.assertFalse(path.with_name('snapshot.json.tmp').exists())
    def test_dangling_edge_rejected(self):
        graph={'nodes':[{'id':'one'}], 'edges':[{'from':'one','to':'missing'}]}
        with patch('app.export_snapshot.snapshot',return_value=graph):
            with self.assertRaises(ValueError):build_snapshot()
    def test_bad_evidence_rejected(self):
        graph={'nodes':[{'id':'one'}], 'edges':[]}
        with patch('app.export_snapshot.snapshot',return_value=graph),patch('app.export_snapshot.evidence',return_value={'verification':'UNTRUSTED'}):
            with self.assertRaises(ValueError):build_snapshot()
