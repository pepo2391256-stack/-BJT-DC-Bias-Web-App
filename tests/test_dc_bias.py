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


class IndependentModelTest(unittest.TestCase):
    """Solve the same circuit with nodal equations instead of the module formulas."""

    def _nodal_solution(self, vcc, r1, r2, rc, re, beta, vbe):
        # Resistances in ohm, voltages in volt.
        k = (beta + 1.0) * re
        ib = ((vcc - vbe) / r1 - vbe / r2) / (1.0 + k / r1 + k / r2)
        vb = vbe + k * ib
        ve = vb - vbe
        ic = beta * ib
        ie = (beta + 1.0) * ib
        vc = vcc - ic * rc
        vce = vc - ve
        return dict(ib=ib, ic=ic, ie=ie, vb=vb, ve=ve, vc=vc, vce=vce)

    def test_nodal_solution_matches_module(self):
        result = calculate_dc_bias(
            vcc=12, r1=100, r2=22, rc=2.2, re=1, beta=100, vbe=0.70
        )
        nodal = self._nodal_solution(
            12.0, 100_000.0, 22_000.0, 2_200.0, 1_000.0, 100.0, 0.70
        )

        self.assertAlmostEqual(result.ib, nodal["ib"], delta=1e-9)
        self.assertAlmostEqual(result.ic, nodal["ic"], delta=1e-9)
        self.assertAlmostEqual(result.ie, nodal["ie"], delta=1e-9)
        self.assertAlmostEqual(result.vb, nodal["vb"], delta=1e-9)
        self.assertAlmostEqual(result.ve, nodal["ve"], delta=1e-9)
        self.assertAlmostEqual(result.vc, nodal["vc"], delta=1e-9)
        self.assertAlmostEqual(result.vce, nodal["vce"], delta=1e-9)

    def test_preview_approximation_ignores_base_loading(self):
        """The illustrative image in the lab sheet sets VB = VTH (no base current)."""
        vcc, r1, r2 = 12.0, 100_000.0, 22_000.0
        vth = vcc * r2 / (r1 + r2)  # 2.164 V, the value used by the preview
        result = calculate_dc_bias(
            vcc=12, r1=100, r2=22, rc=2.2, re=1, beta=100, vbe=0.70
        )

        self.assertAlmostEqual(vth, 2.164, places=3)
        self.assertLess(result.vb, vth)  # base current loads the divider
        self.assertAlmostEqual(result.vb, 1.942, places=3)


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
