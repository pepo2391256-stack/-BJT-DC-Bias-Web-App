import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dc_bias import ValidationError, calculate_dc_bias


class ReferenceExampleTest(unittest.TestCase):
    """Worked example from the lab sheet: 12 V, 100k/22k, 2.2k, 1k, beta=100."""

    def setUp(self):
        self.result = calculate_dc_bias(
            vcc=12,
            r1=100,
            r2=22,
            rc=2.2,
            re=1,
            beta=100,
            vbe=0.70,
        )

    def test_thevenin_equivalent(self):
        self.assertAlmostEqual(self.result.vth, 2.164, places=3)
        self.assertAlmostEqual(self.result.rth, 18032.8, places=1)

    def test_base_and_emitter_voltages(self):
        self.assertAlmostEqual(self.result.vb, 1.942, places=3)
        self.assertAlmostEqual(self.result.ve, 1.242, places=3)

    def test_collector_voltage_and_vce(self):
        self.assertAlmostEqual(self.result.vc, 9.294, places=3)
        self.assertAlmostEqual(self.result.vce, 8.052, places=3)

    def test_collector_current_in_milliamps(self):
        self.assertAlmostEqual(self.result.ic * 1000, 1.230, places=3)
        self.assertAlmostEqual(self.result.ie * 1000, 1.242, places=3)

    def test_example_is_forward_active(self):
        self.assertEqual(self.result.region, "active")
        self.assertIsNone(self.result.warning)


class RegionTest(unittest.TestCase):
    def test_cutoff_when_vth_not_above_vbe(self):
        result = calculate_dc_bias(
            vcc=12, r1=100, r2=5, rc=2.2, re=1, beta=100, vbe=0.70
        )
        self.assertEqual(result.region, "cutoff")
        self.assertEqual(result.ic, 0.0)
        self.assertIsNotNone(result.warning)

    def test_saturation_when_vce_is_too_low(self):
        result = calculate_dc_bias(
            vcc=5, r1=10, r2=10, rc=2.2, re=1, beta=100, vbe=0.70
        )
        self.assertEqual(result.region, "saturation")
        self.assertLess(result.vce, 0.3)
        self.assertIsNotNone(result.warning)


class ValidationTest(unittest.TestCase):
    def test_zero_resistance_is_rejected(self):
        with self.assertRaises(ValidationError):
            calculate_dc_bias(
                vcc=12, r1=0, r2=22, rc=2.2, re=1, beta=100, vbe=0.70
            )

    def test_negative_beta_is_rejected(self):
        with self.assertRaises(ValidationError):
            calculate_dc_bias(
                vcc=12, r1=100, r2=22, rc=2.2, re=1, beta=-5, vbe=0.70
            )

    def test_non_numeric_value_is_rejected(self):
        with self.assertRaises(ValidationError):
            calculate_dc_bias(
                vcc="abc", r1=100, r2=22, rc=2.2, re=1, beta=100, vbe=0.70
            )


if __name__ == "__main__":
    unittest.main()
