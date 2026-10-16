import unittest
from app.factory_economics import estimate

class EconomicsTests(unittest.TestCase):
    def test_baseline_is_explicit(self):
        r=estimate()
        self.assertEqual(r['materials_g']['sugar'],1500)
        self.assertEqual(r['materials_g']['flavor'],75)
        self.assertEqual(r['bottleneck'],'Cooking')
        self.assertEqual(r['cycles'],1)
        self.assertEqual(r['minutes'],18)
    def test_capacity_increases_cycles(self):
        r=estimate(2000)
        self.assertEqual(r['cycles'],2)
        self.assertEqual(r['minutes'],36)
    def test_intensity_increases_pigment_cost(self):
        self.assertGreater(estimate(intensity=100)['material_cost_units'],estimate(intensity=0)['material_cost_units'])
    def test_invalid_graph_stops_batch(self):
        self.assertIsNone(estimate(valid=False)['minutes'])
    def test_fast_has_warning(self):
        self.assertTrue(any('quality' in x.lower() for x in estimate(speed='fast')['warnings']))
    def test_bounds(self):
        for values in ({'quantity':99},{'quantity':5001},{'intensity':-1},{'speed':'turbo'}):
            with self.subTest(values=values),self.assertRaises(ValueError):
                estimate(**values)
