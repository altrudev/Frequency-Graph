import io
import unittest
from unittest.mock import patch
from app.graph import validate_id, _read, impact, GraphError
from app.server import Handler

class GraphTests(unittest.TestCase):
    def test_ids(self):
        self.assertEqual(validate_id("identity"),"identity")
        for value in ("a' RETURN 1","", "../root", "x"*70):
            with self.assertRaises(ValueError): validate_id(value)
    def test_resp(self):
        self.assertEqual(_read(io.BytesIO(b"*2\r\n:5\r\n$3\r\nhey\r\n")),[5,"hey"])
        with self.assertRaises(GraphError): _read(io.BytesIO(b"nonsense\r\n"))
    def test_impact_is_not_authorization(self):
        with patch("app.graph.query",side_effect=[[["id","Identity"]],[["billing","Billing"]]]):
            result=impact("identity")
        self.assertFalse(result["dispatched"])
        self.assertEqual(result["authorization"],"NOT_EVALUATED")
    def test_public_post_disabled(self):
        self.assertTrue(hasattr(Handler,"do_POST"))
        self.assertFalse(hasattr(Handler,"do_DELETE"))

class LiveGraphTests(unittest.TestCase):
    @unittest.skipUnless(__import__("os").getenv("FG_LIVE_TEST"),"Live FalkorDB not requested")
    def test_live(self):
        from app.graph import seed,impact
        seed()
        self.assertTrue(impact("identity")["affected"])

if __name__=="__main__": unittest.main()
