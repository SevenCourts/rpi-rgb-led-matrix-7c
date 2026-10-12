"""The panel says at registration which form factor it is.

The type (M1 192x64, L1 192x96, XL1 320x96) only lived in /opt/7c/panel.conf
on the device, so the server could not know the canvas size of a panel
(led-3t8, for the panel preview hub-0a0p).

Run with: python -m unittest tests.test_registration_panel_type
(or via pytest if installed)
"""

import json
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sevencourts import gateway  # noqa: E402

# The server refuses a registration body above this size.
SERVER_BODY_LIMIT = 1024

# As long as each value gets on a real panel.
_OS_RELEASE = {
    "os_commit_full": "0123456789abcdef0123456789abcdef01234567",
    "buildroot": "2024.02.10-123-g0123456789ab",
    "build_date": "2026-10-12T08:15:30+02:00",
    "rgbmatrix_commit": "0123456789abcdef0123456789abcdef01234567",
}


class RegistrationBodyTest(unittest.TestCase):
    def setUp(self):
        for target, name, value in (
            (gateway.network, "hostname", "10000000deadbeef"),
            (gateway.network, "ip_address", "192.168.178.123"),
            (gateway.network, "vpn_ip_address", "10.8.1.123"),
            (gateway.sys, "os_release", _OS_RELEASE),
        ):
            p = patch.object(target, name, return_value=value)
            p.start()
            self.addCleanup(p.stop)

    def _body(self, panel_type):
        env = {} if panel_type is None else {"PANEL_TYPE": panel_type}
        with patch.dict(os.environ, env):
            if panel_type is None:
                os.environ.pop("PANEL_TYPE", None)
            return gateway._registration_body()

    def test_each_type_is_reported(self):
        for panel_type in ("M1", "L1", "XL1"):
            with self.subTest(panel_type=panel_type):
                self.assertEqual(self._body(panel_type)["panel_type"], panel_type)

    def test_unset_or_unknown_is_m1_as_the_views_draw_it(self):
        for panel_type in (None, "", "XXL9"):
            with self.subTest(panel_type=panel_type):
                self.assertEqual(self._body(panel_type)["panel_type"], "M1")

    def test_the_other_fields_are_still_sent(self):
        body = self._body("L1")
        self.assertEqual(body["code"], "10000000deadbeef")
        self.assertEqual(body["ip"], "192.168.178.123")
        self.assertEqual(body["vpn_ip"], "10.8.1.123")
        self.assertEqual(body["os_version"], _OS_RELEASE["os_commit_full"])

    def test_body_stays_under_the_server_limit(self):
        with patch.object(gateway, "GIT_COMMIT_ID", "f" * 40), patch.object(
            gateway, "GIT_COMMIT_DATE", "2026-10-12"
        ):
            size = len(json.dumps(self._body("XL1")).encode("utf-8"))
        self.assertLess(size, SERVER_BODY_LIMIT)


if __name__ == "__main__":
    unittest.main()
