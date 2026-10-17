"""Every request of the gateway must give up after TIMEOUT_S.

get_raw fetched images with no timeout at all, so an image server that
accepted the connection and then went quiet blocked the draw loop for good
(led-td9). TIMEOUT_S can be set through TABLEAU_TIMEOUT_S: the server-side
renderer runs with a much shorter one than a panel.

Run with: python -m unittest tests.test_gateway_timeout
(or via pytest if installed)
"""

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sevencourts import gateway  # noqa: E402


class GetRawTimeoutTest(unittest.TestCase):
    def test_get_raw_passes_the_timeout(self):
        with patch.object(gateway, "TIMEOUT_S", 2.0), patch.object(
            gateway.requests, "get"
        ) as get:
            raw = gateway.get_raw("http://localhost/images/logo.png")
        get.assert_called_once_with(
            "http://localhost/images/logo.png", stream=True, timeout=2.0
        )
        self.assertIs(raw, get.return_value.raw)

    def test_get_raw_by_path_passes_the_timeout(self):
        with patch.object(gateway.requests, "get") as get:
            gateway.get_raw_by_path("images/logo.png")
        self.assertEqual(get.call_args.kwargs["timeout"], gateway.TIMEOUT_S)


class TimeoutFromEnvTest(unittest.TestCase):
    def test_unset_gives_the_default(self):
        self.assertEqual(gateway._timeout_s(None), 10)

    def test_seconds_are_read_as_a_number(self):
        self.assertEqual(gateway._timeout_s("2"), 2.0)
        self.assertEqual(gateway._timeout_s("0.5"), 0.5)

    def test_unusable_values_give_the_default(self):
        for value in ("", "soon", "0", "-3"):
            with self.subTest(value=value):
                self.assertEqual(gateway._timeout_s(value), 10)


if __name__ == "__main__":
    unittest.main()
