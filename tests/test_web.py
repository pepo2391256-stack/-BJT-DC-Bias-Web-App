import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

VALID_FORM = {
    "vcc": "12",
    "r1": "100",
    "r2": "22",
    "rc": "2.2",
    "re": "1",
    "beta": "100",
    "vbe": "0.7",
}


class WebRouteTest(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_get_index_returns_form(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Calculate DC Bias", response.data)

    def test_post_calculate_returns_backend_results(self):
        response = self.client.post("/calculate", data=VALID_FORM)
        self.assertEqual(response.status_code, 200)
        self.assertIn("1.230".encode(), response.data)  # IC in mA
        self.assertIn("9.294".encode(), response.data)  # VC in V

    def test_post_root_also_calculates(self):
        response = self.client.post("/", data=VALID_FORM)
        self.assertEqual(response.status_code, 200)
        self.assertIn("9.294".encode(), response.data)

    def test_invalid_input_returns_error_without_crashing(self):
        bad_form = dict(VALID_FORM, r1="0")
        response = self.client.post("/calculate", data=bad_form)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"R1", response.data)


if __name__ == "__main__":
    unittest.main()
