import unittest
from candidate import IdentityRoute
class Verification(unittest.TestCase):
    def test_primary(self): self.assertEqual(IdentityRoute().choose(True,False,False),'primary')
    def test_verified_standby(self): self.assertEqual(IdentityRoute().choose(False,True,True),'standby')
    def test_unverified_standby_rejected(self):
        with self.assertRaises(RuntimeError): IdentityRoute().choose(False,True,False)
    def test_total_outage_rejected(self):
        with self.assertRaises(RuntimeError): IdentityRoute().choose(False,False,True)
    def test_primary_preferred(self): self.assertEqual(IdentityRoute().choose(True,True,True),'primary')
if __name__=='__main__': unittest.main(verbosity=1)
