import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dc_bias import (
    ValidationError,
    calculate,
    calculate_emitter_bias,
    calculate_fixed_bias,
)

COMMON = {"vcc": 12, "rc": 2.2, "beta": 100, "vbe": 0.70}


class FixedBiasTest(unittest.TestCase):
    """A2: RB = 1 MOhm, emitter grounded."""

    def setUp(self):
        self.result = calculate_fixed_bias(rb=1000, **COMMON)

    def test_collector_current(self):
        self.assertAlmostEqual(self.result.ic * 1000, 1.130, places=3)

    def test_emitter_is_at_ground(self):
        self.assertAlmostEqual(self.result.ve, 0.0, places=6)
        self.assertAlmostEqual(self.result.vb, 0.700, places=3)

    def test_vce_equals_vc(self):
        self.assertAlmostEqual(self.result.vc, 9.514, places=3)
        self.assertAlmostEqual(self.result.vce, 9.514, places=3)

    def test_mode_and_region(self):
        self.assertEqual(self.result.mode, "fixed")
        self.assertEqual(self.result.region, "active")
        self.assertIsNone(self.result.vth)
        self.assertIsNone(self.result.rth)


class EmitterBiasTest(unittest.TestCase):
    """A3 / A4: RB = 1 MOhm with RE = 1 kOhm and 2 kOhm."""

    def test_re_one_kilo_ohm(self):
        result = calculate_emitter_bias(rb=1000, re=1, **COMMON)
        self.assertAlmostEqual(result.ic * 1000, 1.026, places=3)
        self.assertAlmostEqual(result.ve, 1.037, places=3)
        self.assertAlmostEqual(result.vce, 8.705, places=3)

    def test_larger_re_lowers_collector_current(self):
        small = calculate_emitter_bias(rb=1000, re=1, **COMMON)
        large = calculate_emitter_bias(rb=1000, re=2, **COMMON)
        self.assertAlmostEqual(large.ic * 1000, 0.940, places=3)
        self.assertAlmostEqual(large.vce, 8.033, places=3)
        self.assertLess(large.ic, small.ic)


class DispatchTest(unittest.TestCase):
    def test_dispatch_selects_the_requested_mode(self):
        fixed = calculate("fixed", rb=1000, **COMMON)
        emitter = calculate("emitter", rb=1000, re=1, **COMMON)
        self.assertEqual(fixed.mode, "fixed")
        self.assertEqual(emitter.mode, "emitter")
        # The emitter resistor reduces the base current, so IC is smaller.
        self.assertGreater(fixed.ic, emitter.ic)

    def test_unknown_mode_is_rejected(self):
        with self.assertRaises(ValidationError):
            calculate("class-a", rb=1000, **COMMON)

    def test_zero_rb_is_rejected(self):
        with self.assertRaises(ValidationError):
            calculate_fixed_bias(rb=0, **COMMON)


if __name__ == "__main__":
    unittest.main()
